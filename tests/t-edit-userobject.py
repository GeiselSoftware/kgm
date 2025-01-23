import ipdb
from kgm import Database, KGMGraph

if __name__ == "__main__":
    #ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_g = KGMGraph(db, "/py-test")

    ipdb.set_trace()
    obj_uris = kgm_g.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo

    obj_uri = obj_uris[0]
    print("obj uri:", obj_uri)
    obj = kgm_g.load_user_object(obj_uri)
    print("address:", obj.address)
    obj.address = "1 Main St"

    ipdb.set_trace()
    kgm_g.save()
