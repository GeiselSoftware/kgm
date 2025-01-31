import ipdb
import io
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from SPARQLWrapper import POST, BASIC

from .rdf_utils import *
from .rdf_terms import URI

def make_rq__(prefixes, rq):
    #ipdb.set_trace()
    ret = "\n".join([f"prefix {prefix}: <{prefix_uri}>" for prefix, prefix_uri in prefixes.items()]) + "\n" + rq
    return ret

# returns dict var => list of URI/BNode/Literal
def rq_select__(prefixes, rq, *, config):
    rq = make_rq__(prefixes, rq)    
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query().convert()

    #ipdb.set_trace()
    res_d = {col:[] for col in results['head']['vars']}
    for row in results['results']['bindings']:
        for col in res_d.keys():
            res_d[col].append(None)
        for b_k, b_v in row.items():
            if b_v['type'] == 'literal':
                res_v = from_python_to_Literal(b_v['value'])
            elif b_v['type'] == 'uri':
                res_v = URI(b_v['value'])
            else:
                raise Exception("unknown tag in sparql server response")
            res_d[b_k][-1] = res_v
    return res_d

def rq_construct__(prefixes, rq, *, config):
    rq = make_rq__(prefixes, rq)
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(TURTLE)

    results = sparql.query().convert()
    g = rdflib.Graph()
    g.parse(io.BytesIO(results))

    return g

def rq_update__(prefixes, rq, *, config):
    rq = make_rq__(prefixes, rq)
    fuseki_query_url = config["backend-url"] + "/update"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setMethod("POST");
    #sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query()

    return results
