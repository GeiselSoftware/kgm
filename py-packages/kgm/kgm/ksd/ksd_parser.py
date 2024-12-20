from lark import Lark

ksd_grammar = \
    """
    ?start: value

    value: prefixes class_defs

    prefixes : ("prefix" curie_prefix "<" uri ">")*
    
    class_defs: rdfs_class_def (rdfs_class_def | rdfs_class_ext)*
    rdfs_class_def : "class" class_uri ("subclass of" subclass_uri)? ("end" | class_body "end")
    rdfs_class_ext : "extend class" class_uri ("subclass of" subclass_uri)? ("end" | class_body "end")
    class_uri: curie
    subclass_uri: curie
    class_body: class_member (WS class_member)*
    class_member: curie curie cardinality_spec?

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

class KSDParser:
    def do_it(self, kgm_path, ksd_filename):
        print("ksd_filename:", ksd_filename, type(ksd_filename))
        print("kgm_path:", kgm_path)
        
        l = Lark(ksd_grammar)
        with open(ksd_filename, 'r') as f:
            ksd_code = f.read()

        #print(ksd_code)
        #print(l.parse("Hello, world!"))
        #print(l.parse(ksd_code))
        tree = l.parse(ksd_code)
        print(tree.pretty())
