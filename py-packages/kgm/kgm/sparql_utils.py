import ipdb
import io
import pandas as pd
import rdflib
from SPARQLWrapper import SPARQLWrapper, JSON, TURTLE
from SPARQLWrapper import POST, BASIC

known_prefixes = {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "sh": "http://www.w3.org/ns/shacl#",
    "kgm": "http://www.geisel-software.com/RDF/KGM#",
    "ab": "http://www.geisel-software.com/RDF/alice-bob#",
    "nw": "http://www.geisel-software.com/RDF/NorthWind#"
}

def restore_prefix(curie:str):
    for prefix, prefix_uri_s in known_prefixes.items():
        if curie.find(prefix) == 0:
            return rdflib.URIRef(curie.replace(prefix + ":", prefix_uri_s))
    raise Exception("can't restore prefix in curie", curie)

def make_rq(rq):
    return "\n".join([f"prefix {prefix}: <{prefix_uri_s}>" for prefix, prefix_uri_s in known_prefixes.items()]) + "\n" + rq

class uri:
    def __init__(self, s):
        self.uri = s
        
    def __repr__(self):
        return f"<{self.uri}>"

    def __eq__(self, o):
        return self.uri == o.uri
    def __hash__(self):
        return self.uri.__hash__()

    def collapse_prefix(self):
        for p, p_uri_s in known_prefixes.items():
            if self.uri.find(p_uri_s) == 0:
                return self.uri.replace(p_uri_s, p + ":")
        raise Exception("can't collapse prefix for URI:", self.uri)
    
class literal:
    def __init__(self, s):
        self.literal = s

    def __repr__(self):
        return f'"{self.literal}"'

    def __eq__(self, o):
        return self.literal == o.literal
    def __hash__(self):
        return o.__hash__()

class bnode:
    def __init__(self, s):
        self.bnode = s

    def __repr__(self):
        return f"{self.bnode}"
    
def to_rdfw(d):
    if d['type'] == 'uri':
        return uri(d['value']).collapse_prefix()
    if d['type'] == 'literal':
        return literal(d['value'])
    if d['type'] == 'bnode':
        return bnode(d['value'])
    raise Exception("unknown type")

def rq_insert_graph(g, graph_uri, *, config):
    # Serialize the graph to a string in N-Triples format
    ntriples_data = g.serialize(format="nt")#.decode("utf-8")
    
    if graph_uri:
        assert(type(graph_uri) == rdflib.URIRef)
        update_query = f"""
        INSERT DATA {{
        GRAPH <{graph_uri}> {{
        {ntriples_data}
        }}
        }}
        """
    else:
        update_query = f"""
        INSERT DATA {{
        {ntriples_data}
        }}
        """
            
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

def rq_select(rq, *, config):
    fuseki_query_url = config["backend-url"] + "/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query().convert()

    #ipdb.set_trace()
    return pd.DataFrame.from_records(results['results']['bindings'], columns = results['head']['vars']).map(to_rdfw)

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
    
