import ipdb
from kgm import get_kgm_graph
from kgm import Database, KGMGraph, URI

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/py-test"
    kgm_g_uri = get_kgm_graph(db, kgm_path)
    if kgm_g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")
    kgm_g = KGMGraph(db, kgm_g_uri, None)

    obj_uris = kgm_g.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo
    obj_uri = obj_uris[0]
    obj = kgm_g.load_user_object(obj_uri)    
    print(obj.get_impl())
    ipdb.set_trace()
