import urllib.request
import rdflib

# to quickly look at content: wget -q -O - http://h1:8001/kgm/sparql-example/ab.data.ttl

ttl_file_url = 'http://h1:8001/kgm/sparql-example/ab.data.ttl'
with urllib.request.urlopen(ttl_file_url) as fd:
    g = rdflib.Graph()
    print("loading triples from", ttl_file_url)
    g.parse(fd, format = "turtle")

    rq = """
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix ab: <ab:>

    select ?pet_name ?owner_name ?pet_class
    where {
      ?pet rdf:type ?pet_class;
           ab:name ?pet_name;
           ab:ownedBy ?owner.
      ?owner ab:name ?owner_name.
    }
    """
    print(f"query on {len(g)} triples")
    print(rq)
    
    rq_res = g.query(rq)
    print([str(x) for x in rq_res.vars])
    print("=========")
    for row in rq_res:
        print([str(x) for x in row])
    print(".")
    
