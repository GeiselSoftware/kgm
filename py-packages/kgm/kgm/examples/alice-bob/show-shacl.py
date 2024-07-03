#import ipdb
import sys
sys.dont_write_bytecode = True

import rdflib
import graphviz_utils

if __name__ == "__main__":
    #init_bindings = {}
    init_bindings = {'s': rdflib.URIRef("ab:alice")}
        
    ttl_files = ["./ab.shacl.ttl", "./ab.ttl"]
    #ttl_files = ttl_files[:-1]
    g = rdflib.Graph()
    for ttl_file in ttl_files:
        print(ttl_file, file = sys.stderr)
        g.parse(ttl_file)

    ng = g.query("""
    prefix ab: <ab:>
    construct {
      #?st rdf:type rdfs:Class.
      ?st ?dm_name_uri ?dm_t_s.
      ?st ?cm_name_uri ?cm_t; ?cm_name_uri ?cm_t_s .
      ?s rdf:type ?sst . ?o rdf:type ?ot .
      ?s ?p ?o. ?o ?pp ?oo
    } where { 
      ?st rdf:type rdfs:Class .
      optional {?st sh:property [sh:path ?dm_name_uri; sh:dataclass ?dm_t] bind (str(?dm_t) as ?dm_t_s)}
      optional {?st sh:property [sh:path ?cm_name_uri; sh:class ?cm_t] bind (str(?cm_t) as ?cm_t_s)}
      optional {?s rdf:type ?sst .
      ?s ?p ?o . ?o ?pp ?oo filter(?pp not in (sh:property, rdf:type)) . ?o rdf:type ?ot }
    }
    """, initBindings = init_bindings)

    graphviz_utils.generate_png(ng.graph, "graph.png")
    
