#import ipdb
import uuid
from .sparql_utils import *

def create_uri(rdfs_class: URI) -> URI:
    return URI(rdfs_class.as_turtle() + "--" + str(uuid.uuid4()))
        
def create_kgm_graph(w_config, path):
    descr_g = []
    graph_uri = create_uri(kgm.Graph)
    descr_g.append((graph_uri, rdf.type, RDFObject(kgm.Graph)))
    descr_g.append((graph_uri, kgm.path, RDFObject(Literal(path, xsd.string))))

    rq_insert_graph(descr_g, None, config = w_config)
    return graph_uri

# returns uri on kgm path
def get_kgm_graph(w_config, path):
    rq = make_rq(f'select ?s ?p ?o where {{ ?s kgm:path "{path}"; rdf:type kgm:Graph }}')
    #print(rq)

    rq_res = rq_select(rq, config = w_config)
    graph_uris = rq_res['s']
    #ipdb.set_trace()
    #print(rq_res)
    if len(graph_uris) > 1:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")
    
    return None if len(graph_uris) == 0 else graph_uris[0]



