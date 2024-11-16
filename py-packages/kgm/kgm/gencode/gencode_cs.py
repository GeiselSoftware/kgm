#import ipdb
import pandas as pd
from ..rdf_utils import xsd_dflt_cs_values, restore_prefix__, collapse_prefix__, xsd, URI, Literal
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update

class UserClass:
    def __init__(self):
        self.name = None

def get_cs_type(uc_m_type_uri):
    #ipdb.set_trace()
    if uc_m_type_uri.get_prefix() == xsd.prefix__:
        xsd_type_uri = uc_m_type_uri
        if xsd_type_uri == xsd.string:
            ret = "string"
        elif xsd_type_uri == xsd.integer:
            ret = "int"
        elif xsd_type_uri == xsd.boolean:
            ret = "bool"
        else:
            raise Exception(f"not supported xsd type {xsd_type_uri}")
    else:
        ret = "URIRef_CD_" + uc_m_type_uri.get_suffix()
        
    return ret    

def get_cs_dflt_value(is_class_arg_l, m_type_uri, min_card_l):
    #ipdb.set_trace()
    is_class = is_class_arg_l == Literal.from_python(True)
    cs_type = get_cs_type(m_type_uri)
    ret = None
    #ipdb.set_trace()
    if min_card_l == Literal.from_python(0):
        if is_class:
            ret = "null"
        else:
            ret = "null"
    elif min_card_l == Literal.from_python(1):
        #print("WOW:", is_class, is_class.literal)
        if is_class:
            ret = "null"
        else:
            ret = xsd_dflt_cs_values[m_type_uri]
    else:
        raise Execute("can't get dflt value for card >1")

    return ret
    
