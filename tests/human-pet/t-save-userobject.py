import ipdb
from kgm import Database, KGMGraph

if __name__ == "__main__":
    ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/human-pet"
    g_uri = db.get_kgm_graph(kgm_path)
    if g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")
    g = KGMGraph(db, g_uri)
    ipdb.set_trace()

    obj = g.create_user_object(":Human")
    if 0:
        print(obj.get_impl())
        obj.address = "123 Main St"
        obj.phone = "555-1234"
        obj.age = 1
        obj.cars.multi_value_add("hi")
        print(obj.address)  # Output: 123 Main St
        print(obj.phone)    # Output: 555-1234
        for c in obj.cars:
            print(c)
        print("has hi:", obj.cars.multi_value_has("bi"))
    else:
        obj.get_member_editor("address").svalue_set("123 Main St")
        obj.get_member_editor("phone").svalue_set("555-1234")
        obj.get_member_editor("age").svalue_set(1)
        obj.get_member_editor("cars").mvalue_add("hi")
        print(obj.get_member_editor("address").svalue_get())
        print(obj.get_member_editor("phone").svalue_get())
        for c in obj.get_member_editor("cars").mvalue_get():
            print(c)
        print("has hi:", obj.get_member_editor("cars").mvalue_has("bi"))
        
    # Trying to access an attribute not in the accessible list
    try:
        print(obj.salary)  # Raises AttributeError
    except AttributeError as e:
        print(e)  # Output: Attribute 'salary' is not accessible.

    bim = g.create_user_object(":Pet")
    bim.name = "Bim"
    print(bim.name)
    obj.pet = bim
    obj.get_member_editor("pets").mvalue_add(bim)

    ipdb.set_trace()
    g.save() # ??? db.save
    
