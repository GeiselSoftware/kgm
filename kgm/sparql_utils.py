#import ipdb
import io
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from SPARQLWrapper import POST, BASIC

from .rdf_utils import *

def make_rq__(prefix_man, rq):
    #ipdb.set_trace()
    ret = "\n".join([f"prefix {prefix}: <{prefix_uri}>" for prefix, prefix_uri in prefix_man.prefixes.items()]) + "\n" + rq
    return ret

def to_rdfw__(prefix_man, d):
    if pd.isnull(d):
        return None
    if d['type'] == 'uri':
        return URI(prefix_man.collapse_prefix(d['value']))
    if d['type'] == 'literal':
        if not 'datatype' in d:
            datatype = xsd.string
        else:
            datatype = URI(prefix_man.collapse_prefix(d['datatype']))
        return Literal(d['value'], datatype)
    if d['type'] == 'bnode':
        return BNode(d['value'])
    raise Exception("unknown type")

# returns dict var => list of URI/BNode/Literal
def rq_select__(prefix_man, rq, *, config):
    rq = make_rq__(prefix_man, rq)    
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
            res_d[b_k][-1] = to_rdfw__(prefix_man, b_v)
    return res_d

def rq_construct__(prefix_man, rq, *, config):
    rq = make_rq__(prefix_man, rq)
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(TURTLE)

    results = sparql.query().convert()
    g = rdflib.Graph()
    g.parse(io.BytesIO(results))
            
    return g

def rq_update__(prefix_man, rq, *, config):
    rq = make_rq__(prefix_man, rq)
    fuseki_query_url = config["backend-url"] + "/update"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setMethod("POST");
    #sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query()

    return results

def rq_insert_graph(db, triples, graph_uri):
    # Serialize the graph to a string in N-Triples format
    ntriples_data = []
    #ipdb.set_trace()
    for t in triples:        
        ntriples_data.append(f"{t[0].as_turtle()} {t[1].as_turtle()} {t[2].as_turtle()} .")
        
    ntriples_data_s = "\n".join(ntriples_data)
    if graph_uri:
        assert(type(graph_uri) == URI)
        update_query = f"""
        INSERT DATA {{
        GRAPH {graph_uri.as_turtle()} {{
        {ntriples_data_s}
        }}
        }}
        """
    else:
        update_query = f"""
        INSERT DATA {{
        {ntriples_data_s}
        }}
        """

    db.rq_update(update_query)

def rq_delete_insert(db, kgm_path, dels_inss):
    if len(dels_inss[0]) == 0 and len(dels_inss[1]) == 0:
        return None

    delete_triples = [f"{t.subject.as_turtle()} {t.pred.as_turtle()} {t.object_.as_turtle()} ." for t in dels_inss[0]]
    insert_triples = [f"{t.subject.as_turtle()} {t.pred.as_turtle()} {t.object_.as_turtle()} ." for t in dels_inss[1]]
    
    rq = ""
    if len(delete_triples) > 0:
        delete_triples_s = '\n'.join(delete_triples)
        rq += f"delete {{ graph ?g {{ \n {delete_triples_s} \n }} }}\n"
    if len(insert_triples) > 0:
        insert_triples_s = '\n'.join(insert_triples)
        rq += f"insert {{ graph ?g {{ \n {insert_triples_s} \n }} }}\n"
    rq += f'where {{ ?g kgm:path "{kgm_path}" }}'

    print(rq)

    db.rq_update(rq)
    
