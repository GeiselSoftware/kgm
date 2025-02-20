import ipdb
import sys, io
from kgm.database import Database
from kgm.kgm_graph import KGMGraph
from kgm.rdf_terms import URI
from kgm.rdf_utils import collapse_prefix, get_py_m_name, restore_prefix
from kgm.prefixes import well_known_prefixes, well_known_prefix_members

datatype_cs_dets = {URI(well_known_prefixes['xsd:'] + xsd_typename):None for xsd_typename in well_known_prefix_members['xsd:']}
datatype_cs_dets[restore_prefix('xsd:string', well_known_prefixes)] = ('string', '""')
datatype_cs_dets[restore_prefix('xsd:boolean', well_known_prefixes)] = ('bool?', 'false')
datatype_cs_dets[restore_prefix('xsd:integer', well_known_prefixes)] = ('int?', '0')
datatype_cs_dets[restore_prefix('xsd:float', well_known_prefixes)] = ('float?', '0.0f')
datatype_cs_dets[restore_prefix('xsd:double', well_known_prefixes)] = ('double?', '0.0')

def gen_Factory_create_method(out, g:KGMGraph, uc:"UserClass"):
    #ipdb.set_trace()
    uc_name = get_py_m_name(uc.uc_uri)
    args = ""
    uc_curie = collapse_prefix(uc.uc_uri, g.db.w_prefixes)

    print(f"  public {uc_name} create_{uc_name}({args}) {{", file = out)
    print(f'     UserObject uo = this.g.create_user_object("{uc_curie}");', file = out)
    print(f"     {uc_name} ret = new {uc_name}(uo);", file = out)
    print(f"     {uc_name}.set_default_values(uo);", file = out)
    print(f"     return ret;", file = out)
    print(f"  }}", file = out)
    print("", file = out)
    print(f"  public bool is_{uc_name}(CSUserObject cs_uo) {{", file = out)
    print(f'     return cs_uo.uo.is_class_or_superclass("{uc_curie}");', file = out)
    print(f"  }}", file = out)
    print("", file = out)
    print(f"  public {uc_name} as_{uc_name}(CSUserObject cs_uo) {{", file = out)
    print(f'      if (!cs_uo.uo.is_class_or_superclass("{uc_curie}")) {{', file = out)
    print(f'         throw new Exception("not {uc_name}");', file = out)
    print(f"      }}", file = out)
    print(f"      return new {uc_name}(cs_uo.uo);", file = out)
    print(f"  }}", file = out)
    print(f"", file = out)

def gen_Factory_load_user_object(out, g:KGMGraph):
    print(f"  public override CSUserObject create_cs_user_object__(UserObject uo) {{", file = out)
    print(f"      CSUserObject ret = null;", file = out)
    is_first_loop = True
    for uc in g.all_user_classes.values():
        uc_curie = collapse_prefix(uc.uc_uri, g.db.w_prefixes)
        uc_name = get_py_m_name(uc.uc_uri)
        print(f'      {"if" if is_first_loop else "else if"} (uo.is_class("{uc_curie}")) {{', file = out)
        print(f'         ret = new {uc_name}(uo);', file = out)
        print(f'      }}', file = out)
        is_first_loop = False
        #print(f"    {uc_curie} {uc_name}", file = out)
    print(f"      else {{", file = out)
    print(f'         throw new Exception("unknown type");', file = out)
    print(f"      }}", file = out)
    print(f"", file = out)
    print(f"      return ret;", file = out)
    print(f"  }}", file = out)    

