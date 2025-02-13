from collections import namedtuple
from .rdf_terms import URI

well_known_prefixes = {
    "rdf:": ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", ["type"]),
    "rdfs:": ("http://www.w3.org/2000/01/rdf-schema#", ["Class"]),
    "xsd:": ("http://www.w3.org/2001/XMLSchema#", ["string", "boolean", "integer", "float", "double"]),
    "sh:": ("http://www.w3.org/ns/shacl#", ["property", "path", "datatype", "class___", "minCount", "maxCount", "NodeShape"]),
    "dash:": ("http://datashapes.org/dash#", ["closedByType"]),
    "kgm:": ("urn:kgm:", ["Graph", "path"])
}

if 1:
    for k, v in well_known_prefixes.items():
        #print(k, v)
        prefixes = [x.replace("___", "_") for x in v[1]]
        WNP = namedtuple('WNP', prefixes)
        globals()[k[:-1]] = WNP(*[URI(v[0] + x.replace("___", "")) for x in v[1]])