def gencode_cs(w_config, uc_uri_s):
    #ipdb.set_trace()
    uc_uri = URI(uc_uri_s)
    #print("gencode_cs")
    kgm_path = "/CloudDoors.shacl"
    
    rq = make_rq("""
    select ?uc ?uc_m ?uc_m_minc ?uc_m_maxc ?uc_m_is_class ?uc_m_type {
     ?g kgm:path "{{kgm_path}}".
     graph ?g {
      bind({{uc_uri.as_turtle()}} as ?uc)
      ?uc sh:property ?uc_p .
      ?uc_p sh:minCount ?uc_m_minc; sh:maxCount ?uc_m_maxc .
      { optional { ?uc_p sh:path ?uc_m; sh:datatype ?uc_m_type bind(false as ?uc_m_is_class) } }
        union { optional { ?uc_p sh:path ?uc_m; sh:class ?uc_m_type bind(true as ?uc_m_is_class)} }
      }
    }
    """.replace("{{kgm_path}}", kgm_path)
                 .replace("{{uc_uri.as_turtle()}}", uc_uri.as_turtle())
    )
    #print(rq)
    rq_res = pd.DataFrame(rq_select(rq, config = w_config))
    #ipdb.set_trace()
    #print(rq_res)

    uc = UserClass()
    uc.name = f"CD_{uc_uri.get_suffix()}"
    uc.uriref_class = "URIRef_" + uc.name
    uc.user_class_uri = uc_uri
    
    member_decls = []
    default_ctor_assignments = []
    uriref_member_getseters = []
    user_class_info_member_entries = []
    #ipdb.set_trace()
    for ii, r in rq_res.iterrows():
        cs_m_name = r['uc_m'].get_suffix()
        cs_m_type = get_cs_type(r['uc_m_type'])
        cs_m_min_card = r['uc_m_minc']
        if cs_m_min_card == Literal.from_python(0):
            member_decls.append(f"  public {cs_m_type}? {cs_m_name}__;")
            cs_m_getsetter = f"    public {cs_m_type}? {cs_m_name} {{ get {{ return ref_.{cs_m_name}__; }} set {{ ref_.{cs_m_name}__ = value; }} }}"
        elif cs_m_min_card == Literal.from_python(1):
            member_decls.append(f"  public {cs_m_type} {cs_m_name}__;")
            cs_m_getsetter = f"    public {cs_m_type} {cs_m_name} {{ get {{ return ref_.{cs_m_name}__; }} set {{ Debug.Assert(ref_.{cs_m_name}__ != null); ref_.{cs_m_name}__ = value; }} }}"
        else:
            raise Exception("not supported minc > 1")

        uc_member_info_initializer = []
        uc_m = r['uc_m'].as_turtle()
        uc_m_type = r['uc_m_type'].as_turtle()
        uc_member_info_initializer.append(f"Turtle.make_uri(\"{uc_m}\")")
        uc_member_info_initializer.append(f"{r['uc_m_minc']}")
        uc_member_info_initializer.append(f"{r['uc_m_maxc']}")
        uc_member_info_initializer.append("sh.class_" if r['uc_m_is_class'] == Literal.from_python(True) else "sh.datatype")
        uc_member_info_initializer.append(f"Turtle.make_uri(\"{uc_m_type}\")")
        uc_member_info_initializer.append(f"typeof({uc.name}).GetField(\"{cs_m_name}__\")")
        if r['uc_m_is_class'] == Literal.from_python(True):
            uc_member_info_initializer.append(f"() => {cs_m_type}.create(null)")
        else:
            uc_member_info_initializer.append("null")
        
        #ipdb.set_trace()
        cs_m_dflt_value = get_cs_dflt_value(r['uc_m_is_class'], r['uc_m_type'], cs_m_min_card)
        
        default_ctor_assignments.append(f"  {cs_m_name}__ = {cs_m_dflt_value};")
        uriref_member_getseters.append(cs_m_getsetter)
        user_class_info_member_entries.append(f"{{ \"{cs_m_name}\", new uc_member_info({','.join(uc_member_info_initializer)}) }}")
        
    
    print("""
    // generated code - DO NOT EDIT
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Threading.Tasks;
    using kgm;
    
    public class {{uc.name}} {
      public static URI uo_class_uri = Turtle.make_uri("{{uc.user_class_uri}}");

      {{member_decls}}

      public {{uc.name}}() {
         {{default_ctor_assignments}}
      }

      public static Dictionary<string, uc_member_info> user_class_info = new Dictionary<string, uc_member_info>{
       {{user_class_info_member_entries}}
      };

    }

    public class {{uc.uriref_class}} : URIRef {
      [DebuggerBrowsable(DebuggerBrowsableState.Never)]
      {{uc.name}} ref_;
      public {{uc.uriref_class}}(URI uri, {{uc.name}} ref_) { this.uri = uri; this.ref_ = ref_; }

      {{uriref_member_getseters}}

      // public interface

      public override object get_ref() { return this.ref_ as object; }
      public override Dictionary<string, uc_member_info> get_user_class_info() { return {{uc.name}}.user_class_info; }
      public override URI get_uo_class_uri() { return {{uc.name}}.uo_class_uri; }

      public static {{uc.uriref_class}} create(URI? uri)
      {
        if (uri == null) {
            uri = URI.new_uo_uri({{uc.name}}.uo_class_uri);
        }
        {{uc.name}} new_uo_ref = new {{uc.name}}();
        return new {{uc.uriref_class}}(uri, new_uo_ref);
      }

      public static async Task<{{uc.uriref_class}}> load(GraphDB gdb, URI uo_uri) {
        {{uc.uriref_class}} ret = {{uc.uriref_class}}.create(uo_uri);
        await gdb.load(ret);
        return ret;
      }

      public async Task save(GraphDB gdb) {
        await gdb.save(this);
      }
    }

    """.replace("{{uc.uriref_class}}", uc.uriref_class)
          .replace("{{uc.name}}", uc.name)
          .replace("{{uc.user_class_uri}}", uc.user_class_uri.as_turtle())
          .replace("{{member_decls}}", "\n".join(member_decls))
          .replace("{{default_ctor_assignments}}", "\n".join(default_ctor_assignments))
          .replace("{{uriref_member_getseters}}", "\n".join(uriref_member_getseters))
          .replace("{{user_class_info_member_entries}}", ",\n".join(user_class_info_member_entries))
          )
