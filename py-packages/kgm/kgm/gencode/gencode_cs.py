class UserClass:
    def __init__(self):
        self.name = None
    
def gencode_cs():
    print("gencode_cs")
    user_class = UserClass()
    user_class.name = "CD_KeyPair"
    user_class.uriref_class = "URIRef_" + user_class.name
    user_class.user_class_uri = "http://www.geisel-software.com/RDF/KGM/TestUser#KeyPair"
    
    print("""
    // generated code
    using System.Collections.Generic;
    using System.Diagnostics;
    using System.Threading.Tasks;
    using kgm;
    
    public class {{user_class.name}} {
      public static URI uo_class_uri = new URI("{{user_class.user_class_uri}}");
      public {{user_class.name}}() {
      }

      public static Dictionary<string, uc_member_info> user_class_info = new Dictionary<string, uc_member_info>{
      }

    }

    public class {{user_class.uriref_class}} : URIRef {
      [DebuggerBrowsable(DebuggerBrowsableState.Never)]
      {{user_class.name}} ref_;
      public {{user_class.uriref_class}}(URI uri, {{user_class.name}} ref_) { this.uri = uri; this.ref_ = ref_; }

      public override object get_ref() { return this.ref_ as object; }
      public override Dictionary<string, uc_member_info> get_user_class_info() { return CD_KeyPair.user_class_info; }
      public override URI get_uo_class_uri() { return {{user_class.name}}.uo_class_uri; }

      public static {{user_class.uriref_class}} create(URI? uri)
      {
        if (uri == null) {
            uri = RDFUtils.create_uo_uri({{user_class.name}}.uo_class_uri);
        }
        {{user_class.name}} new_uo_ref = new {{user_class.name}}();
        return new {{user_class.uriref_class}}(uri, new_uo_ref);
      }

      public static async Task<{{user_class.uriref_class}}> load(GraphDB gdb, URI uo_uri) {
        {{user_class.uriref_class}} ret = {{user_class.uriref_class}}.create(uo_uri);
        await gdb.load(ret);
        return ret;
      }

      public async Task save(GraphDB gdb) {
        await gdb.save(this);
      }
    }

    """.replace("{{user_class.uriref_class}}", user_class.uriref_class)
          .replace("{{user_class.name}}", user_class.name)
          .replace("{{user_class.user_class_uri}}", user_class.user_class_uri))
