#import ipdb
from .prefixes import xsd
from .rdf_terms import URI, Literal

def get_py_m_name(m_path_uri:URI) -> str:
    #ipdb.set_trace()
    return m_path_uri.uri_s.split(":")[-1] # v.m_path_uri.get_suffix()

def make_URI_from_string(full_uri_s:str) -> URI:
    assert(isinstance(full_uri_s, str))
    return URI(full_uri_s)

def make_URI_from_parts(prefix_part:URI, suffix_part:str) -> URI:
    assert(isinstance(prefix_part, URI))
    assert(isinstance(suffix_part, str))
    return URI(prefix_part.uri_s + suffix_part)

def make_Literal(value_o, datatype_uri):
    return Literal(value_o, datatype_uri)

def get_supported_Literal_python_types():
    return [str, bool, int, float]

def from_python_to_Literal(v:object) -> Literal:
    if type(v) == str:
        return make_Literal(f'{v}', xsd.string)
    elif type(v) == bool:
        return make_Literal("true" if v else "false", xsd.boolean)
    elif type(v) == int:
        return make_Literal(f"{v}", xsd.integer)
    elif type(v) == float:
        return make_Literal(f"{v}", xsd.float)

    raise Exception(f"from_python_to_Literal: unsupported type {type(v)}")

def from_Literal_to_python(l:Literal) -> object:
    ret = None
    if l.datatype_uri == xsd.string:
        ret = f"{l.value_o}"
    elif l.datatype_uri == xsd.boolean:
        ret = l.value_o.lower() == "true"
    elif l.datatype_uri == xsd.integer:
        ret = int(l.value_o)
    elif l.datatype_uri == xsd.float:
        ret = float(l.value_o)
    else:
        #ipdb.set_trace()
        raise Exception(f"unsupported xsd type: {l.datatype_uri}")

    return ret
