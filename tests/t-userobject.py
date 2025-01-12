import ipdb
from kgm.rdf_utils import URI

class UserObject:
    def __init__(self):
        self._edges = []  # Define allowed attributes
        self._storage = {}  # Store attribute values
    
    def __setattr__(self, name, value):
        # Handle attributes allowed in the restricted list
        if name in {"_edges", "_storage"}:
            # Bypass restriction for internal attributes
            super().__setattr__(name, value)
        else:
            uri = URI(":" + name)
            if uri in self._edges:
                self._storage[uri] = value
            else:
                # Allow unrestricted attributes to behave normally
                super().__setattr__(name, value)
    
    def __getattr__(self, name):
        # Provide access to restricted attributes
        uri = URI(":" + name)
        if uri in self._edges:
            return self._storage.get(uri, None)  # Default to None if unset
        # Raise AttributeError if attribute not found or restricted
        raise AttributeError(f"member '{uri.as_turtle()}' is not accessible.")
    
    def add_member(self, attr):
        """Add new attributes to the accessible list."""
        uri = URI(":" + attr)
        self._edges.append(uri)

if __name__ == "__main__":
    # Example Usage
    obj = UserObject()

    # Adding new accessible attributes dynamically
    obj.add_member("address")
    obj.add_member("phone")
    obj.address = "123 Main St"
    obj.phone = "555-1234"
    
    print(obj.address)  # Output: 123 Main St
    print(obj.phone)    # Output: 555-1234
    
    # Trying to access an attribute not in the accessible list
    try:
        print(obj.salary)  # Raises AttributeError
    except AttributeError as e:
        print(e)  # Output: Attribute 'salary' is not accessible.

    print(obj._storage)
