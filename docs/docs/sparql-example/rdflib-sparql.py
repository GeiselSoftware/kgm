import urllib.request
import rdflib

# to quickly look at content: wget -q -O - http://h1:8001/kgm/sparql-example/ab-small.ttl

ttl_file_url = 'http://h1:8001/kgm/sparql-example/ab-small.ttl'
with urllib.request.urlopen(ttl_file_url) as fd:
    g = rdflib.Graph()
    g.parse(fd, format = "turtle")
    print("loaded", len(g), "triples")

    rq = """
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix ab: <ab:>

    select ?owner_name ?pet_name ?pet_class
    where {
      ?pet rdf:type ?pet_class .
      ?pet ab:name ?pet_name .
      ?pet ab:ownedBy ?owner .
      ?owner ab:name ?owner_name .
    }
    """

    rq_res = g.query(rq)
    for row in rq_res:
        print([str(x) for x in row])

