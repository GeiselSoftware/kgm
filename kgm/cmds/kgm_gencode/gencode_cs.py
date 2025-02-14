#import ipdb
import sys, os
from enum import Enum
import pandas as pd
from kgm.rdf_utils import xsd_dflt_cs_values, xsd, URI, Literal
from kgm.database import Database

class UserClass:
    def __init__(self, uc_uri, cs_namespace):
        self.cs_namespace = cs_namespace
        self.name = f"{uc_uri.get_suffix()}"
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
    min_c = from_Literal_to_python(min_c)
    max_c = from_Literal_to_python(max_c) if max_c is not None else max_c
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

def get_cs_dflt_value(cs_m_type:str):
    ret = None
    if cs_m_type == "string":
        ret = '""'
    elif cs_m_type == "int":
        ret = "0"
    elif cs_m_type == "float":
        ret = "0.0f"
    elif cs_m_type == "double":
        ret = "0.0"
    else:
        raise Exception(f"unsupported CS type {cs_m_type}")
    return ret
    
def gencode_cs_class(db, kgm_path, uc_uri_s, cs_namespace):    
    #ipdb.set_trace()
    uc_uri = URI(uc_uri_s)
    #print("gencode_cs")
    
    rq = """
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
    """.replace("{{kgm_path}}", kgm_path).replace("{{uc_uri.as_turtle()}}", uc_uri.as_turtle())
    
    #print(rq)
    rq_res = pd.DataFrame(db.rq_select(rq))
    #ipdb.set_trace()
    #print(rq_res)

    uc = UserClass(uc_uri, cs_namespace)
    
    uc_member_decls = []
    uo_members_setup = []
    uo_members_assignment = []
    uo_member_getseters = []
    user_class_info_member_entries = []
    uo_create_func_args = ["GraphDB db"] # first arg of T::create

    for ii, r in rq_res.iterrows():
        m_cardinality = classify_minc_maxc(r['uc_m_minc'], r['uc_m_maxc'])
        if m_cardinality is None:
            raise Exception("failed to resolve cardinality")

        #ipdb.set_trace()
        m_uri = r['uc_m']
        cs_m_name = r['uc_m'].get_suffix()
        cs_m_type, cs_m_is_literal = get_cs_type(r['uc_m_type'])
        if m_cardinality == member_cardinalty_t.ZERO_ONE:
            if cs_m_is_literal and cs_m_type != "string":
                uc_member_decls.append(f"public UOStructScalar<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public {cs_m_type}? {cs_m_name} {{ get {{ return this.{cs_m_name}__.Get(); }} set {{ this.{cs_m_name}__.Set(value); }} }}"
                create_func = "null"
                uo_members_setup.append(f'this.{cs_m_name}__ = new UOStructScalar<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func});')
            else:
                uc_member_decls.append(f"public UOClassScalar<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public {cs_m_type}? {cs_m_name} {{ get {{ return this.{cs_m_name}__.Get(); }} set {{ this.{cs_m_name}__.Set(value); }} }}"
                create_func = f"{cs_m_type}.create_empty" if cs_m_type != "string" else "null"
                uo_members_setup.append(f'this.{cs_m_name}__ = new UOClassScalar<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func});')
        elif m_cardinality == member_cardinalty_t.ONE_ONE:
            if cs_m_is_literal and cs_m_type != "string":
                uc_member_decls.append(f"public UOStructScalar<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public {cs_m_type} {cs_m_name} {{ get {{ return this.{cs_m_name}__.GetNN(); }} set {{ this.{cs_m_name}__.Set(value); }} }}"
                dflt_v = get_cs_dflt_value(cs_m_type); create_func = "null"
                uo_members_setup.append(f'this.{cs_m_name}__ = new UOStructScalar<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func}); this.{cs_m_name}__.SetInitialValue({dflt_v});')
            else:
                uc_member_decls.append(f"public UOClassScalar<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public {cs_m_type} {cs_m_name} {{ get {{ return this.{cs_m_name}__.Get(); }} set {{ this.{cs_m_name}__.Set(value); }} }}"
                create_func = f"{cs_m_type}.create_empty" if cs_m_type != "string" else "null"
                m_setup = f'this.{cs_m_name}__ = new UOClassScalar<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func});'
                if cs_m_type == "string":
                    dflt_v = get_cs_dflt_value(cs_m_type)
                    m_setup += f" this.{cs_m_name}__.SetInitialValue({dflt_v});"
                uo_members_setup.append(m_setup)            
        elif m_cardinality == member_cardinalty_t.MANY:
            if cs_m_is_literal and cs_m_type != "string":
                uc_member_decls.append(f"public UOStructSet<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public UOStructSet<{cs_m_type}> {cs_m_name} {{ get {{ return this.{cs_m_name}__; }} }}"
                create_func = "null"
                uo_members_setup.append(f'this.{cs_m_name}__ = new UOStructSet<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func});')
            else:
                uc_member_decls.append(f"public UOClassSet<{cs_m_type}> {cs_m_name}__;")
                cs_m_getsetter = f"public UOClassSet<{cs_m_type}> {cs_m_name} {{ get {{ return this.{cs_m_name}__; }} }}"                
                if cs_m_type != "string":
                    create_func = f"{cs_m_type}.create_empty"
                else:
                    create_func = "null"
                uo_members_setup.append(f'this.{cs_m_name}__ = new UOClassSet<{cs_m_type}>(db, this, URI.create("{m_uri.as_turtle()}"), {create_func});')
        else:
            raise Exception("unknown cardinality")
            
        uc_member_info_initializer = []
        uc_m = r['uc_m'].as_turtle()
        uc_m_type = r['uc_m_type'].as_turtle()
        if m_cardinality == member_cardinalty_t.MANY:
            uc_member_info_class = "uc_member_info"
        else:
            uc_member_info_class = "uc_member_info"
        uc_member_info_initializer.append(f"URI.create(\"{uc_m}\")")
        uc_member_info_initializer.append(f"{r['uc_m_minc']}")
        m_maxc = from_Literal_to_python(r['uc_m_maxc']) if r['uc_m_maxc'] is not None else -1
        uc_member_info_initializer.append(f"{m_maxc}")
        uc_member_info_initializer.append("sh.class_" if r['uc_m_is_class'] == Literal.from_python(True) else "sh.datatype")
        uc_member_info_initializer.append(f"URI.create(\"{uc_m_type}\")")
        uc_member_info_initializer.append(f"typeof({uc.name}).GetField(\"{cs_m_name}__\")")
        
        uo_member_getseters.append(cs_m_getsetter)
        user_class_info_member_entries.append(f"{{ \"{cs_m_name}\", new {uc_member_info_class}({','.join(uc_member_info_initializer)}) }}")

        if cs_m_is_literal == False:
            # only links can be assigned during create
            if m_cardinality == member_cardinalty_t.MANY:
                uo_create_func_args.append(f"HashSet<{cs_m_type}>? {cs_m_name}")
                uo_members_assignment.append(f"if ({cs_m_name} != null) {{ foreach (var el in {cs_m_name}) {{ {cs_m_name}.Add(el); }} }}")
            else:
                uo_create_func_args.append(f"{cs_m_type}? {cs_m_name}")
                uo_members_assignment.append(f"ret.{cs_m_name} = {cs_m_name};")
    
    code = """// generated code - DO NOT EDIT
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Threading.Tasks;
    using kgm;

    namespace {{cs_namespace}} {
      public class {{uc.name}} : UserObject {

        {{uc_member_decls}}

        private {{uc.name}}(GraphDB db) {
          this.__uri = null;
          {{uo_members_setup}}
        }

        private static Dictionary<string, uc_member_info> user_class_info = new Dictionary<string, uc_member_info>{
          {{user_class_info_member_entries}}
        };

        public static URI uo_class_uri = URI.create("{{uc.user_class_uri}}");
        {{uo_member_getseters}}

        // public interface

        public override Dictionary<string, uc_member_info> get_user_class_info() { return user_class_info; }
        public override URI get_uo_class_uri() { return uo_class_uri; }

        public static {{uc.name}} create_empty(GraphDB db)
        {
          {{uc.name}} new_uo = new {{uc.name}}(db);
          return new_uo;
        }

        public static {{uc.name}} create({{uo_create_func_args}})
        {
          var ret = create_empty(db);
          ret.__uri = UserObject.new_uo_uri({{uc.name}}.uo_class_uri);        
          {{uo_members_assignment}};
          db.add_user_object(ret);
          return ret;
        }
      }
    }
    """

    code = code \
    .replace("{{cs_namespace}}", cs_namespace) \
    .replace("{{uc.name}}", uc.name) \
    .replace("{{uc.user_class_uri}}", uc.user_class_uri.as_turtle()) \
    .replace("{{uc_member_decls}}", "\n".join(uc_member_decls)) \
    .replace("{{uo_members_setup}}", "\n".join(uo_members_setup)) \
    .replace("{{uo_members_assignment}}", "\n".join(uo_members_assignment)) \
    .replace("{{uo_member_getseters}}", "\n".join(uo_member_getseters)) \
    .replace("{{user_class_info_member_entries}}", ",\n".join(user_class_info_member_entries)) \
    .replace("{{uo_create_func_args}}", ",\n".join(uo_create_func_args))

    code = "\n".join([x for x in code.split("\n")])
    return code

def gencode_cs_namespace(cs_namespace, user_class_uris):    
    class_factories_code = []
    for user_class_uri in user_class_uris:
        cs_user_class = user_class_uri.get_suffix()
        class_factories_code.append(f"""
        if (rdf_type.Equals(URI.create("{user_class_uri.as_turtle()}"))) {{
         ret = {cs_user_class}.create_empty(db);
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
      public override UserObject create_user_object(GraphDB db, URI rdf_type) {{
       UserObject ret = null;
       {class_factories_code}
       return ret;
      }}
     }}
    }}

    """
    return code
    
def gencode_for_namespace(db:Database, kgm_path, cs_namespace, output_dir):
    if output_dir != "-":
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    rq = """
    select ?uc
    where {
        ?g kgm:path "{{kgm_path}}" .
        graph ?g { ?uc rdf:type rdfs:Class }
    }
    """.replace("{{kgm_path}}", kgm_path)

    rq_res = pd.DataFrame(db.rq_select(rq))
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
        res_code = gencode_cs_class(db, kgm_path, r.uc.as_turtle(), cs_namespace)
        if output_dir != "-":
            out_fn = os.path.join(output_dir, f"{cs_class}.cs")
            print(f"generating {out_fn}")
            with open(out_fn, "w") as out:
                print(res_code, file = out)
        else:
            print(res_code)

            
            
                  
