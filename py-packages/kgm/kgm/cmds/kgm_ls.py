import pandas as pd
from ..sparql_utils import make_rq_select, rq_select, to_rdfw

def do_ls_kgm_graphs(kgm_path):
    query = make_rq_select("""
    PREFIX kgm: <kgm:>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    select ?kgm_path ?g { ?g rdf:type ?gt filter(?gt = kgm:DataGraph || ?gt = kgm:SHACLGrpah). ?g kgm:path ?kgm_path } 
    """)
    #print(query)
    
    res = rq_select(query)
    print(pd.DataFrame.from_dict(res['results']['bindings']).map(to_rdfw).to_string(index = False))

def do_ls_all_graphs():
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
