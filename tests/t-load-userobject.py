import ipdb
from kgm.database import *

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    gdb = Database(fuseki_url, "/py-test")

    obj = gdb.load(URI(":Human--e98c0c7a-f9cb-44bd-848b-a595ce4c793e"))
    print(obj.get_impl())
    ipdb.set_trace()
