#import ipdb
from lark import Lark, Visitor
import pandas as pd
from kgm.prefixes import well_known_prefixes

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

class ClassMemberDescriptor:
    def __init__(self, member_name_uri, member_type_uri, minc, maxc):
        self.member_name_uri = member_name_uri
        self.member_type_uri = member_type_uri
        self.minc = minc
        self.maxc = maxc
        
class ClassDescriptor:
    def __init__(self, class_uri, superclasses, members):
        self.class_uri = class_uri
        self.superclasses = superclasses
        self.members = members
        
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
        self.members.append(ClassMemberDescriptor(v.member_name_uri, v.member_type_uri, v.min_c, v.max_c))
    
class MyVisitor(Visitor):
    def __init__(self):
        self.known_rdfs_classes = {}
        
    def prefix(self, m):
        prefix = "".join([x.value for x in m.children[0].children])
        uri = m.children[1].children[0].value

    def rdfs_class_def(self, m):
        class_uri = "".join([x.value for x in m.children[0].children[0].children])
        if class_uri in self.known_rdfs_classes:
            raise Exception(f"attempt to redefined rdfs class {class_uri}")
        v = MyClassVisitor(); v.visit(m)
        self.known_rdfs_classes[class_uri] = ClassDescriptor(class_uri, v.superclasses, v.members)

    def rdfs_class_ext(self, m):
        class_uri = "".join([x.value for x in m.children[0].children[0].children])
        if not class_uri in self.known_rdfs_classes:
            raise Exception(f"attempt to extend unknown rdfs class {class_uri}")        
        v = MyClassVisitor(); v.visit(m)
        class_desc = self.known_rdfs_classes[class_uri]
        class_desc.superclasses.extend(v.superclasses)
        class_desc.members.extend(v.members)
        
class KSDParser:
    @staticmethod
    def dump_ksd(db, kgm_path):
        rq = f"""\
        select ?uc ?uc_m_name ?uc_m_is_class ?uc_m_type ?uc_m_minc ?uc_m_maxc {{
         ?g kgm:path "{kgm_path}"
         graph ?g {{
          ?uc rdf:type rdfs:Class .
          ?uc sh:property ?uc_p.
          ?uc_p sh:path ?uc_m_name filter(?uc_m_name != rdf:type).
          ?uc_p sh:minCount ?uc_m_minc.
          optional {{ ?uc_p sh:maxCount ?uc_m_maxc }}
          {{ optional {{ ?uc_p sh:datatype ?uc_m_type bind(false as ?uc_m_is_class) }} }}
          union {{ optional {{ ?uc_p sh:class ?uc_m_type bind(true as ?uc_m_is_class)}} }}
         }}
        }}
        """
        #print(make_rq(rq))
        classes_dets = pd.DataFrame(db.rq_select(rq))
        #print(classes_dets)

        rq = f"""\
        select ?uc ?super_uc {{
         ?g kgm:path "{kgm_path}"
         graph ?g {{
          ?uc rdf:type rdfs:Class; rdfs:subClassOf ?super_uc .
         }}
        }}
        """
        superclasses_dets = pd.DataFrame(db.rq_select(rq))
        #print(superclasses_dets)

        #ipdb.set_trace()
        print(f'prefix : <urn:kgm::>')
        print()
        
        for class_uri in classes_dets.uc.unique():
            #ipdb.set_trace()
            F = superclasses_dets.uc == class_uri
            superclasses = ""
            if F.any():
                superclasses = ";".join([f"subclass of {x}" for x in superclasses_dets.loc[F, 'super_uc']])
            print(f"class {class_uri} {superclasses}")
            
            F = classes_dets.uc == class_uri
            #ipdb.set_trace()
            for m in classes_dets.loc[F, :].itertuples():
                minc = from_Literal_to_python(m.uc_m_minc)
                maxc = from_Literal_to_python(m.uc_m_maxc) if m.uc_m_maxc is not None else -1
                card = ""
                if not (minc == 1 and maxc == 1):
                    maxc = f"{maxc}" if maxc != -1 else "inf"
                    card = f"[{minc}..{maxc}]"                    
                print(f" {m.uc_m_name} {m.uc_m_type}{card}")
            print(f"end\n")
        
        
    def parse_ksd_file(self, ksd_filename):
        l = Lark(ksd_grammar)
        with open(ksd_filename, 'r') as f:
            ksd_code = f.read()

        #print(ksd_code)

        tree = l.parse(ksd_code, start = "start")
        #print(tree.pretty())

        v = MyVisitor()
        v.visit_topdown(tree)

        for prefix in ["rdf:", "rdfs:", "sh:", "xsd:"]:
            uri = well_known_prefixes[prefix]
            print(f"@prefix {prefix} <{uri[0]}> .")
            
        print(f"@prefix : <urn:kgm::> .") # empty prefix for empty kgm namespace

        print()

        for rdfs_class_uri, cls in v.known_rdfs_classes.items():
            #print(cls.class_uri, cls.superclasses)
            #print(" ", [x.__dict__ for x in cls.members])

            print(f"{cls.class_uri} rdf:type rdfs:Class;")
            for c in cls.superclasses:
                print(f"    rdfs:subClassOf {c};")
            print("     rdf:type sh:NodeShape; sh:closed true;")
            
            for m in cls.members:
                shacl_m = []
                shacl_m.append(f"sh:path {m.member_name_uri}")
                if m.member_type_uri.startswith("xsd:"):
                    shacl_m.append(f"sh:datatype {m.member_type_uri}")
                else:
                    shacl_m.append(f"sh:class {m.member_type_uri}")
                shacl_m.append(f"sh:minCount {m.minc}")
                if m.maxc >= 0:
                    shacl_m.append(f"sh:maxCount {m.maxc}")
                print(f' sh:property [{"; ".join(shacl_m)}];')
            print(".\n")
        
