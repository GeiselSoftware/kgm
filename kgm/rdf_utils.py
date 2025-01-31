#import ipdb
from .known_prefixes import xsd
from .rdf_terms import URI, Literal, BNode, RDFObject

def collapse_prefix__(uri:str, prefixes):
    assert(type(uri) == str)
    for p, p_uri in prefixes.items():
        #print(uri, p_uri)
        if uri.find(p_uri) == 0:
            return uri.replace(p_uri, p + ":")
    raise Exception("can't collapse prefix for URI:", uri)    

def to_turtle(rdf_o, prefixes = None) -> str:
    ret = None
    if isinstance(rdf_o, URI):
        if prefixes is not None:
            ret = collapse_prefix__(rdf_o.uri, prefixes)
        else:
            ret = "<" + rdf_o.uri + ">"
    elif isinstance(rdf_o, Literal):
        if rdf_o.datatype_uri == xsd.string:
            ret = f'"{rdf_o.value_o}"'
        elif rdf_o.datatype_uri == xsd.integer:
            ret = f"{rdf_o.value_o}"
        else:
            ret = '"' + f"{rdf_o.value_o}" + '"' + "^^" + to_turtle(self.datatype_uri)
    elif isinstance(rdf_o, BNode):
        ret = "_:" + rdf_o.bnode
    elif isinstance(rdf_o, RDFObject):        
        return to_turtle(rdf_o.object_)
    else:
        raise "to_turtle() failed"
    
    return ret

def as_python(rdf_o):
    ret = None
    if isinstance(rdf_o, Literal):
        if rdf_o.datatype_uri == xsd.string:
            ret = f"{self.value_o}"
        elif self.datatype_uri == xsd.integer:
            ret = int(self.value_o)
        elif self.datatype_uri == xsd.boolean:
            ret =self.value_o.lower() == "true"
        else:
            #ipdb.set_trace()
            raise Exception(f"unsupported xsd type: {to_turtle(self.datatype)}")
    else:
        raise Exception("as_python failed")

    return ret

def from_python_to_Literal(v):
    if type(v) == str:
        return Literal(f'{v}', xsd.string)
    elif type(v) == bool:
        return Literal("true" if v else "false", xsd.boolean)
    elif type(v) == int:
        return Literal(f"{v}", xsd.integer)

    raise Exception(f"from_python: unsupported type {typeof(v)}")

