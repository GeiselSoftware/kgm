import ipdb
from kgm import Database, KGMGraph, URI

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_g = KGMGraph(db, "/py-test")

    obj = kgm_g.load_user_object(URI(":Human--843cfc03-0b8e-4478-b25d-b924189b655b"))
    print(obj.get_impl())
    ipdb.set_trace()
