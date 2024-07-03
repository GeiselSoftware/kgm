#!/usr/bin/env python3

import sys
#sys.dont_write_bytecode = True

#import ipdb
import argparse
import pandas as pd
import rdflib
import uuid

from kgm.sparql_utils import rq_select, rq_insert_graph, rq_update, to_rdfw, kgm_prefix

def create_uri(rdfs_class):
    uri_s = rdfs_class + "##" + str(uuid.uuid4())
    return rdflib.URIRef(uri_s)
    
def do_upload_graph(args):
    turtle_file_path = args.ttl_file
    kgm_path = args.kgm_path
    add_f = args.add
    #ipdb.set_trace()

    g = rdflib.Graph()
    g.parse(turtle_file_path, format="turtle")
    
    rq_res = rq_select(f'prefix kgm: <kgm:> select ?s where {{ ?s kgm:path "{kgm_path}" }}')
    print(rq_res)
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

    descr_g = rdflib.Graph()
    descr_g.add((graph_uri, rdflib.URIRef("kgm:path"), rdflib.Literal(kgm_path)))

    rq_insert_graph(descr_g, None)
    rq_insert_graph(g, graph_uri)

    print(kgm_path, graph_uri)
    
def do_remove_kgm_graph(args):
    kgm_graph_uri = args.kgm_graph_uri
    rq_queries = [f"drop graph <{kgm_graph_uri}>",
                  f'delete {{ ?s ?p ?o }} where {{ bind(<{kgm_graph_uri}> as ?s) {{ ?s ?p ?o }} }}']
        
    for rq in rq_queries:
        print(rq)
        rq_update(rq)
    
def do_ls_kgm_graphs(args):
    print("args:", args)

    query = """
    PREFIX kgm: <kgm:>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?kgm_path ?graph_uri { ?graph_uri kgm:path ?kgm_path } 
    """.replace("%kgm_prefix%", kgm_prefix)
    #print(query)
    
    res = rq_select(query)
    print(pd.DataFrame.from_dict(res['results']['bindings']).map(to_rdfw).to_string(index = False))

def do_ls_all_graphs(args):
    print("args:", args)

    # SPARQL query to run
    query = """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>    
    select ?g (count(*) as ?count) { 
     { bind(rdf:nil as ?g) ?s ?p ?o } union { graph ?g {?s ?p ?o} }
    } 
    group by ?g
    """

    res = rq_select(query)
    print(pd.DataFrame.from_dict(res['results']['bindings']).map(to_rdfw))

def main():
    parser = argparse.ArgumentParser(description="Command processor example")
    subparsers = parser.add_subparsers(title="subcommands") #, description="valid subcommands") #, help="sub-command help")

    if 0:
        subcommand_config = subparsers.add_parser("config", help = "configure graph store explorer")
        subcommand_config_parsers = subcommand_config.add_subparsers()
        subcommand_config_show = subcommand_config_parsers.add_parser("show", help = "shows current config")
        subcommand_config_show.set_defaults(func = do_config_show)
        subcommand_config_set = subcommand_config_parsers.add_parser("set", help = "set specified config_value")
        subcommand_config_set_config_set.add_argument("--key", required = True, help = "key")
        subcommand_config_set.add_argument("--value", required = True, help = "value")
        subcommand_config_set.set_defaults(func = do_config_set)

    if 1:    
        subcommand_graph = subparsers.add_parser("graph", help = "graph commands")
        subcommand_graph_parsers = subcommand_graph.add_subparsers()
        if 1:
            subcommand_show = subcommand_graph_parsers.add_parser("show", help = "shows kgm graphs")
            subcommand_show.set_defaults(func = do_ls_all_graphs)
        if 1:
            subcommand_upload = subcommand_graph_parsers.add_parser("upload", help = "uploads ttl file")
            subcommand_upload.add_argument("--kgm-path", type=str, required = True, help = "destination kgm graph path")
            subcommand_upload.add_argument("--ttl-file", type=str, required = True, help = "data file")
            subcommand_upload.add_argument("--add", action = 'store_true', required = False, help = "add triples if graph exists")
            subcommand_upload.set_defaults(func = do_upload_graph)            
        if 1:
            subcommand_remove = subcommand_graph_parsers.add_parser("remove", help = "remove kgm graph")
            subcommand_remove.add_argument("--kgm-graph-uri", type=str, required = True, help = "remove KGM graph")
            subcommand_remove.set_defaults(func = do_remove_kgm_graph)
            
    if 0:
        subcommand_remove = subparsers.add_parser("remove", help = "remote kgm graph")
        subcommand_remove.add_argument("--kgm-path", type=str, required = True, help = "kgm graph to remove")
        subcommand_remove.set_defaults(func = do_remove_kgm_graph)

    if 1:
        subcommand_ls = subparsers.add_parser("ls", help = "provides list of all kgm graphs")
        subcommand_ls.set_defaults(func = do_ls_kgm_graphs)
        
    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()
        
if __name__ == "__main__":
    main()
    
