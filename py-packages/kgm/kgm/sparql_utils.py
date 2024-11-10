#import ipdb
import io
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from SPARQLWrapper import POST, BASIC

#from .known_prefixes import *
from .rdf_utils import *

def make_rq(rq):
    return "\n".join([f"prefix {prefix}: <{prefix_uri.uri}>" for prefix, prefix_uri in known_prefixes.items()]) + "\n" + rq

def to_rdfw(d):
    if pd.isnull(d):
        return None
    if d['type'] == 'uri':
        return URI(d['value'])
    if d['type'] == 'literal':
        if not 'datatype' in d:
            datatype = xsd.string
        else:
            datatype = URI(d['datatype'])
        return Literal(d['value'], datatype)
    if d['type'] == 'bnode':
        return BNode(d['value'])
    raise Exception("unknown type")

def rq_insert_graph(triples, graph_uri, *, config):
    # Serialize the graph to a string in N-Triples format
    ntriples_data = []
    for t in triples:
        ntriples_data.append(f"{t[0].as_turtle()} {t[1].as_turtle()} {t[2].as_turtle()} .")
        
    ntriples_data_s = "\n".join(ntriples_data)
    if graph_uri:
        assert(type(graph_uri) == URI)
        update_query = make_rq(f"""
        INSERT DATA {{
        GRAPH <{graph_uri.uri}> {{
        {ntriples_data_s}
        }}
        }}
        """)
    else:
        update_query = make_rq(f"""
        INSERT DATA {{
        {ntriples_data_s}
        }}
        """)

    #ipdb.set_trace()
    # Create a SPARQLWrapper instance
    fuseki_update_url = config["backend-url"] + "/update"
    sparql = SPARQLWrapper(fuseki_update_url)
    #sparql.setHTTPAuth(BASIC)
    #sparql.setCredentials("username", "password")  # Replace with your Fuseki credentials if necessary
    
    # Set the query and the request method
    sparql.setQuery(update_query)
    sparql.setMethod(POST)
    
    # Execute the query
    response = sparql.query()
    
    # Check the response status
    if response.response.status != 200:
        raise Exception(f"Failed to insert data. Status code: {response.response.status}")

# returns dict var => list of URI/BNode/Literal
def rq_select(rq, *, config):
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
            res_d[b_k][-1] = to_rdfw(b_v)
    return res_d

def rq_construct(rq, *, config):
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(TURTLE)

    results = sparql.query().convert()
    g = rdflib.Graph()
    g.parse(io.BytesIO(results))
            
    return g

def rq_update(rq, *, config):
    fuseki_query_url = config["backend-url"] + "/update"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setMethod("POST");
    #sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query()

    return results
    
