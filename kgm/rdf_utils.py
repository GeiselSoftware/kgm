#import ipdb
from .rdf_terms import URI, Literal, BNode, RDFObject, RDFTriple
from .prefixes import xsd

def get_py_m_name(m_path_uri:URI) -> str:
    #ipdb.set_trace()
    return m_path_uri.uri_s.split(":")[-1] # v.m_path_uri.get_suffix()

def restore_prefix(curie:str, w_prefixes) -> URI:
    assert(type(curie) == str)
    for prefix, prefix_uri in w_prefixes.items():
        if curie.find(prefix) == 0:
            return URI(curie.replace(prefix, prefix_uri))
    raise Exception("can't restore prefix in curie", curie)

def collapse_prefix(uri:URI, w_prefixes) -> str:
    assert(isinstance(uri, URI))
    for p, p_uri in w_prefixes.items():
        #print(uri, p_uri)
        if uri.uri_s.find(p_uri) == 0:
            return uri.uri_s.replace(p_uri, p)
    raise Exception("can't collapse prefix for uri:", uri)

def to_turtle(o, w_prefixes):
    if isinstance(o, URI):
        ret = collapse_prefix(o, w_prefixes)
    elif isinstance(o, BNode):
        ret = "_:" + o.bnode
    elif isinstance(o, Literal):
        ret = f'"{o.value_o}"^^<{o.datatype_uri}>'
    elif isinstance(o, RDFObject):
        ret = to_turtle(o.object_, w_prefixes)
    elif isinstance(o, RDFTriple):
        ret = f"{to_turtle(o.subject, w_prefixes)} {to_turtle(o.pred, w_prefixes)} {to_turtle(o.object_, w_prefixes)} ."
    else:
        raise Exception("can't covert to turtle")
    return ret

def make_rq(rq:str, w_prefixes) -> str:
    #ipdb.set_trace()
    ret = "\n".join([f"prefix {prefix} <{prefix_uri_s}>" for prefix, prefix_uri_s in w_prefixes.items()]) \
        + "\n" + rq
    return ret

def make_URI_from_string(full_uri_s:str) -> URI:
    assert(isinstance(full_uri_s, str))
    return URI(full_uri_s)

def make_URI_from_parts(prefix_part:URI, suffix_part:str) -> URI:
    assert(isinstance(prefix_part, URI))
    assert(isinstance(suffix_part, str))
    return URI(prefix_part.uri_s + suffix_part)

def make_Literal(value_o, datatype_uri):
    return Literal(value_o, datatype_uri)

def from_python_to_Literal(v):
    if type(v) == str:
        return make_Literal(f'{v}', xsd.string)
    elif type(v) == bool:
        return make_Literal("true" if v else "false", xsd.boolean)
    elif type(v) == int:
        return make_Literal(f"{v}", xsd.integer)
    elif type(v) == float:
        return make_Literal(f"{v}", xsd.float)

    raise Exception(f"from_python_to_Literal: unsupported type {type(v)}")
