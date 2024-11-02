#import ipdb
import sys
import rdflib
import urllib
import pandas as pd
from ..config_utils import load_config
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update
from ..kgm_utils import *

def do_ls(w_config, path):
    print("do_ls:", path)
    query = make_rq("""
    select ?kgm_path ?g { ?g rdf:type kgm:Graph; kgm:path ?kgm_path } 
    """)
    #print(query)
    
    res = rq_select(query, config = w_config)
    print(res)

def do_new(w_config, path):
    print("do_graph_new:", path)

    graph_curie, _ = get_kgm_graph(w_config, path)
    if graph_curie != None:
        print(f"graph exists on path {path}, giving up, graph was {graph_curie}")
        return
    del graph_curie
    
    kgm_g_class_uri = get_kgm_graph_class_uri()
    graph_uri = create_kgm_graph(w_config, kgm_g_class_uri, path)
    print(f"created graph at path {path}: {graph_uri}")

def do_cat(w_config, path):
    graph_curie, _ = get_kgm_graph(w_config, path)
    if graph_curie is None:
        print(f"can't find graph at path {path}", file = sys.stderr)
        return

    graph_uri = restore_prefix(graph_curie)
    rq = make_rq(f"""
    construct {{ 
      ?s ?p ?o 
    }} where {{ 
       graph <{graph_uri}> {{ 
         ?s ?p ?o
       }} 
    }} order by ?s ?p ?o
    """)
    #print(rq)
    g = rq_construct(rq, config = w_config)
    #print(len(g))
    #print(type(g))

    if 0:
        print(g.serialize(format="ttl"))
    else:
        # this is other end of hack to insert bnodes as URIs with dummy: as prefix
        res_g = rdflib.Graph()
        for s, p, o in g:
            #print(s, p, o)
            if s.toPython().startswith("dummy:"):
                s = rdflib.BNode(s)
            if type(o) == rdflib.URIRef and o.toPython().startswith("dummy:"):
                o = rdflib.BNode(o)
            res_g.add((s, p, o))
        print(res_g.serialize(format="ttl"))
    
def do_import(w_config, path, ttl_file):
    print("do_import:", path, ttl_file)

    graph_curie, _ = get_kgm_graph(w_config, path)
    if graph_curie != None:
        print(f"graph at path {path} already exists:", graph_curie)
        return
    del graph_curie
    
    kgm_g_class_uri = get_kgm_graph_class_uri()
    graph_uri = create_kgm_graph(w_config, kgm_g_class_uri, path)
    
    # check do we really have empty dest graph
    rq = make_rq(f"select (count(?s) as ?c) {{ graph <{graph_uri}> {{ ?s ?p ?o }} }}")
    rq_res = rq_select(rq, config = w_config)
    if rq_res.iloc[0, 0].literal != "0":
        print(f"dest graph at path {path} is not empty, giving up, graph was {graph_curie}")
        return
    
    g = rdflib.Graph()    
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            g.parse(fd, format = "turtle")
    else:
        g.parse(ttl_file, format="turtle")

    #ipdb.set_trace()
    rq_insert_graph(g, graph_uri, config = w_config)

    print(path, graph_uri)
    
def do_remove(w_config, path):
    graph_uri, _ = get_kgm_graph(w_config, path)
    if graph_uri == None:
        print("can't find graph at path {path}")
        return
    
    rq_queries = [make_rq(f"drop graph {graph_uri}"),
                  make_rq(f'delete {{ ?s ?p ?o }} where {{ bind({graph_uri} as ?s) {{ ?s ?p ?o }} }}')]
        
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)

def do_copy(w_config, source_path, dest_path):
    print("do_copy:", source_path, dest_path)

    source_graph_curie, source_graph_props = get_kgm_graph(w_config, source_path)
    if source_graph_props == None:
        print(f"no graph at source path {source_path}")
        return

    dest_graph, _ = get_kgm_graph(w_config, dest_path)
    if dest_graph != None:
        print(f"there is a graph at dest path {dest_path}: {dest_graph_uri}, giving up")
        return    
    del dest_graph
    
    kgm_g_class_curie = source_graph_props["rdf:type"]
    kgm_g_class_uri = restore_prefix(kgm_g_class_curie)
    dest_graph_uri = create_kgm_graph(w_config, kgm_g_class_uri, dest_path)    
    rq_queries = [make_rq(f'insert {{ <{dest_graph_uri}> kgm:path "{dest_path}"; ?p ?o }} where {{ {source_graph_curie} ?p ?o filter(?p != kgm:path) }}'),
                  make_rq(f'copy {source_graph_curie} to <{dest_graph_uri}>')]
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)
    
    
def do_rename(w_config, path, new_path):
    print("do_rename:", path, new_path)

    graph_uri, _ = get_kgm_graph(w_config, path)
    if graph_uri == None:
        print("no graph at path {path}")
        return

    new_graph_uri, _ = get_kgm_graph(w_config, new_path)
    if new_graph_uri != None:
        print(f"there is a graph at new path {new_path}: {new_graph_uri}, giving up")
        return
    del new_graph_uri
    
    rq_queries = [make_rq(f'delete data {{ {graph_uri} kgm:path "{path}" }}'),
                  make_rq(f'insert data {{ {graph_uri} kgm:path "{new_path}" }}')]
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)

def do_show(w_config, curie):
    rq = make_rq(f"""
    select ?uo ?uo_member ?uo_member_value {{ 
      graph ?g
      {{ 
        bind({curie} as ?s_uo)
        ?uo ?uo_member ?uo_member_value .
        ?s_uo (<>|!<>)* ?uo .
      }}
    }}
    """)
    #print(rq)
    print(rq_select(rq, config = w_config))

def do_graph_select(w_config, select_query):
    query_text = make_rq(select_query)

    print("got query:")
    print(query_text)
    print("---")
    rq_res = rq_select(query_text, config = w_config)
    print(rq_res)

