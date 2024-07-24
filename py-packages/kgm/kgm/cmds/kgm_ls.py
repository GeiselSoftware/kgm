import pandas as pd
from ..sparql_utils import rq_select, rq_insert_graph, rq_update, to_rdfw, kgm_prefix

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
