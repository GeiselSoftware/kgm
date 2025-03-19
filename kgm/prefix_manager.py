from kgm.rdf_terms import URI, RDFTriple
from kgm.prefixes import well_known_prefixes
from .rdf_terms import URI, Literal, BNode, RDFObject, RDFTriple

class PrefixManager:
    def __init__(self, empty_prefix):
        self.w_prefixes = {}
        self.w_prefixes[":"] = well_known_prefixes["kgm:"] + empty_prefix + ":" # must be first, : maps to urn:kgm: with empty namespace
        for k, v in well_known_prefixes.items():
            self.w_prefixes[k] = v

    def to_turtle(self, o):
        if isinstance(o, URI):
            ret = self.collapse_prefix(o)
        elif isinstance(o, BNode):
            ret = "_:" + o.bnode
        elif isinstance(o, Literal):
            ret = f'"{o.value_o}"^^<{o.datatype_uri}>'
        elif isinstance(o, RDFObject):
            ret = self.to_turtle(o.object_)
        elif isinstance(o, RDFTriple):
            ret = f"{self.to_turtle(o.subject)} {self.to_turtle(o.pred)} {self.to_turtle(o.object_)} ."
        else:
            raise Exception("can't covert to turtle")
        return ret

    def restore_prefix(self, curie:str) -> URI:
        assert(type(curie) == str)
        for prefix, prefix_uri in self.w_prefixes.items():
            if curie.find(prefix) == 0:
                return URI(curie.replace(prefix, prefix_uri))
        raise Exception("can't restore prefix in curie", curie)

    def collapse_prefix(self, uri:URI) -> str:
        assert(isinstance(uri, URI))
        for p, p_uri in self.w_prefixes.items():
            #print(uri, p_uri)
            if uri.uri_s.find(p_uri) == 0:
                return uri.uri_s.replace(p_uri, p)
        raise Exception("can't collapse prefix for uri:", uri)

    def make_rq(self, rq:str) -> str:
        #ipdb.set_trace()
        ret = "\n".join([f"prefix {prefix} <{prefix_uri_s}>" for prefix, prefix_uri_s in self.w_prefixes.items()]) \
            + "\n" + rq
        return ret        

    def make_RDFTriple_from_turtle_statement(self, turtle_statement:str) -> RDFTriple:
        return ...

    def make_turtle_statement_from_RDFTriple(self, rdf_triple:RDFTriple) -> str:
        return ...
    
