import ipdb
from lark import Lark, Visitor

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
    
    curie_prefix: CNAME? COLON
    curie: CNAME? COLON CNAME
    COLON: ":"
    uri: /https?:\\/\\/(?:www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)/
    cardinality_spec: "[" minc ".." maxc "]"
    minc: INT
    maxc: INT | INF
    INF: "inf" | "n"
    
    %import common.CNAME
    %import common.INT
    %import common.SH_COMMENT
    %import common.WS

    %ignore SH_COMMENT
    %ignore WS
    """

class MyClassMemberVisitor(Visitor):
    def __init__(self):
        self.min_c = 1
        self.max_c = 1
        
    def class_member_name(self, m):
        self.member_name_uri = "".join([x.value for x in m.children[0].children])
        #print("class_member_name:", member_name_uri)
        
    def class_member_type(self, m):
        self.member_type_uri = "".join([x.value for x in m.children[0].children])
        #print("class_member_type:", member_type_uri)

    def class_member_cardinality(self, m):
        minc = m.children[0].children[0].children[0].value
        maxc = m.children[0].children[1].children[0].value
        self.min_c = int(minc)
        self.max_c = int(maxc) if maxc not in ["n", "inf"] else -1
        #ipdb.set_trace()
        #print("class_member_cardinality:", minc, maxc)
        
class MyClassVisitor(Visitor):
    def __init__(self):
        self.members = []
        self.superclasses = []

    def subclass_uri(self, m):
        #print("subclass_uri:", m)
        self.superclasses.append("".join([x.value for x in m.children[0].children]))
        #ipdb.set_trace()
        
    def class_member(self, m):
        #print("class_member:", m)
        v = MyClassMemberVisitor()
        v.visit(m)
        self.members.append((v.member_type_uri, v.member_name_uri, v.min_c, v.max_c))
    
class MyVisitor(Visitor):
    def __init__(self):
        self.local_prefixes = {}
        self.known_rdfs_classes = {}
        
    def prefix(self, m):
        prefix = "".join([x.value for x in m.children[0].children])
        uri = m.children[1].children[0].value
        self.local_prefixes[prefix] = uri

    def rdfs_class_def(self, m):
        class_uri = "".join([x.value for x in m.children[0].children[0].children])
        if class_uri in self.known_rdfs_classes:
            raise Exception(f"attempt to redefined rdfs class {class_uri}")
        v = MyClassVisitor(); v.visit(m)
        self.known_rdfs_classes[class_uri] = (v.superclasses, v.members)

    def rdfs_class_ext(self, m):
        class_uri = "".join([x.value for x in m.children[0].children[0].children])
        if not class_uri in self.known_rdfs_classes:
            raise Exception(f"attempt to extend unknown rdfs class {class_uri}")        
        v = MyClassVisitor(); v.visit(m)
        self.known_rdfs_classes[class_uri][0].extend(v.superclasses)
        self.known_rdfs_classes[class_uri][1].extend(v.members)
        
class KSDParser:
    def do_it(self, kgm_path, ksd_filename):
        #print("ksd_filename:", ksd_filename, type(ksd_filename))
        #print("kgm_path:", kgm_path)
        
        l = Lark(ksd_grammar)
        with open(ksd_filename, 'r') as f:
            ksd_code = f.read()

        #print(ksd_code)

        tree = l.parse(ksd_code, start = "start")
        #print(tree.pretty())

        v = MyVisitor()
        v.visit_topdown(tree)
        print("+++++++++++++++")
        for prefix, prefix_uri in v.local_prefixes.items():
            print(prefix, prefix_uri)

        print("---------------")
        for rdfs_class_uri, cls in v.known_rdfs_classes.items():
            print(rdfs_class_uri, cls[0]) # superclasses
            print("  ", cls[1]) # members
            
        
