class URI:
    def __init__(self, s):
        self.uri = s

    def __repr__(self):
        return self.uri
        
    def __eq__(self, o):
        assert(type(o) == URI)
        return self.uri == o.uri

    def __hash__(self):
        return self.uri.__hash__()

    def as_turtle(self):
        return collapse_prefix__(self.uri)

    def get_suffix(self):
        curie = collapse_prefix__(self.uri)
        return curie.split(':')[-1]
    
class Literal:
    def __init__(self, value, datatype_uri):
        assert(type(datatype_uri) == URI)
        self.datatype_uri = datatype_uri
        if self.datatype_uri == xsd.string:
            self.literal = value
        elif self.datatype_uri == xsd.integer:
            self.literal = int(value)
        elif self.datatype_uri == xsd.boolean:
            self.literal = value == "true"
        else:
            raise Exception(f"not supported datatype {self.datatype_uri}")

    def __repr__(self):
        return f"{self.literal}"

    def __eq__(self, o):
        if type(o) == Literal:
            return self.literal == o.literal
        return self.literal == o
    
    def __hash__(self):
        return o.__hash__()    

    def as_turtle(self):
        if self.datatype_uri == xsd.string:
            return f'"{self.literal}"'
        elif self.datatype_uri == xsd.integer:
            return f"{self.literal}"
        else:
            return '"' + f"{self.literal}" + '"' + "^^" + self.datatype_uri.as_turtle()
    
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
    
###########

class rdf:
    prefix__ = "rdf"
    prefix_uri__ = URI("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    type = URI(prefix_uri__.uri + "type")

class rdfs:
    prefix__ = "rdfs"
    prefix_uri__ = URI("http://www.w3.org/2000/01/rdf-schema#")
    Class = URI(prefix_uri__.uri + "Class")
    
class xsd:
    prefix__ = "xsd"
    prefix_uri__ = URI("http://www.w3.org/2001/XMLSchema#")
    string = URI(prefix_uri__.uri + "string")
    boolean = URI(prefix_uri__.uri + "boolean")
    integer = URI(prefix_uri__.uri + "integer")

xsd_dflt_cs_values = {}
xsd_dflt_cs_values[xsd.string] = "\"\""
xsd_dflt_cs_values[xsd.boolean] = "\"false\""
xsd_dflt_cs_values[xsd.integer] = "0"
    
class sh:
    prefix__ = "sh"
    prefix_uri__ = URI("http://www.w3.org/ns/shacl#")
    property = URI(prefix_uri__.uri + "property")

class kgm:
    prefix__ = "kgm"
    prefix_uri__ = URI("http://www.geisel-software.com/RDF/KGM#")
    Graph = URI(prefix_uri__.uri + "Graph")
    path = URI(prefix_uri__.uri + "path")
    
class ab:
    prefix__ = "ab"
    prefix_uri__ = URI("http://www.geisel-software.com/RDF/alice-bob#")

class nw:
    prefix__ = "nw"
    prefix_uri__ = URI("http://www.geisel-software.com/RDF/NorthWind#")

class TU:
    prefix__ = "TU"
    prefix_uri__ = URI("http://www.geisel-software.com/RDF/KGM/TestUser#")
    
known_prefixes = {
    rdf.prefix__: rdf.prefix_uri__,
    rdfs.prefix__: rdfs.prefix_uri__,
    xsd.prefix__: xsd.prefix_uri__,
    sh.prefix__: sh.prefix_uri__,
    kgm.prefix__: kgm.prefix_uri__,
    ab.prefix__: ab.prefix_uri__,
    nw.prefix__: nw.prefix_uri__,
    TU.prefix__: TU.prefix_uri__
}

def collapse_prefix__(uri:str):
    for p, p_uri in known_prefixes.items():
        if uri.find(p_uri.uri) == 0:
            return uri.replace(p_uri.uri, p + ":")
    raise Exception("can't collapse prefix for URI:", uri)

def restore_prefix__(curie:str):
    for prefix, prefix_uri in known_prefixes.items():
        if curie.find(prefix) == 0:
            return curie.replace(prefix + ":", prefix_uri.uri)
    raise Exception("can't restore prefix in curie", curie)
