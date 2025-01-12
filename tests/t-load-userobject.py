import ipdb
from kgm.database import *

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    gdb = Database(fuseki_url, "/py-test")

    obj = gdb.load_user_object(URI(":Human--3f202842-6c51-45a2-876c-0caa47445847"))
    print(obj.get_impl())
    ipdb.set_trace()
