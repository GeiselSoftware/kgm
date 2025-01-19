import ipdb
from kgm.database import *

if __name__ == "__main__":
    ipdb.set_trace()
    gdb = Database("/py-test")

    obj = gdb.load_user_object(URI(":Human--1c822fbf-2ba6-4a52-8bf9-94bcdbe8285f"))
    print(obj.get_impl())
    ipdb.set_trace()