def gen_UserClass_adapter_code(out, g:KGMGraph, uc:"UserClass"):
    uc_name = get_py_m_name(uc.uc_uri)
    print(f" public class {uc_name} : CSUserObject {{", file = out)
    print(f"   public {uc_name}(UserObject uo) {{", file = out)
    print(f"      this.uo = uo;", file = out)
    print(f"   }}", file = out)
    print(f"", file = out)
    
    print(f"   public static void set_default_values(UserObject uo) {{", file = out)

    for super_uc_uri in uc.super_uc_uris:
        super_uc = g.all_user_classes.get(super_uc_uri)
        super_uc_name = get_py_m_name(super_uc.uc_uri)
        print(f'     {super_uc_name}.set_default_values(uo);', file = out)
        
    for uc_m in uc.members.values():        
        is_scalar = uc_m.max_c == 1
        if uc_m.is_class == False and is_scalar == True:
            uc_m_name = get_py_m_name(uc_m.m_path_uri)
            uc_m_cs_type, uc_m_cs_dflt = datatype_cs_dets[uc_m.m_type_uri]
            print(f'     uo.get_member_editor("{uc_m_name}").svalue_set({uc_m_cs_dflt});', file = out)

    print(f"   }}", file = out)
    print(f"", file = out)
    
    for uc_m in uc.members.values():
        is_scalar = uc_m.max_c == 1
        uc_m_name = get_py_m_name(uc_m.m_path_uri)
        if uc_m.is_class == False:
            uc_m_cs_type, uc_m_cs_dflt = datatype_cs_dets[uc_m.m_type_uri]
            if is_scalar:
                print(f"   public {uc_m_cs_type} {uc_m_name} {{", file = out)
                print(f'     get {{ return uo.get_member_editor("{uc_m_name}").svalue_get() as {uc_m_cs_type}; }}', file = out)
                print(f'     set {{ uo.get_member_editor("{uc_m_name}").svalue_set(value); }}', file = out)
                print(f"   }}", file = out)
            else:
                print(f'   public CSUserObjectListStruct<{uc_m_cs_type.replace("?", "")}> {uc_m_name} {{', file = out)
                print(f'       get {{ return new CSUserObjectListStruct<{uc_m_cs_type.replace("?", "")}>(uo.get_member_editor("{uc_m_name}")); }}', file = out)
                print(f"   }}", file = out)
        else:
            uc_m_cs_type = get_py_m_name(uc_m.m_type_uri)
            if is_scalar:
                print(f"   public {uc_m_cs_type} {uc_m_name} {{", file = out)
                print(f'     get {{', file = out)
                print(f'         UserObject member_uo = uo.get_member_editor("{uc_m_name}").svalue_get() as UserObject;', file = out)
                print(f'         return member_uo.cs_uo as {uc_m_cs_type};', file = out)
                print(f'     }}', file = out)
                print(f'     set {{', file = out)
                print(f'         uo.get_member_editor("{uc_m_name}").svalue_set(value.uo);', file = out)
                print(f'     }}', file = out)
                print(f"   }}", file = out)
            else:
                print(f"   public CSUserObjectListClass<{uc_m_cs_type}> {uc_m_name} {{", file = out)
                print(f'       get {{', file = out)
                print(f'            var me = uo.get_member_editor("{uc_m_name}");', file = out)
                print(f'            return new CSUserObjectListClass<{uc_m_cs_type}>(me);', file = out)
                print(f'       }}', file = out)
                print(f"   }}", file = out)
            
    print(f" }} // end of {uc_name}", file = out)
    
def gen_code(g:KGMGraph, cs_namespace:str) -> str:
    out = io.StringIO()

    print("// generated code - do not edit", file = out)
    print("using kgm;", file = out)
    print("", file = out)
    print(f"namespace {cs_namespace} {{", file = out)

    print(" public class Factory : kgm.CSUserObjectFactory {", file = out)
    print("  public Factory() { this.g = null; }", file = out)

    for uc in g.all_user_classes.values():
        gen_Factory_create_method(out, g, uc)
    gen_Factory_load_user_object(out, g)
    print(" } // end of Factory", file = out)
    print("", file = out)
    print("", file = out)
    
    for uc in g.all_user_classes.values():
        gen_UserClass_adapter_code(out, g, uc)
        print("", file = out)

    print(f"}} // end of namespace {cs_namespace}", file = out)
    
    return out.getvalue()

def gencode_for_namespace(w_config, kgm_path, cs_namespace, output_dir):
    #ipdb.set_trace()
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)

    graph_uri = db.get_kgm_graph(kgm_path)
    if graph_uri is None:
        raise Exception(f"graph at path does not exists:", graph_uri)        

    kgm_g = KGMGraph(db, graph_uri, None)
    print(gen_code(kgm_g, cs_namespace))
    
    sys.exit(3)
    
    if output_dir != "-":
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

