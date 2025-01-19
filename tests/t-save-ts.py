import uuid
import kgm
import clickhouse_connect
import numpy as np

class TimeSeries:
    def __init__(self, ts_m:kgm.UserObject, clickhouse_db):
        self.ts_m = ts_m
        self.clickhouse_db = clickhouse_db
        self.serno = 0

        tn = self.ts_m.tablename = str(uuid.uuid4()).replace("-", "_")
        q = f"create table {tn} ( serno Int64, value Float64 ) engine = MergeTree() order by (serno)"
        print(q)
        self.clickhouse_db.command(q)
        self.ts_m.get_db().save()
        
    def add(self, v:float):
        tn = self.ts_m.tablename
        q = f"insert into {tn}(serno, value) values({self.serno}, {v})"
        print(q)
        self.clickhouse_db.command(q)
        self.serno += 1
    
if __name__ == "__main__":
    gdb = kgm.Database("/ts-test")
    ccdb = clickhouse_connect.get_client(host='localhost', port=18123, username='default', password='')
    
    ts_m = gdb.create_user_object(kgm.URI(":TimeSeries"))
    #ts_m.tablename = "hi"
    gdb.save()

    print("ts_m:", ts_m.get_uri())
    ts = TimeSeries(ts_m, ccdb)

    if 1:
        for i in range(100):
            ts.add(np.random.rand())
    print(ts.ts_m.get_uri())
    
