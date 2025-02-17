import ipdb
from kgm import Database, KGMGraph

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/mdvne"
    g_uri = db.get_kgm_graph(kgm_path)
    if g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")
    g = KGMGraph(db, g_uri)
    ipdb.set_trace()

    if 1:
        ssw1 = g.create_user_object(":SSwitch")
        sl1 = g.create_user_object(":SLink")
        sl1.bw = 1000; sl1.resBw = 900
        sl2 = g.create_user_object(":SLink")
        sl2.bw = 1000; sl2.resBw = 900
        ssrv1 = g.create_user_object(":SServer")
        ssrv1.cpu = 32; ssrv1.resCpu = 25

        ssw1.out_ = sl1
        sl1.in_.mvalue_add(ssrv1)
        sl2.in_.mvalue_add(ssw1)
        ssrv1.out_ = sl2
        
    g.save()
