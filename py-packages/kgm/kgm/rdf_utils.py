class URI:
    def __init__(self, compact_uri):
        assert(type(compact_uri) == str)
        if len(compact_uri) >= 2 and compact_uri[0] == "<" and compact_uri[-1] == ">":
            # need to convert to compact uri
            self.compact_uri = collapse_prefix__(compact_uri)
        else:
            self.compact_uri = compact_uri

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
            return Literal(f'"{v}"', xsd.string)
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

xsd_dflt_cs_values = {}
xsd_dflt_cs_values[xsd.string] = "\"\""
xsd_dflt_cs_values[xsd.boolean] = "\"false\""
xsd_dflt_cs_values[xsd.integer] = "0"

class sh:
    prefix__ = "sh"
    prefix_uri__ = "http://www.w3.org/ns/shacl#"

sh.property = build_uri__(sh, "property")

class kgm:
    prefix__ = "kgm"
    prefix_uri__ = "http://www.geisel-software.com/RDF/KGM#"

kgm.Graph = build_uri__(kgm, "Graph")
kgm.path = build_uri__(kgm, "path")

class ab:
    prefix__ = "ab"
    prefix_uri__ = "http://www.geisel-software.com/RDF/alice-bob#"
    
class nw:
    prefix__ = "nw"
    prefix_uri__ = "http://www.geisel-software.com/RDF/NorthWind#"

class __:
    prefix__ = ""
    prefix_uri__ = "http://www.geisel-software.com/RDF/KGM/TestUser#"

known_prefixes = {
    rdf.prefix__: rdf.prefix_uri__,
    rdfs.prefix__: rdfs.prefix_uri__,
    xsd.prefix__: xsd.prefix_uri__,
    sh.prefix__: sh.prefix_uri__,
    kgm.prefix__: kgm.prefix_uri__,
    ab.prefix__: ab.prefix_uri__,
    nw.prefix__: nw.prefix_uri__,
    __.prefix__: __.prefix_uri__
}

def collapse_prefix__(uri:str):
    assert(type(uri) == str)
    for p, p_uri in known_prefixes.items():
        #print(uri, p_uri)
        if uri.find(p_uri) == 0:
            return uri.replace(p_uri, p + ":")
    raise Exception("can't collapse prefix for URI:", uri)

def restore_prefix__(curie:str):
    assert(type(curie) == str)    
    for prefix, prefix_uri in known_prefixes.items():
        if curie.find(prefix) == 0:
            return curie.replace(prefix + ":", prefix_uri)
    raise Exception("can't restore prefix in curie", curie)

