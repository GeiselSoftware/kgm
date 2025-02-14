import ipdb
import io
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from SPARQLWrapper import POST, BASIC

from .prefixes import xsd
from .rdf_terms import URI
from .rdf_utils import make_rq, to_turtle, make_Literal, make_URI_from_string

# returns dict var => list of URI/BNode/Literal
def rq_select(rq, *, config, w_prefixes):
    #ipdb.set_trace()
    rq = make_rq(rq, w_prefixes)
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query().convert()
    return results

def rq_construct(rq, *, config, w_prefixes):
    rq = make_rq(rq, w_prefixes)
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(TURTLE)

    results = sparql.query().convert()
    g = rdflib.Graph()
    g.parse(io.BytesIO(results))

    return g

def rq_update(rq, *, config, w_prefixes):
    rq = make_rq(rq, w_prefixes)
    fuseki_update_url = config["backend-url"] + "/update"
    sparql = SPARQLWrapper(fuseki_update_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setMethod("POST");
    #sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query()

    return results

def rq_handle_select_result(rq_select_res, w_prefixes):
    #ipdb.set_trace()
    results = rq_select_res
    res_d = {col:[] for col in results['head']['vars']}
    for row in results['results']['bindings']:
        for col in res_d.keys():
            res_d[col].append(None)
        for b_k, b_v in row.items():
            if b_v['type'] == 'literal':
                #ipdb.set_trace()
                if 'datatype' in b_v:
                    res_v = make_Literal(b_v['value'], make_URI_from_string(b_v['datatype']))
                else:
                    res_v = make_Literal(b_v['value'], xsd.string)
            elif b_v['type'] == 'uri':
                res_v = make_URI_from_string(b_v['value'])
            else:
                raise Exception("unknown tag in sparql server response")
            res_d[b_k][-1] = res_v
    return res_d

def rq_delete_insert(graph_uri:URI, dels_inss, *, config, w_prefixes):
    if len(dels_inss[0]) == 0 and len(dels_inss[1]) == 0:
        return None

    rq = io.StringIO()
    print(make_rq("", w_prefixes), file = rq)    
    for update_action, triples in zip(['delete', 'insert'], dels_inss):
        if len(triples) > 0:
            print(f"{update_action} {{", file = rq)
            if graph_uri is not None:
                print(f" graph {to_turtle(graph_uri, w_prefixes)} {{", file = rq)
            for t in triples:
                print(to_turtle(t, w_prefixes), file = rq)
            if graph_uri is not None:
                print(" }", file = rq)
            print("}", file = rq)
    print("where {}", file = rq)

    #ipdb.set_trace()
    print(rq.getvalue())

    rq_update(rq.getvalue(), config = config, w_prefixes = w_prefixes)
