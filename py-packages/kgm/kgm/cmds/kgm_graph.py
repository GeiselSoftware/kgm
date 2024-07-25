import ipdb
import uuid
import rdflib
import urllib
import pandas as pd
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update, to_rdfw, kgm_prefix

def create_uri(rdfs_class):
    uri_s = rdfs_class + "--" + str(uuid.uuid4())
    return rdflib.URIRef(uri_s)

def do_ls_kgm_graphs(kgm_path):
    query = make_rq("""
    PREFIX kgm: <kgm:>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?kgm_path ?g { ?g rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGraph). ?g kgm:path ?kgm_path } 
    """)
    #print(query)
    
    res = rq_select(query)
    print(pd.DataFrame.from_dict(res['results']['bindings']).map(to_rdfw).to_string(index = False))

def do_add_graph(ttl_file, kgm_path, kgm_graph_type, add_f):
    print("do_add_graph:", ttl_file, kgm_path, kgm_graph_type, add_f)

    g = rdflib.Graph()    
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            g.parse(fd, format = "turtle")
    else:
        g.parse(ttl_file, format="turtle")

    rq = make_rq(f"""
    select ?s where {{ 
      #?s rdf:type/rdfs:subClassOf kgm:Graph; 
      ?s rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGraph) .
      ?s kgm:path "{kgm_path}"
    }}
    """)
    #print(rq)
    rq_res = rq_select(rq)
    #print(rq_res)
    if len(rq_res["results"]["bindings"]) in [0, 1]:
        if len(rq_res["results"]["bindings"]) == 1:
            s_uri = rdflib.URIRef(rq_res["results"]["bindings"][0]["s"]["value"])
            if not add_f:
                print(f"graph exists on path {kgm_path}: {s_uri}")
                return
            graph_uri = s_uri
        else:
            graph_uri = create_uri("kgm:Graph")
    else:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

    kgm_g_class = None
    if kgm_graph_type == "data":
        kgm_g_class = rdflib.URIRef("kgm:DataGraph")
    elif kgm_graph_type == "shacl":
        kgm_g_class = rdflib.URIRef("kgm:SHACLGraph")
    else:
        raise Exception(f"unexpected value of graph-type: {kgm_graph_type}")
    
    ipdb.set_trace()
    descr_g = rdflib.Graph()
    graph_uri = create_uri(kgm_g_class)
    descr_g.add((graph_uri, rdflib.RDF.type, kgm_g_class))
    descr_g.add((graph_uri, rdflib.URIRef("kgm:path"), rdflib.Literal(kgm_path)))

    rq_insert_graph(descr_g, None)
    rq_insert_graph(g, graph_uri)

    print(kgm_path, graph_uri)
    
def do_remove_graph(kgm_path):
    rq = make_rq(f'select ?g {{ ?g kgm:path "{kgm_path}" }}')
    print(rq)
    rq_res = rq_select(rq)
    print(rq_res)
    kgm_graph_uri = rdflib.URIRef(rq_res["results"]["bindings"][0]["g"]["value"])
    rq_queries = [f"drop graph <{kgm_graph_uri}>",
                  f'delete {{ ?s ?p ?o }} where {{ bind(<{kgm_graph_uri}> as ?s) {{ ?s ?p ?o }} }}']
        
    for rq in rq_queries:
        print(rq)
        rq_update(rq)

def do_graph_replace(kgm_path, ttl_file):
    ipdb.set_trace()
    rq = make_rq(f"""
    select ?s where {{ 
      #?s rdf:type/rdfs:subClassOf kgm:Graph; 
      ?s rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGraph) .
      ?s kgm:path "{kgm_path}"
    }}
    """)
    #print(rq)
    rq_res = rq_select(rq)
    #print(rq_res)
    if len(rq_res["results"]["bindings"]) in [0, 1]:
        if len(rq_res["results"]["bindings"]) == 1:
            g_uri = rdflib.URIRef(rq_res["results"]["bindings"][0]["s"]["value"])
        else:
            raise Exception(f"no graph found at {kgm_path}")
    else:
        raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

    g = rdflib.Graph()    
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            g.parse(fd, format = "turtle")
    else:
        g.parse(ttl_file, format="turtle")
    
    rq_update(f"clear graph <{g_uri}>")
    rq_insert_graph(g, g_uri)
        
def do_graph_select(select_query, select_query_file):
    if select_query is None:
        with open(select_query_file) as fd:
            query_text = fd.read()
    else:
        query_text = make_rq(select_query)

    print("got query:")
    print(query_text)
    print("---")
    rq_res = rq_select(query_text)
    print(rq_res)
