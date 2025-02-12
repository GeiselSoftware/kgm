#
# docker install on ubuntu jellyfish: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04
#
# --- from https://hub.docker.com/r/clickhouse/clickhouse-server/
# run clickhouse in docker: 
# docker run -d -p 18123:8123 -p19000:9000 --name local-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server
# docker start local-clickhouse-server
# docker exec -it local-clickhouse-server clickhouse-client
# > create table a (a String) engine = Log
# > select * from a
#
# pip install posix-ipc
# pip install clickhouse-connect
#

import ipdb
import kgm
import numpy as np
import clickhouse_connect

def add_point(series_uo, v):
    clickhouse_db = series_uo.db.get_cc()
    q = f"insert into {series_uo.tablename}(serno, value) values({self.serno}, {v})"
    

class SeriesA:
    def __init__(self, series_uo):
        self.series_uo = series_uo
        self.series_uo.tablename = kgm.gen_nanoid()
        #ipdb.set_trace()
        self.clickhouse_db = self.series_uo.get_g().db.clickhouse_client
        self.serno = 0
        q = f"create table {self.series_uo.tablename} ( serno Int64, value Float64 ) engine = MergeTree() order by (serno)"
        #print(q)
        self.clickhouse_db.command(q)
        
    def add_point(self, v:float):
        q = f"insert into {self.series_uo.tablename}(serno, value) values({self.serno}, {v})"
        #print(q)
        self.clickhouse_db.command(q)
        self.serno += 1
        
if __name__ == "__main__":
    ipdb.set_trace()
    ccc = clickhouse_connect.get_client(host='h1', port=18123, username='default', password='')
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = kgm.Database(fuseki_url, ccc)
    kgm_path = "/test-ccu"
    g_uri = db.get_kgm_graph(kgm_path)
    if g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")

    g = kgm.KGMGraph(db, g_uri)

    ipdb.set_trace()
    #test_uo = g.create_uo(":Test", tdata = g.create_uo(":TestData"), vs = g.create_uo(":Series"))
    test_uo = g.create_user_object(":Test")
    test_uo.tdata = g.create_user_object(":TestData")
    test_uo.vs = g.create_user_object(":Series")
    test_uo.tdata.testdata = 111.0
    series_a = SeriesA(test_uo.vs)
    
    ipdb.set_trace()
    g.save()
    print("test.vs:", test_uo.vs.get_uri())

    for i in range(100):
        series_a.add_point(np.random.rand())

