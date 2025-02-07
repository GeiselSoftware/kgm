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

# kgm graph add /kgm/ccu ccu.ksd
# kgm graph add /tests/test-ccu test-ccu.ksd

import ipdb
import uuid
import kgm
import numpy as np
import clickhouse_connect

class CCUSeries:
    def __init__(self, g, cc_db):
        self.m = g.create_user_object(":Series")
        self.m.tablename = str(uuid.uuid4()).replace("-", "_")
        self.clickhouse_db = cc_db
        self.serno = 0
        q = f"create table {self.m.tablename} ( serno Int64, value Float64 ) engine = MergeTree() order by (serno)"
        #print(q)
        self.clickhouse_db.command(q)
        
    def add(self, v:float):
        q = f"insert into {self.m.tablename}(serno, value) values({self.serno}, {v})"
        #print(q)
        self.clickhouse_db.command(q)
        self.serno += 1

class Test:
    def __init__(self, g:kgm.KGMGraph, cc_db):
        self.m = g.create_user_object(":Test")
        self.m.tdata = g.create_user_object(":TestData")
        self.m.tdata.testdata = 1.0
        self.series = CCUSeries(g, cc_db)
        self.m.vs = self.series.m
        
if __name__ == "__main__":
    ipdb.set_trace()
    ccc = clickhouse_connect.get_client(host='h1', port=18123, username='default', password='')
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = kgm.Database(fuseki_url, ccc)
    kgm_path = "/test-ccu"
    #g = db.open_graph("/tests/test-ccu", additional_graphs = ["/sys/ccu"])
    g_uri = db.get_kgm_graph(kgm_path)
    if g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")

    g = kgm.KGMGraph(db, g_uri)
        
    test_pyo = Test(g, ccc)
    
    ipdb.set_trace()
    g.save()
    print("test.vs:", test_pyo.m.vs.get_uri())

    if 1:
        for i in range(100):
            test_pyo.series.add(np.random.rand())
