#import ipdb
import sys, os
from enum import Enum
import pandas as pd
from ..rdf_utils import xsd_dflt_cs_values, restore_prefix__, collapse_prefix__, xsd, URI, Literal
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update

class UserClass:
    def __init__(self, uc_uri, cs_namespace):
        self.cs_namespace = cs_namespace
        self.name = f"{uc_uri.get_suffix()}"
        self.uriref_class = self.name
        self.user_class_uri = uc_uri

def get_cs_type(uc_m_type_uri):
    #ipdb.set_trace()
    is_literal = False
    if uc_m_type_uri.get_prefix() == xsd.prefix__:
        is_literal = True
        xsd_type_uri = uc_m_type_uri
        if xsd_type_uri == xsd.string:
            ret = "string"
        elif xsd_type_uri == xsd.integer:
            ret = "int"
        elif xsd_type_uri == xsd.float:
            ret = "float"
        elif xsd_type_uri == xsd.double:
            ret = "double"
        elif xsd_type_uri == xsd.boolean:
            ret = "bool"
        else:
            raise Exception(f"not supported xsd type {xsd_type_uri}")
    else:
        ret = uc_m_type_uri.get_suffix()
        
    return ret, is_literal

member_cardinalty_t = Enum('member_cardinalty_t', [('ZERO_ONE', 0), ('ONE_ONE', 1), ('MANY', 2)])
def classify_minc_maxc(min_c, max_c) -> member_cardinalty_t:
    ret = None
    min_c = min_c.as_python()
    max_c = max_c.as_python() if max_c is not None else max_c
    if min_c == 0:
        if max_c == 1:
            ret = member_cardinalty_t.ZERO_ONE
        elif max_c is None or max_c > 1:
            ret = member_cardinalty_t.MANY
    elif min_c == 1:
        if max_c == 1:
            ret = member_cardinalty_t.ONE_ONE
        elif max_c is None or max_c > 1:
            ret = member_cardinalty_t.MANY

    #if ret is None:
    #    ipdb.set_trace()
    
    return ret

def get_cs_dflt_value(is_class_arg_l, m_type_uri, cardinality: member_cardinalty_t):
    #ipdb.set_trace()
    is_class = is_class_arg_l.as_python() == True
    cs_type, _ = get_cs_type(m_type_uri)
    ret = None
    #ipdb.set_trace()
    if cardinality == member_cardinalty_t.ZERO_ONE:
        if is_class:
            ret = "null"
        else:
            ret = "null"
    elif cardinality == member_cardinalty_t.ONE_ONE:
        #print("WOW:", is_class, is_class.literal)
        if is_class:
            ret = "null"
        else:
            ret = xsd_dflt_cs_values[m_type_uri]
    else:
        ret = f"new HashSet<{cs_type}>()"

    return ret
    
