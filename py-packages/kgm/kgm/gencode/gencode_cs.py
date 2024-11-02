#import ipdb
from ..rdf_utils import xsd_dflt_cs_values, restore_prefix
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update

class UserClass:
    def __init__(self):
        self.name = None

def get_cs_dflt_value(is_class, m_type_curie, cs_type, min_card):
    ret = None
    #ipdb.set_trace()
    if min_card == 0:
        if is_class.literal:
            ret = "null"
        else:
            ret = "null"
    elif min_card == 1:
        #print("WOW:", is_class, is_class.literal)
        if is_class.literal:
            ret = f"new {cs_type}()"
        else:
            ret = xsd_dflt_cs_values[restore_prefix(m_type_curie)]
    else:
        raise Execute("can't get dflt value for card >1")

    return ret
    
def gencode_cs(w_config, uc_curie):
    print("gencode_cs")
    kgm_path = "/CloudDoors.shacl"
    
    rq = make_rq("""
    select ?uc ?uc_m ?uc_m_minc ?uc_m_maxc ?uc_m_is_class ?uc_m_type {
     ?g kgm:path "{{kgm_path}}".
     graph ?g {
      bind({{uc_curie}} as ?uc)
      ?uc sh:property ?uc_p .
      ?uc_p sh:minCount ?uc_m_minc; sh:maxCount ?uc_m_maxc .
      { optional { ?uc_p sh:path ?uc_m; sh:datatype ?uc_m_type bind(false as ?uc_m_is_class) } }
        union { optional { ?uc_p sh:path ?uc_m; sh:class ?uc_m_type bind(true as ?uc_m_is_class)} }
      }
    }
    """.replace("{{kgm_path}}", kgm_path).replace("{{uc_curie}}", uc_curie))
    
    print(rq)
    rq_res = rq_select(rq, config = w_config)
    #ipdb.set_trace()
    print(rq_res)

    uc = UserClass()
    uc.name = f"CD_{uc_curie.split(':')[1]}"
    uc.uriref_class = "URIRef_" + uc.name
    uc.user_class_uri = uc_curie
    
    member_decls = []
    default_assignments = []
    uriref_member_getseters = []
    user_class_info_member_entries = []
    for ii, r in rq_res.iterrows():
        cs_m_name = r['uc_m'].get_suffix()
        cs_m_min_card = r['uc_m_minc']
        if cs_m_min_card == 0:
            cs_m_type = r['uc_m_type'].get_suffix() + "?"
            cs_m_getsetter = f"    public {cs_m_type} {cs_m_name} {{ get {{ return ref_.{cs_m_name}__; }} set {{ ref_.{cs_m_name}__ = value; }} }}"
        elif cs_m_min_card == 1:
            cs_m_type = r['uc_m_type'].get_suffix()
            cs_m_getsetter = f"    public {cs_m_type} {cs_m_name} {{ get {{ return ref_.{cs_m_name}__; }} set {{ Debug.Assert(ref_.{cs_m_name}__); ref_.{cs_m_name}__ = value; }} }}"
        else:
            raise Exception("not supported minc > 1")

        uc_member_info_initializer = []
        uc_m = r['uc_m'].curie
        uc_member_info_initializer.append(f"RDFUtils.restore_prefix(new CURIE(\"{uc_m}\"))")
        uc_member_info_initializer.append(f"{r['uc_m_minc']}")
        uc_member_info_initializer.append(f"{r['uc_m_maxc']}")
        uc_member_info_initializer.append("xsd.class_" if r['uc_m_is_class'].literal == True else "xsd.datatype")
        uc_member_info_initializer.append('new URI("' + restore_prefix(r['uc_m_type']).uri + '")')
        uc_member_info_initializer.append(f"typeof({uc.name}).GetField(\"{cs_m_name}__\")")
        if r['uc_m_is_class'].literal == True:
            uc_member_info_initializer.append(f"() => new {uc.uriref_class}(null, new {uc_m}()))")
        else:
            uc_member_info_initializer.append("null")
        
        #ipdb.set_trace()
        cs_m_dflt_value = get_cs_dflt_value(r['uc_m_is_class'], r['uc_m_type'], r['uc_m'].get_suffix(), cs_m_min_card)
        
        member_decls.append(f"  public {cs_m_type} {cs_m_name}__;")
        default_assignments.append(f"  {cs_m_name}__ = {cs_m_dflt_value};")
        uriref_member_getseters.append(cs_m_getsetter)
        user_class_info_member_entries.append(f"{{ \"{cs_m_name}\", new uc_member_info({','.join(uc_member_info_initializer)}) }}")
        
    
    print("""
    // generated code
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Threading.Tasks;
    using kgm;
    
    public class {{uc.name}} {
      public static URI uo_class_uri = RDFUtils.restore_prefix("{{uc.user_class_uri}}");

      {{member_decls}}

      public {{uc.name}}() {
         {{default_ctor_assignments}}
      }

      public static Dictionary<string, uc_member_info> user_class_info = new Dictionary<string, uc_member_info>{
       {{user_class_info_member_entries}}
      }

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
            uri = RDFUtils.create_uo_uri({{uc.name}}.uo_class_uri);
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
          .replace("{{uc.user_class_uri}}", uc.user_class_uri)
          .replace("{{member_decls}}", "\n".join(member_decls))
          .replace("{{default_ctor_assignments}}", "\n".join(default_assignments))
          .replace("{{uriref_member_getseters}}", "\n".join(uriref_member_getseters))
          .replace("{{user_class_info_member_entries}}", ",\n".join(user_class_info_member_entries))
          )
