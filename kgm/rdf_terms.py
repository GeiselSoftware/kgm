import ipdb
from collections import namedtuple

well_known_prefixes = {
    "rdf": ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", ["type"]),
    "rdfs": ("http://www.w3.org/2000/01/rdf-schema#", ["Class"]),
    "xsd": ("http://www.w3.org/2001/XMLSchema#", ["string", "boolean", "integer", "float", "double"]),
    "sh": ("http://www.w3.org/ns/shacl#", ["property", "path", "datatype", "class___", "minCount", "maxCount", "NodeShape"]),
    "dash": ("http://datashapes.org/dash#", ["closedByType"]),
    "kgm": ("http://www.geisel-software.com/kgm/kgm#", ["Graph", "path"])
}

class URI:
    def __init__(self, rdftf: "RDFTermFactory", uri_s:str):
        # NOTE that rdftf can be None only for well known prefixes
        assert(type(uri_s) == str)
        assert(len(uri_s) > 2 and uri_s[0] != "<" and uri_s[-1] != ">")
        self.rdftf = rdftf
        self.uri_s = uri_s
        
    def __repr__(self):
        return self.uri_s
        
    def __eq__(self, o):
        assert(type(o) == URI)
        return self.uri_s == o.uri_s

    def __hash__(self):
        return self.uri_s.__hash__()

    def to_turtle(self) -> str:
        if self.rdftf is None:
            for p, p_uri in well_known_prefixes.items():
                #print(uri, p_uri)
                if self.uri_s.find(p_uri[0]) == 0:
                    return self.uri_s.replace(p_uri[0], p + ":")
            raise Exception("can't collapse prefix for well-known uri:", self.uri_s)
        
        return self.rdftf.collapse_prefix(self)


if 1:
    for k, v in well_known_prefixes.items():
        #print(k, v)
        prefixes = [x.replace("___", "_") for x in v[1]]
        WNP = namedtuple('WNP', prefixes)
        globals()[k] = WNP(*[URI(None, v[0] + x.replace("___", "")) for x in v[1]])

    
class Literal:
    def __init__(self, rdftf: "RDFTermFactory", value_o, datatype_uri):
        assert(rdftf is not None)
        assert(type(datatype_uri) == URI)
        self.rdftf = rdftf
        self.value_o = value_o
        self.datatype_uri = datatype_uri
        
    def __repr__(self):
        return f"{self.value_o}"

    def __eq__(self, o):
        assert(type(o) == Literal)
        return self.value_o == o.value_o
    
    def __hash__(self):
        return self.value_o.__hash__()    

    def to_turtle(self):
        xsd_string = self.rdftf.restore_prefix("xsd:string")
        xsd_integer = self.rdftf.restore_prefix("xsd:integer")
        if self.datatype_uri == xsd_string:
            ret = f'"{self.value_o}"'
        elif self.datatype_uri == xsd_integer:
            ret = f"{self.value_o}"
        else:
            ret = '"' + f"{self.value_o}" + '"' + "^^" + self.datatype_uri.to_turtle()
        return ret

    def as_python(self):
        xsd_string = self.rdftf.restore_prefix("xsd:string")
        xsd_boolean = self.rdftf.restore_prefix("xsd:boolean")
        xsd_integer = self.rdftf.restore_prefix("xsd:integer")        
        ret = None
        if self.datatype_uri == xsd_string:
            ret = f"{self.value_o}"
        elif self.datatype_uri == xsd_integer:
            ret = int(self.value_o)
        elif self.datatype_uri == xsd_boolean:
            ret = self.value_o.lower() == "true"
        else:
            #ipdb.set_trace()
            raise Exception(f"unsupported xsd type: {self.datatype.to_turtle()}")

        return ret
    
class BNode:
    def __init__(self, s):
        self.bnode = s

    def __repr__(self):
        return f"{self.bnode}"

    def to_turtle(self):
        ret = "_:" + self.bnode
        return ret
    
class RDFTermFactory:
    def __init__(self):            
        self.prefixes = {} # prefix:str -> prefix_uri:URI
        self.init_well_known_prefixes()
        
    def init_well_known_prefixes(self):
        for prefix, prefix_info in well_known_prefixes.items():
            prefix_uri_s, prefix_members = prefix_info
            self.prefixes[prefix] = URI(self, prefix_uri_s)

            
    def add_prefixes(self, rq_res):
        for prefix, prefix_uri_s in zip(rq_res['prefix'], rq_res['prefix_uri']):
            self.prefixes[prefix] = URI(self, prefix_uri_s)

    def restore_prefix(self, curie:str) -> URI:
        assert(type(curie) == str)
        for prefix, prefix_uri in self.prefixes.items():
            if curie.find(prefix + ":") == 0:
                return URI(self, curie.replace(prefix + ":", prefix_uri.uri_s))
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
                        xsd_string = self.restore_prefix("xsd:string")
                        res_v = self.make_Literal(b_v['value'], xsd_string)
                elif b_v['type'] == 'uri':
                    res_v = self.make_URI_from_string(b_v['value'])
                else:
                    raise Exception("unknown tag in sparql server response")
                res_d[b_k][-1] = res_v
        return res_d
    
    def make_URI_from_string(self, full_uri_s:str) -> URI:
        assert(isinstance(full_uri_s, str))
        return URI(self, full_uri_s)

    def make_URI_from_parts(self, prefix_part:URI, suffix_part:str) -> URI:
        assert(isinstance(prefix_part, URI))
        assert(isinstance(suffix_part, str))
        return URI(self, prefix_part.uri_s + suffix_part)
    
    def make_Literal(self, value_o, datatype_uri):
        return Literal(self, value_o, datatype_uri)

    def from_python_to_Literal(self, v):
        xsd_string = self.restore_prefix("xsd:string")
        xsd_boolean = self.restore_prefix("xsd:boolean")
        xsd_integer = self.restore_prefix("xsd:integer")
        if type(v) == str:
            return self.make_Literal(f'{v}', xsd_string)
        elif type(v) == bool:
            return self.make_Literal("true" if v else "false", xsd_boolean)
        elif type(v) == int:
            return self.make_Literal(f"{v}", xsd_integer)

        raise Exception(f"from_python_to_Literal: unsupported type {typeof(v)}")
