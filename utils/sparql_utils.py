from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper, JSON
from SPARQLWrapper import POST, BASIC

gse_prefix = "https://www.geisel-software.com/RDFPrefix/#"
fuseki_url = "http://localhost:3030/gse"

class uri:
    def __init__(self, s):
        self.uri = s
        
    def __repr__(self):
        return f"<{self.uri}>"

class literal:
    def __init__(self, s):
        self.literal = s

    def __repr__(self):
        return self.literal

def to_rdfw(d):
    if d['type'] == 'uri':
        return uri(d['value'])
    if d['type'] == 'literal':
        return literal(d['value'])
    raise Exception("unknown type")

def rq_insert_graph(g, graph_uri):
    # Serialize the graph to a string in N-Triples format
    ntriples_data = g.serialize(format="nt")#.decode("utf-8")
    
    if graph_uri:
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
    fuseki_update_url = f"{fuseki_url}/update"
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

def rq_select(rq):
    fuseki_query_url = f"{fuseki_url}/query"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query().convert()

    return results

def rq_update(rq):
    fuseki_query_url = f"{fuseki_url}/update"
    sparql = SPARQLWrapper(fuseki_query_url)

    # Set the query and the return format
    sparql.setQuery(rq)
    sparql.setMethod("POST");
    #sparql.setReturnFormat(JSON)

    # Run the query and get the results
    results = sparql.query()

    return results
    

