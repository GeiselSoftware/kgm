import ipdb
from kgm import get_kgm_graph
from kgm import Database, KGMGraph, URI

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/py-test"
    g = db.open_graph(kgm_path)
    if g is None:
        raise Exception(f"can't find kgm path {kgm_path}")

    obj_uris = g.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo
    obj_uri = obj_uris[0]
    obj = g.load_user_object(obj_uri)    
    print(obj.get_impl())
    ipdb.set_trace()
