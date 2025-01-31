#
# docker install on ubuntu jellyfish: https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-22-04
#
# --- from https://hub.docker.com/r/clickhouse/clickhouse-server/
# run clickhouse in docker: 
# docker run -d -p 18123:8123 -p19000:9000 --name local-clickhouse-server --ulimit nofile=262144:262144 clickhouse/clickhouse-server
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
from kgm import xsd
import numpy as np
import clickhouse_connect

class CCUSeries:
    def __init__(self, series_uo:UserObject):        
        self.series_uo = series_uo
        self.clickhouse_db = cc_db

        #ipdb.set_trace()
        self.series_uo.tablename = str(uuid.uuid4()).replace("-", "_")
        self.serno = 0
        q = f"create table {self.series_uo.tablename} ( serno Int64, value Float64 ) engine = MergeTree() order by (serno)"
        #print(q)
        self.clickhouse_db.command(q)
        
    def add(self, v:float):
        q = f"insert into {self.series_uo.tablename}(serno, value) values({self.serno}, {v})"
        #print(q)
        self.clickhouse_db.command(q)
        self.serno += 1

class Test:
    def __init__(self, g:kgm.KGMGraph):
        self.tdata = g.create_user_object(":Test")
        self.tdata.testdata = 1.0
        self.tdata.vs_pyo = CCUSeries(g.create_user_object("ccu:Series"))
        self.tdata = CCUSeries(self.tdata_uo.vs)
        
if __name__ == "__main__":
    ipdb.set_trace()
    ccc = clickhouse_connect.get_client(host='h1', port=18123, username='default', password='')
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = kgm.Database(fuseki_url, ccc)
    g = db.open_graph("/tests/test-ccu", additional_graphs = ["/sys/ccu"])

    ipdb.set_trace()
    if 0:
        ccu_series_uc = g.create_user_class("ccu:Series")
        ccu_series_uc.add_member("ccu:tablename", xsd.string, 1, 1)
        g.save()
        
    test_pyo = Test(g.create_user_object(":Test"))
    test_pyo.tdata = g.create_user_object(":TestData")
    test_pyo.tdata.testdata = 1.0
    test_pyo.vs = g.create_user_object("ccu:Series")
    
    #ipdb.set_trace()
    g.save()
    print("ts_m:", ts.ts_m.get_uri())

    if 1:
        for i in range(100):
            ts.add(np.random.rand())
