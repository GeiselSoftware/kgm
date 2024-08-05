import urllib.request
import rdflib

ttl_file_url = 'http://h1:8001/kgm/sparql-example/ab.data.ttl'
with urllib.request.urlopen(ttl_file_url) as fd:
    g = rdflib.Graph()
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

    for row in g.query(rq): print([str(x) for x in row])
