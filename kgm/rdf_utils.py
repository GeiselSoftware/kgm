#import ipdb
from .rdf_terms import URI, Literal, BNode, RDFTermFactory

class RDFObject:
    def __init__(self, object_):
        assert(isinstance(object_, URI) or isinstance(object_, Literal))
        self.object_ = object_

    def to_turtle(self):
        return self.object_.to_turtle()
        
class RDFTriple:
    def __init__(self, s:URI, p:URI, o:RDFObject):
        self.subject = s
        self.pred = p
        self.object_ = o

    def to_turtle(self):
        return " ".join([x.to_turtle() for x in [self.subject, self.pred, self.object_]]) + " ."

def get_py_m_name(m_path_uri:URI) -> str:
    return m_path_uri.uri_s.split("--")[-1] # v.m_path_uri.get_suffix()
