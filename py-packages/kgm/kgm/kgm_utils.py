import rdflib
from .sparql_utils import *

def get_graph_uri(w_config, path):
    rq = make_rq(f"""
    select ?s where {{ 
      #?s rdf:type/rdfs:subClassOf kgm:Graph; 
      ?s rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGraph) .
      ?s kgm:path "{path}"
    }}
    """)
    #print(rq)

    rq_res = rq_select(rq, config = w_config)
    #print(rq_res)
    if len(rq_res["results"]["bindings"]) == 1:
        graph_uri = rdflib.URIRef(rq_res["results"]["bindings"][0]["s"]["value"])
    elif len(rq_res["results"]["bindings"]) == 0:
        graph_uri = None
    else:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")
    
    return graph_uri


