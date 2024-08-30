#import ipdb
import uuid
import rdflib
from .sparql_utils import *

def create_uri(rdfs_class: rdflib.URIRef) -> rdflib.URIRef:
    uri_s = rdfs_class.toPython() + "--" + str(uuid.uuid4())
    return rdflib.URIRef(uri_s)

def get_kgm_graph_class_uri():
    kgm_g_class_uri = rdflib.URIRef(known_prefixes["kgm"] + "Graph")
    return kgm_g_class_uri
        
def create_kgm_graph(w_config, kgm_g_class_uri, path):
    assert(type(kgm_g_class_uri) == rdflib.URIRef)
    graph_uri = create_uri(kgm_g_class_uri)
    descr_g = rdflib.Graph()
    descr_g.add((graph_uri, rdflib.RDF.type, kgm_g_class_uri))
    descr_g.add((graph_uri, rdflib.URIRef(known_prefixes["kgm"] + "path"), rdflib.Literal(path)))

    rq_insert_graph(descr_g, None, config = w_config)
    return graph_uri

# for give graph path will return tuple (graph_uri:string, {pred: obj}:dict(string, string))
# graph_uri - is kgm graph's curie,
# {pred: obj} - dict of graph's pred:obj pairs as found in kgm backend
def get_kgm_graph(w_config, path):
    rq = make_rq(f'select ?s ?p ?o where {{ ?s kgm:path "{path}"; ?p ?o }}')
    #print(rq)

    rq_res = rq_select(rq, config = w_config)
    graph_uris = rq_res.s.unique()
    #ipdb.set_trace()
    #print(rq_res)
    if len(graph_uris) > 1:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")
    
    return (None, None) if len(graph_uris) == 0 else (graph_uris[0], {r.iloc[0]:r.iloc[1] for _, r in rq_res.drop('s', axis = 1).iterrows()})



