from collections import namedtuple
from .rdf_terms import URI

well_known_prefixes = {}; well_known_prefix_members = {}
well_known_prefixes["kgm:"] = "urn:kgm:"
well_known_prefix_members["kgm:"] = ["Graph", "path"]
well_known_prefixes["rdf:"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
well_known_prefix_members["rdf:"] = ["type"]
well_known_prefixes["rdfs:"] = "http://www.w3.org/2000/01/rdf-schema#"
well_known_prefix_members["rdfs:"] = ["Class"]
well_known_prefixes["xsd:"] = "http://www.w3.org/2001/XMLSchema#"
well_known_prefix_members["xsd:"] = ["string", "boolean", "integer", "float", "double"]
well_known_prefixes["sh:"] = "http://www.w3.org/ns/shacl#"
well_known_prefix_members["sh:"] = ["property", "path", "datatype", "class___", "minCount", "maxCount", "NodeShape"]
well_known_prefixes["dash:"] = "http://datashapes.org/dash#"
well_known_prefix_members["dash:"] =  ["closedByType"]

if 1:
    for prefix, prefix_uri in well_known_prefixes.items():
        #print(k, v)
        members = well_known_prefix_members[prefix]
        WNP = namedtuple('WNP', [x.replace("___", "_") for x in members])
        globals()[prefix[:-1]] = WNP(*[URI(prefix_uri + x.replace("___", "")) for x in members])
