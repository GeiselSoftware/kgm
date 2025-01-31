#import ipdb
#from . import xsd

class URI:
    def __init__(self, uri_string:str):
        assert(type(uri_string) == str)
        assert(len(uri_string) > 2 and uri_string[0] != "<" and uri_string[-1] != ">")
        self.uri = uri_string
        
    def __repr__(self):
        return self.uri
        
    def __eq__(self, o):
        assert(type(o) == URI)
        return self.uri == o.uri

    def __hash__(self):
        return self.uri.__hash__()
    
class Literal:
    def __init__(self, value_o, datatype_uri):
        assert(type(datatype_uri) == URI)
        self.value_o = value_o
        self.datatype_uri = datatype_uri
        
    def __repr__(self):
        return f"{self.value_o}"

    def __eq__(self, o):
        assert(type(o) == Literal)
        return self.value_o == o.value_o
    
    def __hash__(self):
        return self.value_o.__hash__()    
        
class BNode:
    def __init__(self, s):
        self.bnode = s

    def __repr__(self):
        return f"{self.bnode}"
    
class RDFObject:
    def __init__(self, object_):
        assert(isinstance(object_, URI) or isinstance(object_, Literal))
        self.object_ = object_

class RDFTriple:
    def __init__(self, s:URI, p:URI, o:RDFObject):
        self.subject = s
        self.pred = p
        self.object_ = o
