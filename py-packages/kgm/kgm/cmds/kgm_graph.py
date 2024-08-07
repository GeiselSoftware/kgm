#import ipdb
import uuid
import rdflib
import urllib
import pandas as pd
from ..config_utils import load_config
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update, to_rdfw, kgm_prefix
from ..kgm_utils import get_graph_uri

def do_ls(w_config, path):
    print("do_ls:", path)
    query = make_rq("""
    select ?kgm_path ?g { ?g rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGraph). ?g kgm:path ?kgm_path } 
    """)
    #print(query)
    
    res = rq_select(query, config = w_config)
    print(pd.DataFrame.from_dict(res['results']['bindings']).map(to_rdfw).to_string(index = False))

def create_uri(rdfs_class: rdflib.URIRef) -> rdflib.URIRef:
    uri_s = rdfs_class.toPython() + "--" + str(uuid.uuid4())
    return rdflib.URIRef(uri_s)
    
def do_new(w_config, kgm_graph_type, path):
    print("do_graph_new:", kgm_graph_type, path)

    graph_uri = get_graph_uri(w_config, path)
    if graph_uri != None:
        print(f"graph exists on path {path}, giving up: {graph_uri}")
        return

    #create_kgm_graph(w_config, kgm_graph_type, path)
    kgm_g_class = None
    if kgm_graph_type == "data":
        kgm_g_class = rdflib.URIRef("http://www.geisel-software.com/RDF/KGM#DataGraph")
    elif kgm_graph_type == "shacl":
        kgm_g_class = rdflib.URIRef("http://www.geisel-software.com/RDF/KGM#SHACLGraph")
    else:
        raise Exception(f"unexpected value of graph-type: {kgm_graph_type}")
    
    descr_g = rdflib.Graph()
    graph_uri = create_uri(kgm_g_class)
    descr_g.add((graph_uri, rdflib.RDF.type, kgm_g_class))
    descr_g.add((graph_uri, rdflib.URIRef("http://www.geisel-software.com/RDF/KGM#path"), rdflib.Literal(path)))

    rq_insert_graph(descr_g, None, config = w_config)
    print(f"created graph at path {path}: {graph_uri}")
    
def do_append(w_config, path, ttl_file):
    print("do_append:", path, ttl_file)

    graph_uri = get_graph_uri(w_config, path)
    if graph_uri == None:
        print("no graph at path {path}")
        return

    g = rdflib.Graph()    
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            g.parse(fd, format = "turtle")
    else:
        g.parse(ttl_file, format="turtle")

    rq_insert_graph(g, graph_uri, config = w_config)

    print(path, graph_uri)
    
def do_remove(w_config, path):
    graph_uri = get_graph_uri(w_config, path)
    if graph_uri == None:
        print("can't find graph at path {path}")
        return
    
    rq_queries = [f"drop graph <{graph_uri}>",
                  f'delete {{ ?s ?p ?o }} where {{ bind(<{graph_uri}> as ?s) {{ ?s ?p ?o }} }}']
        
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)

def do_copy(w_config, source_path, dest_path):
    print("do_copy:", source_path, dest_path)

    source_graph_uri = get_graph_uri(w_config, source_path)
    if source_graph_uri == None:
        print("no graph at source path {source_path}")
        return

    dest_graph_uri = get_graph_uri(w_config, dest_path)
    if dest_graph_uri != None:
        print(f"there is a graph at dest path {dest_path}: {dest_graph_uri}, giving up")
        return    

def do_rename(w_config, path, new_path):
    print("do_rename:", path, new_path)

    graph_uri = get_graph_uri(w_config, path)
    if graph_uri == None:
        print("no graph at path {path}")
        return

    new_graph_uri = get_graph_uri(w_config, new_path)
    if new_graph_uri != None:
        print(f"there is a graph at new path {new_path}: {new_graph_uri}, giving up")
        return

        
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
