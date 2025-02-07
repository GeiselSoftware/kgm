import ipdb
from collections import namedtuple

well_known_prefixes = {
    "rdf": ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", ["type"]),
    "rdfs": ("http://www.w3.org/2000/01/rdf-schema#", ["Class"]),
    "xsd": ("http://www.w3.org/2001/XMLSchema#", ["string", "boolean", "integer", "float", "double"]),
    "sh": ("http://www.w3.org/ns/shacl#", ["property", "path", "datatype", "class___", "minCount", "maxCount", "NodeShape"]),
    "dash": ("http://datashapes.org/dash#", ["closedByType"]),
    "kgm": ("urn:kgm:", ["Graph", "path"])
}

class URI:
    def __init__(self, uri_s:str):
        assert(type(uri_s) == str)
        assert(len(uri_s) > 2 and uri_s[0] != "<" and uri_s[-1] != ">")
        self.uri_s = uri_s
        
    def __repr__(self):
        return self.uri_s
        
    def __eq__(self, o):
        assert(type(o) == URI)
        return self.uri_s == o.uri_s

    def __hash__(self):
        return self.uri_s.__hash__()

    def to_turtle(self, rdftf:"RDFTermFactory") -> str:
        if rdftf is None:
            for p, p_uri in well_known_prefixes.items():
                #print(uri, p_uri)
                if self.uri_s.find(p_uri[0]) == 0:
                    return self.uri_s.replace(p_uri[0], p + ":")
            raise Exception("can't collapse prefix for well-known uri:", self.uri_s)
        
        return rdftf.collapse_prefix(self)


if 1:
    for k, v in well_known_prefixes.items():
        #print(k, v)
        prefixes = [x.replace("___", "_") for x in v[1]]
        WNP = namedtuple('WNP', prefixes)
        globals()[k] = WNP(*[URI(v[0] + x.replace("___", "")) for x in v[1]])

    
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

    def to_turtle(self, rdftf:"RDFTermFactory"):
        if self.datatype_uri == xsd.string:
            ret = f'"{self.value_o}"'
        elif self.datatype_uri == xsd.integer:
            ret = f"{self.value_o}"
        else:
            ret = '"' + f"{self.value_o}" + '"' + "^^" + self.datatype_uri.to_turtle(rdftf)
        return ret

    def as_python(self):
        ret = None
        if self.datatype_uri == xsd.string:
            ret = f"{self.value_o}"
        elif self.datatype_uri == xsd.integer:
            ret = int(self.value_o)
        elif self.datatype_uri == xsd.boolean:
            ret = self.value_o.lower() == "true"
        else:
            #ipdb.set_trace()
            raise Exception(f"unsupported xsd type: {self.datatype_uri}")

        return ret
    
class BNode:
    def __init__(self, s):
        self.bnode = s

    def __repr__(self):
        return f"{self.bnode}"

    def to_turtle(self, rdftf):
        ret = "_:" + self.bnode
        return ret
    
class RDFTermFactory:
    def __init__(self):            
        self.prefixes = {} # prefix:str -> prefix_uri:URI
        self.init_well_known_prefixes()
        
    def init_well_known_prefixes(self):
        for prefix, prefix_info in well_known_prefixes.items():
            prefix_uri_s, prefix_members = prefix_info
            self.prefixes[prefix] = URI(prefix_uri_s)
            
    def add_prefixes(self, rq_res):
        for prefix, prefix_uri_s in zip(rq_res['prefix'], rq_res['prefix_uri']):
            self.prefixes[prefix] = URI(prefix_uri_s)

    def restore_prefix(self, curie:str) -> URI:
        assert(type(curie) == str)
        for prefix, prefix_uri in self.prefixes.items():
            if curie.find(prefix + ":") == 0:
                return URI(curie.replace(prefix + ":", prefix_uri.uri_s))
        raise Exception("can't restore prefix in curie", curie)

    def collapse_prefix(self, uri:URI) -> str:
        assert(isinstance(uri, URI))
        for p, p_uri in self.prefixes.items():
            #print(uri, p_uri)
            if uri.uri_s.find(p_uri.uri_s) == 0:
                return uri.uri_s.replace(p_uri.uri_s, p + ":")
        raise Exception("can't collapse prefix for uri:", uri.uri_s)
    
    def make_rq(self, rq:str) -> str:
        #ipdb.set_trace()
        ret = "\n".join([f"prefix {prefix}: <{prefix_uri_s}>" for prefix, prefix_uri_s in self.prefixes.items()]) \
            + "\n" + rq
        return ret

    def handle_rq_select_result(self, rq_select_res):
        #ipdb.set_trace()
        results = rq_select_res
        res_d = {col:[] for col in results['head']['vars']}
        for row in results['results']['bindings']:
            for col in res_d.keys():
                res_d[col].append(None)
            for b_k, b_v in row.items():
                if b_v['type'] == 'literal':
                    #ipdb.set_trace()
                    if 'datatype' in b_v:
                        res_v = self.make_Literal(b_v['value'], self.make_URI_from_string(b_v['datatype']))
                    else:
                        res_v = self.make_Literal(b_v['value'], xsd.string)
                elif b_v['type'] == 'uri':
                    res_v = self.make_URI_from_string(b_v['value'])
                else:
                    raise Exception("unknown tag in sparql server response")
                res_d[b_k][-1] = res_v
        return res_d
    
    def make_URI_from_string(self, full_uri_s:str) -> URI:
        assert(isinstance(full_uri_s, str))
        return URI(full_uri_s)

    def make_URI_from_parts(self, prefix_part:URI, suffix_part:str) -> URI:
        assert(isinstance(prefix_part, URI))
        assert(isinstance(suffix_part, str))
        return URI(prefix_part.uri_s + suffix_part)

    @staticmethod
    def make_Literal(value_o, datatype_uri):
        return Literal(value_o, datatype_uri)

    @staticmethod
    def from_python_to_Literal(v):
        if type(v) == str:
            return RDFTermFactory.make_Literal(f'{v}', xsd.string)
        elif type(v) == bool:
            return RDFTermFactory.make_Literal("true" if v else "false", xsd.boolean)
        elif type(v) == int:
            return RDFTermFactory.make_Literal(f"{v}", xsd.integer)
        elif type(v) == float:
            return RDFTermFactory.make_Literal(f"{v}", xsd.float)

        raise Exception(f"from_python_to_Literal: unsupported type {type(v)}")
