import ipdb
from kgm.database import *

if __name__ == "__main__":
    #ipdb.set_trace()
    gdb = Database("/py-test")

    ipdb.set_trace()
    obj_uris = gdb.select_in_current_graph("select ?uo { ?uo rdf:type :Human }").uo

    obj_uri = obj_uris[0]
    print("obj uri:", obj_uri)
    obj = gdb.load_user_object(obj_uri)
    print("address:", obj.address)
    obj.address = "1 Main St"

    ipdb.set_trace()
    gdb.save()
