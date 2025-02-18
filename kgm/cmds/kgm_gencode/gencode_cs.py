import ipdb
import sys, io
from kgm.database import Database
from kgm.kgm_graph import KGMGraph
from kgm.rdf_utils import collapse_prefix

def gen_Factory_create_method(out, g:KGMGraph, uc:"UserClass"):
    #ipdb.set_trace()
    uc_name = uc.uc_uri.uri_s
    args = ""
    uc_curie = collapse_prefix(uc.uc_uri, g.db.w_prefixes)

    print(f"  public {uc_name} create_{uc_name}({args}) {{", file = out)
    print(f'     UserObject uo = this.g.create_user_object("{uc_curie}");', file = out)
    print(f"     {uc_name} ret = new {uc_name}(uo);", file = out)
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

    print(f"  }}", file = out)

def gen_Factory_load_user_object(out, g:KGMGraph):
    print(f"  public async Task<CSUserObject> load_user_object(URI uri) {{", file = out)
    print(f"      UserObject uo = await this.g.load_user_object(uri);", file = out)
    print(f"      CSUserObject ret = null;", file = out)
    
    print(f"      return ret;", file = out)
    print(f"  }}", file = out)    

def gen_UserClass_adapter_code(out, g:KGMGraph, uc:"UserClass"):
    uc_name = uc.uc_uri.uri_s
    print(f" public class {uc_name} {{", file = out)
    print(f"   public {uc_name} : CSUserObject {{", file = out)
    print(f"      this.uo = uo;", file = out)
    print(f"   }}", file = out)
    print(f"", file = out)
    print(f"   public static void set_default_values(UserObject uo) {{", file = out)
    print(f"   }}", file = out)
    print(f" }} // end of {uc_name}", file = out)
    
def gen_code(g:KGMGraph, target_namespace:str) -> str:
    out = io.StringIO()

    print("// generated code - do not edit", file = out)
    print("using kgm;", file = out)
    print("", file = out)
    print(f"namespace {target_namespace} {{", file = out)

    print(" public class Factory {", file = out)
    print("  private KGMGraph g;", file = out)
    print("  public Factory(KGMGraph g) { this.g = g; }", file = out)

    for uc in g.all_user_classes.values():
        gen_Factory_create_method(out, g, uc)
    gen_Factory_load_user_object(out, g)
    print(" } // end of Factory", file = out)
    print("", file = out)
    print("", file = out)
    
    for uc in g.all_user_classes.values():
        gen_UserClass_adapter_code(out, g, uc)
        print("", file = out)

    print(f"}} // end of namespace", file = out)
    
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

