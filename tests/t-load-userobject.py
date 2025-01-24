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

    obj = kgm_g.load_user_object(URI(":Human--b9fec1ba-10fb-470a-b4fa-f78496514211"))
    print(obj.get_impl())
    ipdb.set_trace()
