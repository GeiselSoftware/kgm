#import ipdb
import sys
sys.dont_write_bytecode = True

import rdflib
import graphviz_utils

rq_show_objects = """
    prefix ab: <ab:>
    construct {
      ?s0 ?p0 ?o0 .
      ?o0 ?p ?o .
    } where { 
      ?s0 ?p0 ?o0.
      ?s0 rdf:type [ rdf:type rdfs:Class ]. ?o0 rdf:type [ rdf:type rdfs:Class ].
      optional {?o0 ?p ?o . ?s rdf:type [ rdf:type rdfs:Class ]. ?o rdf:type [ rdf:type rdfs:Class ]. }
    }
"""

rq_show_objects_w_details = """
    prefix ab: <ab:>
    construct {
      ?s0 ?p0 ?o0 .
      ?o0 ?p ?o .

      ?s0_type ?dm_name_uri ?dm_t_s .
      ?s0_type ?cm_name_uri ?cm_t; ?cm_name_uri ?cm_t_s .
    } where {
      ?s0 ?p0 ?o0.
      ?s0 rdf:type ?s0_type. ?s0_type rdf:type rdfs:Class. 
      ?o0 rdf:type ?o0_type. ?o0_type rdf:type rdfs:Class.

      optional {?s0_type sh:property [sh:path ?dm_name_uri; sh:dataclass ?dm_t] bind (str(?dm_t) as ?dm_t_s)}
      optional {?s0_type sh:property [sh:path ?cm_name_uri; sh:class ?cm_t] bind (str(?cm_t) as ?cm_t_s)}

      optional {?o0 ?p ?o . ?s rdf:type [ rdf:type rdfs:Class ]. ?o rdf:type [ rdf:type rdfs:Class ]. }
    }
"""

if __name__ == "__main__":
    #init_bindings = {}
    init_bindings = {'s0': rdflib.URIRef("ab:alice")}
        
    ttl_files = ["./ab.shacl.ttl", "./ab.ttl"]
    #ttl_files = ttl_files[:-1]
    g = rdflib.Graph()
    for ttl_file in ttl_files:
        print(ttl_file, file = sys.stderr)
        g.parse(ttl_file)

    #ng = g.query(rq_show_objects, initBindings = init_bindings)
    ng = g.query(rq_show_objects_w_details, initBindings = init_bindings)

    graphviz_utils.generate_png(ng.graph, "t.png")
