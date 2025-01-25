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

import ipdb
import uuid
import kgm
from kgm import xsd
import numpy as np
import clickhouse_connect

class Series:
    def __init__(self, g:kgm.KGMGraph, cc_db):        
        self.ts_m = g.create_user_object(kgm.URI("ccu:Series"))
        self.clickhouse_db = cc_db

        #ipdb.set_trace()
        self.tn = self.ts_m.tablename = str(uuid.uuid4()).replace("-", "_")
        self.serno = 0
        q = f"create table {self.tn} ( serno Int64, value Float64 ) engine = MergeTree() order by (serno)"
        #print(q)
        self.clickhouse_db.command(q)
        
    def add(self, v:float):
        q = f"insert into {self.tn}(serno, value) values({self.serno}, {v})"
        #print(q)
        self.clickhouse_db.command(q)
        self.serno += 1
    
if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = kgm.Database(fuseki_url)
    g_uri = kgm.get_kgm_graph(db, "/ccu-series-test.new")
    g = kgm.KGMGraph(db, g_uri, None)
    ipdb.set_trace()
    if 0:
        ccu_series_uc = g.create_user_class(kgm.URI("ccu:Series"))
        ccu_series_uc.add_member(kgm.URI("ccu:tablename"), xsd.string, 1, 1)
        g.save()
        
    ccc = clickhouse_connect.get_client(host='h1', port=18123, username='default', password='')
    ts = Series(g, ccc)
    #ipdb.set_trace()
    g.save()
    print("ts_m:", ts.ts_m.get_uri())

    if 1:
        for i in range(100):
            ts.add(np.random.rand())
