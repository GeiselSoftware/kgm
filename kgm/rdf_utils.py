#import ipdb

class PrefixManager:
    def __init__(self):
        self.is_initialized = False
        self.prefixes = {} # prefix -> prefix_uri

    def collapse_prefix(self, uri:str) -> str:
        assert(self.is_initialized)
        assert(type(uri) == str)
        for p, p_uri in self.prefixes.items():
            #print(uri, p_uri)
            if uri.find(p_uri) == 0:
                return uri.replace(p_uri, p + ":")
        raise Exception("can't collapse prefix for URI:", uri)

    def restore_prefix(self, curie:str) -> str:
        assert(self.is_initialized)
        assert(type(curie) == str)    
        for prefix, prefix_uri in self.prefixes.items():
            if curie.find(prefix) == 0:
                return curie.replace(prefix + ":", prefix_uri)
        raise Exception("can't restore prefix in curie", curie)

class URI:
    def __init__(self, uri:str):
        global prefix_man
        assert(type(uri) == str)
        self.compact_uri = None
        if len(uri) >= 2 and uri[0] == "<" and uri[-1] == ">":
            # need to convert to compact uri
            self.compact_uri = prefix_man.collapse_prefix(uri)
        else:
            self.compact_uri = uri

    def __repr__(self):
        return self.compact_uri
        
    def __eq__(self, o):
        assert(type(o) == URI)
        return self.compact_uri == o.compact_uri

    def __hash__(self):
        return self.compact_uri.__hash__()

    def as_turtle(self):
        return self.compact_uri

    def get_suffix(self):
        return self.compact_uri.split(':')[-1]

    def get_prefix(self):
        return self.compact_uri.split(':')[0]
    
class Literal:
    def __init__(self, value_o, datatype_uri):
        assert(type(datatype_uri) == URI)
        self.value_o = value_o
        self.datatype_uri = datatype_uri

    @staticmethod
    def from_python(v):
        if type(v) == str:
            return Literal(f'{v}', xsd.string)
        elif type(v) == bool:
            return Literal("true" if v else "false", xsd.boolean)
        elif type(v) == int:
            return Literal(f"{v}", xsd.integer)
        
        raise Exception(f"to_python: unsupported type {typeof(v)}")
        
    def __repr__(self):
        return f"{self.value_o}"

    def __eq__(self, o):
        assert(type(o) == Literal)
        return self.value_o == o.value_o
    
    def __hash__(self):
        return self.value_o.__hash__()    

    def as_turtle(self):
        if self.datatype_uri == xsd.string:
            return f'"{self.value_o}"'
        elif self.datatype_uri == xsd.integer:
            return f"{self.value_o}"
        else:
            return '"' + f"{self.value_o}" + '"' + "^^" + self.datatype_uri.as_turtle()

    def as_python(self):
        if self.datatype_uri == xsd.string:
            return f"{self.value_o}"
        elif self.datatype_uri == xsd.integer:
            return int(self.value_o)
        elif self.datatype_uri == xsd.boolean:
            return self.value_o.lower() == "true"
        else:
            #ipdb.set_trace()
            raise Exception(f"unsupported xsd type: {self.datatype_uri.as_turtle()}")        
        
class BNode:
    def __init__(self, s):
        self.bnode = s

    def __repr__(self):
        return f"{self.bnode}"

    def as_turtle(self):
        return "_:" + self.bnode
    
class RDFObject:
    def __init__(self, object_):
        self.object_ = object_

    def as_turtle(self):
        return self.object_.as_turtle()

class RDFTriple:
    def __init__(self, s:URI, p:URI, o:RDFObject):
        self.subject = s
        self.pred = p
        self.object_ = o

######################

def build_uri__(prefix_cls, suffix):
    return URI(prefix_cls.prefix__ + ":" + suffix)

class rdf:
    prefix__ = "rdf"
    prefix_uri__ = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

rdf.type = build_uri__(rdf, "type")

class rdfs:
    prefix__ = "rdfs"
    prefix_uri__ = "http://www.w3.org/2000/01/rdf-schema#"
    
rdfs.Class = build_uri__(rdfs, "Class")
    
class xsd:
    prefix__ = "xsd"
    prefix_uri__ = "http://www.w3.org/2001/XMLSchema#"

xsd.string = build_uri__(xsd, "string")
xsd.boolean = build_uri__(xsd, "boolean")
xsd.integer = build_uri__(xsd, "integer")
xsd.float = build_uri__(xsd, "float")
xsd.double = build_uri__(xsd, "double")

xsd_dflt_cs_values = {}
xsd_dflt_cs_values[xsd.string] = "\"\""
xsd_dflt_cs_values[xsd.boolean] = "\"false\""
xsd_dflt_cs_values[xsd.integer] = "0"
xsd_dflt_cs_values[xsd.float] = "0.0f"
xsd_dflt_cs_values[xsd.double] = "0.0"

class sh:
    prefix__ = "sh"
    prefix_uri__ = "http://www.w3.org/ns/shacl#"

sh.property = build_uri__(sh, "property")
sh.path = build_uri__(sh, "path")
sh.datatype = build_uri__(sh, "datatype")
sh.class_ = build_uri__(sh, "class")
sh.min_c = build_uri__(sh, "minCount")
sh.max_c = build_uri__(sh, "maxCount")
sh.NodeShape = build_uri__(sh, "NodeShape")

class dash:
    prefix__ = "dash"
    prefix_uri__ = "http://datashapes.org/dash#"

dash.closedByType = build_uri__(dash, "closedByType")

class kgm:
    prefix__ = "kgm"
    prefix_uri__ = "http://www.geisel-software.com/RDF/KGM#"

kgm.Graph = build_uri__(kgm, "Graph")
kgm.path = build_uri__(kgm, "path")

known_prefixes = {
    rdf.prefix__: rdf.prefix_uri__,
    rdfs.prefix__: rdfs.prefix_uri__,
    xsd.prefix__: xsd.prefix_uri__,
    sh.prefix__: sh.prefix_uri__,
    dash.prefix__: dash.prefix_uri__,
    kgm.prefix__: kgm.prefix_uri__,
}

