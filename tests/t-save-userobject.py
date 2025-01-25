import ipdb
from kgm import get_kgm_graph
from kgm import Database, KGMGraph
from kgm import URI, xsd

if __name__ == "__main__":
    #ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    db = Database(fuseki_url)
    kgm_path = "/py-test"
    kgm_g_uri = get_kgm_graph(db, kgm_path)
    if kgm_g_uri is None:
        raise Exception(f"can't find kgm path {kgm_path}")
    kgm_g = KGMGraph(db, kgm_g_uri, None)
    uc = URI(":Human")
    ipdb.set_trace()
    if not kgm_g.has_user_class(uc):
        kgm_g.create_user_class(uc)
    
    obj = kgm_g.create_user_object(URI(":Human"))
    print(obj.get_impl())
    
    # Adding new accessible attributes dynamically
    ipdb.set_trace()
    obj.add_member("address", xsd.string, 1, 1)
    obj.add_member("phone", xsd.string, 1, 1)
    obj.add_member("cars", xsd.string, 0, -1)
    obj.address = "123 Main St"
    obj.phone = "555-1234"
    obj.add_member("age", xsd.integer, 1, 1)
    obj.age = 1
    obj.cars.add("hi")
    
    print(obj.address)  # Output: 123 Main St
    print(obj.phone)    # Output: 555-1234
    for c in obj.cars:
        print(c)
    print("has hi:", obj.cars.has_value("bi"))
        
    # Trying to access an attribute not in the accessible list
    try:
        print(obj.salary)  # Raises AttributeError
    except AttributeError as e:
        print(e)  # Output: Attribute 'salary' is not accessible.

    kgm_g.create_user_class(URI(":Pet"))
    bim = kgm_g.create_user_object(URI(":Pet"))
    bim.add_member("name", xsd.string, 1, 1)
    bim.name = "Bim"
    print(bim.name)

    obj.add_member("pet", URI(":Pet"), 1, 1)
    obj.add_member("pets", URI(":Pet"), 0, -1)
    obj.pet = bim
    obj.pets.add(bim)

    ipdb.set_trace()
    kgm_g.save()
