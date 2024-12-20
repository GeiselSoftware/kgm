from lark import Lark, Transformer

ksd_grammar = \
    """
    start: prefix* class_defs
    prefix: "prefix" curie_prefix "<" uri ">"
    class_defs: rdfs_class_def (rdfs_class_def | rdfs_class_ext)*
    rdfs_class_def : "class" class_uri ("subclass of" subclass_uri)? ("end" | class_body "end")
    rdfs_class_ext : "extend class" class_uri ("subclass of" subclass_uri)? ("end" | class_body "end")
    class_uri: curie
    subclass_uri: curie
    class_body: class_member (WS class_member)*
    class_member: class_member_name class_member_type class_member_cardinality?
    class_member_name: curie
    class_member_type: curie
    class_member_cardinality: cardinality_spec
    
    curie_prefix: CNAME? ":"
    curie:  CNAME? ":" CNAME
    uri: /https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)/
    cardinality_spec: "[" number ".." number "]"
    number: DIGIT+ | "n" | "inf"
    string : ESCAPED_STRING
    
    %import common.CNAME
    %import common.DIGIT
    %import common.ESCAPED_STRING
    %import common.SH_COMMENT
    %import common.SIGNED_NUMBER
    %import common.WS

    %ignore SH_COMMENT
    %ignore WS
    """

class MyTransformer(Transformer):
    def prefix(self, v):
        print("prefix:", v)
        #return v
        
    def class_uri(self, v):
        print("class_uri:", v)

    def subclass_uri(self, v):
        print("subclass_uri:", v)
        
    def class_member_name(self, m):
        print("class_member_name:", m)

    def class_member_type(self, m):
        print("class_member_type:", m)

    def class_member_cardinality(self, m):
        print("class_member_cardinality:", m)
        
    #def __default_token__(self, t):
    #    print(t)

class KSDParser:
    def do_it(self, kgm_path, ksd_filename):
        print("ksd_filename:", ksd_filename, type(ksd_filename))
        print("kgm_path:", kgm_path)
        
        l = Lark(ksd_grammar)
        with open(ksd_filename, 'r') as f:
            ksd_code = f.read()

        #print(ksd_code)

        tree = l.parse(ksd_code, start = "start")
        #print(tree.pretty())
        MyTransformer().transform(tree)
