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

#import ipdb
import uuid
import kgm
import numpy as np

class Series:
    def __init__(self, db):        
        self.ts_m = db.create_user_object(kgm.URI("kgm:Series"))
        self.clickhouse_db = db.clickhouse_db

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
    db = kgm.Database("/series-test", init_clickhouse = True)
    
    ts = Series(db)
    #ipdb.set_trace()
    db.save()
    print("ts_m:", ts.ts_m.get_uri())

    if 1:
        for i in range(100):
            ts.add(np.random.rand())
    