def gencode_cs_class(w_config, kgm_path, uc_uri_s, cs_namespace):    
    #ipdb.set_trace()
    uc_uri = URI(uc_uri_s)
    #print("gencode_cs")
    
    rq = make_rq("""
    select ?uc ?uc_m ?uc_m_minc ?uc_m_maxc ?uc_m_is_class ?uc_m_type {
      ?g kgm:path "{{kgm_path}}".
      graph ?g {
        bind({{uc_uri.as_turtle()}} as ?uc)
        ?uc sh:property ?uc_p.
        ?uc_p sh:path ?uc_m filter(?uc_m != rdf:type).
        ?uc_p sh:minCount ?uc_m_minc.
        optional { ?uc_p sh:maxCount ?uc_m_maxc }
        { optional { ?uc_p sh:datatype ?uc_m_type bind(false as ?uc_m_is_class) } }
          union { optional { ?uc_p sh:class ?uc_m_type bind(true as ?uc_m_is_class)} }
        }
    }
    """.replace("{{kgm_path}}", kgm_path)
                 .replace("{{uc_uri.as_turtle()}}", uc_uri.as_turtle())
    )
    #print(rq)
    rq_res = pd.DataFrame(rq_select(rq, config = w_config))
    #ipdb.set_trace()
    #print(rq_res)

    uc = UserClass(uc_uri, cs_namespace)
    
    member_decls = []
    default_ctor_assignments = []
    uriref_member_getseters = []
    user_class_info_member_entries = []
    uriref_create_args = ["GraphDB db"] # first arg of T::create
    uriref_create_member_init_statements = []

    for ii, r in rq_res.iterrows():
        m_cardinality = classify_minc_maxc(r['uc_m_minc'], r['uc_m_maxc'])
        if m_cardinality is None:
            raise Exception("failed to resolve cardinality")

        #ipdb.set_trace()
        cs_m_name = r['uc_m'].get_suffix()
        cs_m_type, cs_m_is_literal = get_cs_type(r['uc_m_type'])
        match m_cardinality:
            case member_cardinalty_t.ZERO_ONE:
                member_decls.append(f"public {cs_m_type}? {cs_m_name}__;")
                cs_m_getsetter = f"public {cs_m_type}? {cs_m_name} {{ get {{ return __ref.{cs_m_name}__; }} set {{ __ref.{cs_m_name}__ = value; }} }}"
            case member_cardinalty_t.ONE_ONE:
                if cs_m_is_literal:
                    member_decls.append(f"public {cs_m_type} {cs_m_name}__;")
                    cs_m_getsetter = f"public {cs_m_type} {cs_m_name} {{ get {{ return __ref.{cs_m_name}__; }} set {{ __ref.{cs_m_name}__ = value; }} }}"
                else:
                    member_decls.append(f"public {cs_m_type}? {cs_m_name}__;")
                    cs_m_getsetter = f"public {cs_m_type}? {cs_m_name} {{ get {{ return __ref.{cs_m_name}__; }} set {{ __ref.{cs_m_name}__ = value; }} }}"
            case member_cardinalty_t.MANY:
                #raise Exception("not supported cardinality: ", m_cardinality)
                member_decls.append(f"public HashSet<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"""
                public HashSet<{cs_m_type}> {cs_m_name} {{
                get {{ return __ref.{cs_m_name}__; }}
                }}
                """

        uc_member_info_initializer = []
        uc_m = r['uc_m'].as_turtle()
        uc_m_type = r['uc_m_type'].as_turtle()
        if m_cardinality == member_cardinalty_t.MANY:
            uc_member_info_class = "uc_list_member_info"
            uc_member_adder = f'typeof(HashSet<{cs_m_type}>).GetMethod("Add")'
        else:
            uc_member_info_class = "uc_scalar_member_info"
            uc_member_adder = "null"
        uc_member_info_initializer.append(f"Turtle.make_uri(\"{uc_m}\")")
        uc_member_info_initializer.append(f"{r['uc_m_minc']}")
        m_maxc = r['uc_m_maxc'].as_python() if r['uc_m_maxc'] is not None else -1
        uc_member_info_initializer.append(f"{m_maxc}")
        uc_member_info_initializer.append("sh.class_" if r['uc_m_is_class'] == Literal.from_python(True) else "sh.datatype")
        uc_member_info_initializer.append(f"Turtle.make_uri(\"{uc_m_type}\")")
        uc_member_info_initializer.append(f"typeof({uc.name}_Impl).GetField(\"{cs_m_name}__\")")
        if r['uc_m_is_class'].as_python() == True:
            uc_member_info_initializer.append(f"() => {cs_m_type}.create_empty()")
        else:
            uc_member_info_initializer.append("null")
        uc_member_info_initializer.append(uc_member_adder)
        
        #ipdb.set_trace()
        cs_m_dflt_value = get_cs_dflt_value(r['uc_m_is_class'], r['uc_m_type'], m_cardinality)
        
        default_ctor_assignments.append(f"{cs_m_name}__ = {cs_m_dflt_value};")
        uriref_member_getseters.append(cs_m_getsetter)
        user_class_info_member_entries.append(f"{{ \"{cs_m_name}\", new {uc_member_info_class}({','.join(uc_member_info_initializer)}) }}")

        if cs_m_is_literal == False:
            # only links can be assigned during create
            if m_cardinality == member_cardinalty_t.MANY:
                uriref_create_args.append(f"HashSet<{cs_m_type}>? {cs_m_name}")
                uriref_create_member_init_statements.append(f"if ({cs_m_name} != null) {{ ret.{cs_m_name}.UnionWith({cs_m_name}); }}")
            else:
                uriref_create_args.append(f"{cs_m_type}? {cs_m_name}")
                uriref_create_member_init_statements.append(f"ret.{cs_m_name} = {cs_m_name}")
    
    code = """// generated code - DO NOT EDIT
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Threading.Tasks;
    using kgm;

    namespace {{cs_namespace}} {
      public class {{uc.name}}_Impl {

        {{member_decls}}

        public {{uc.name}}_Impl() {
          {{default_ctor_assignments}}
        }

        public static Dictionary<string, uc_member_info_base> user_class_info = new Dictionary<string, uc_member_info_base>{
          {{user_class_info_member_entries}}
        };
      }

      public class {{uc.uriref_class}} : UserObject {
        [DebuggerBrowsable(DebuggerBrowsableState.Never)]
        private {{uc.name}}_Impl __ref;
        private {{uc.uriref_class}}(URI uri, {{uc.name}}_Impl ref_) { this.__uri = uri; this.__ref = ref_; }

        public static URI uo_class_uri = Turtle.make_uri("{{uc.user_class_uri}}");
        {{uriref_member_getseters}}

        // public interface

        public override object get_ref() { return this.__ref as object; }
        public override Dictionary<string, uc_member_info_base> get_user_class_info() { return {{uc.name}}_Impl.user_class_info; }
        public override URI get_uo_class_uri() { return uo_class_uri; }

        public static {{uc.uriref_class}} create_empty()
        {
          URI new_uri = URI.new_uo_uri({{uc.name}}.uo_class_uri);        
          {{uc.name}}_Impl new_uo_ref = new {{uc.name}}_Impl();
          {{uc.uriref_class}} ret = new {{uc.uriref_class}}(new_uri, new_uo_ref);
          return ret;
        }

        public static {{uc.uriref_class}} create({{uriref_create_args}})
        {
          var ret = create_empty();
          {{uriref_create_member_init_statements}};
          db.add(ret);
          return ret;
        }
      }
    }
    """

    code = code \
    .replace("{{cs_namespace}}", cs_namespace) \
    .replace("{{uc.uriref_class}}", uc.uriref_class) \
    .replace("{{uc.name}}", uc.name) \
    .replace("{{uc.user_class_uri}}", uc.user_class_uri.as_turtle()) \
    .replace("{{member_decls}}", "\n".join(member_decls)) \
    .replace("{{default_ctor_assignments}}", "\n".join(default_ctor_assignments)) \
    .replace("{{uriref_member_getseters}}", "\n".join(uriref_member_getseters)) \
    .replace("{{user_class_info_member_entries}}", ",\n".join(user_class_info_member_entries)) \
    .replace("{{uriref_create_args}}", ",\n".join(uriref_create_args)) \
    .replace("{{uriref_create_member_init_statements}}", ";\n".join(uriref_create_member_init_statements))

    code = "\n".join([x for x in code.split("\n")])
    return code

def gencode_cs_namespace(cs_namespace, user_class_uris):    
    class_factories_code = []
    for user_class_uri in user_class_uris:
        cs_user_class = user_class_uri.get_suffix()
        class_factories_code.append(f"""
        if (rdf_type.Equals(URI.create("{user_class_uri.as_turtle()}"))) {{
         ret = {cs_user_class}.create_empty();
        }}
        """)
    class_factories_code.append("""\
    {
      throw new System.Exception($"unknown rdf_type: {{rdf_type.as_turtle()}}");
    }
    """)
        
    class_factories_code = " else ".join(class_factories_code)
    code = f"""\
    // generated code - DO NOT EDIT

    using kgm;

    namespace {cs_namespace} {{
     public class UserObjectFactory : kgm.UserObjectFactory {{
      public override UserObject create_user_object(URI rdf_type) {{
       UserObject ret = null;
       {class_factories_code}
       return ret;
      }}
     }}
    }}

    """
    return code
    
def gencode_for_namespace(w_config, kgm_path, cs_namespace, output_dir):
    if output_dir != "-":
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    rq = make_rq("""
    select ?uc
    where {
        ?g kgm:path "{{kgm_path}}" .
        graph ?g { ?uc rdf:type rdfs:Class }
    }
    """.replace("{{kgm_path}}", kgm_path))

    rq_res = pd.DataFrame(rq_select(rq, config = w_config))
    #print(rq_res)

    res_code = gencode_cs_namespace(cs_namespace, [r.uc for r in rq_res.itertuples()])
    if output_dir != "-":
        out_fn = os.path.join(output_dir, "ns.cs")
        print(f"generating {out_fn}")
        with open(out_fn, "w") as out:
            print(res_code, file = out)
    else:
        print(res_code)

    for r in rq_res.itertuples():
        #print("UC:", r.uc)
        cs_class = r.uc.get_suffix()
        res_code = gencode_cs_class(w_config, kgm_path, r.uc.as_turtle(), cs_namespace)
        if output_dir != "-":
            out_fn = os.path.join(output_dir, f"{cs_class}.cs")
            print(f"generating {out_fn}")
            with open(out_fn, "w") as out:
                print(res_code, file = out)
        else:
            print(res_code)

            
            
                  
