import ipdb
from kgm.database import *

if __name__ == "__main__":
    #ipdb.set_trace()
    fuseki_url = "http://localhost:3030/kgm-default-dataset"
    gdb = Database(fuseki_url, "/py-test")
    uc = URI(":Human")
    if not gdb.has_user_class(uc):
        gdb.create_user_class(uc)
    
    obj = gdb.create_user_object(URI(":Human"))
    print(obj.get_impl())
    
    # Adding new accessible attributes dynamically
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

    gdb.create_user_class(URI(":Pet"))
    bim = gdb.create_user_object(URI(":Pet"))
    bim.add_member("name", xsd.string, 1, 1)
    bim.name = "Bim"
    print(bim.name)

    obj.add_member("pet", URI(":Pet"), 1, 1)
    obj.add_member("pets", URI(":Pet"), 0, -1)
    obj.pet = bim
    obj.pets.add(bim)
    
    gdb.save()
