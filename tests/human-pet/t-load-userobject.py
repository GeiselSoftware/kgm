import ipdb
from kgm import Database, KGMGraph, URI

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    g_uris = db.get_graph_uris(["/human-pet", "/human-pet.shacl"])
    g = KGMGraph(db, None, g_uris)

    ipdb.set_trace()
    obj_uris = g.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo
    obj_uri = obj_uris[0]
    obj = g.load_user_object(obj_uri)    
    print(obj)
    ipdb.set_trace()
