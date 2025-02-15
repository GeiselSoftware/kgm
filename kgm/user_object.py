import ipdb
from kgm.rdf_terms import URI, Literal, RDFObject, RDFTriple
from kgm.rdf_utils import get_py_m_name, from_python_to_Literal, get_supported_Literal_python_types

class UserClassMember:
    def __init__(self, uc, m_path_uri, m_type_uri, min_c, max_c):
        self.user_class = uc
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c
        self.max_c = max_c

class UserClass:
    def __init__(self, g:"KGMGraph", uc_uri:URI):
        self.g = g
        self.uc_uri = uc_uri
        self.super_uc_uris = set()
        self.sub_uc_uris = set()
        self.members = {} # m_path_uri => member attrs

    def add_member__(self, m_path_uri, m_type_uri, min_c:int, max_c:int):
        assert(type(min_c) == int)
        assert(isinstance(m_path_uri, URI))
        assert(isinstance(m_type_uri, URI))
        
        if m_path_uri in self.members:
            #ipdb.set_trace()
            raise Exception(f"this member already added: {to_turtle(m_path_uri)}")

        #ipdb.set_trace()
        new_uc_m = UserClassMember(self, m_path_uri, m_type_uri, min_c, max_c)
        self.members[m_path_uri] = new_uc_m

    def load_create_user_object__(self, uo_uri:URI) -> "UserObject":
        ret = UserObject(self.g, uo_uri, self)
        for k, v in self.members.items():
            ret.add_member_editor__(v.m_path_uri, v.m_type_uri, v.min_c, v.max_c)
        return ret

    def show(self):
        print("uc_uri:", self.uc_uri)
        for k, v in self.members.items():
            print(k, "   ", v)
    
class UserObjectMemberEditor:
    def __init__(self, uo, m_path_uri, m_type_uri, min_c, max_c):
        self.uo = uo
        #self.m_uc = m_uc # it points to actual rdfs class where member was introduced in rdfs class hierarchy
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c; self.max_c = max_c
        self.loaded_values = set()
        self.values = set()

    def is_single_value(self):
        return self.min_c == 1 and self.max_c == 1

    def is_multi_value(self):
        return not (self.min_c == 1 and self.max_c == 1)
    
    def single_value_set(self, v:object, supress_marking_as_changed = False):
        assert(self.is_single_value())
        assert(type(v) in [UserObject] + get_supported_Literal_python_types())
        if v in self.values:
            return
        
        self.values.clear()
        self.values.add(v)
        if supress_marking_as_changed == False:
            self.uo.get_impl().g.changed_uo_members.add(self)
        
    def single_value_get(self) -> object:
        assert(self.is_single_value())
        for el in self.values:
            return el
        raise Exception("single_value_get: no value found")

    def multi_value_has(self, v:object) -> bool:
        assert(self.is_multi_value())
        assert(type(v) in [UserObject] + get_supported_Literal_python_types())
        return v in self.values

    def multi_value_add(self, v:object, supress_marking_as_changed = False):
        assert(self.is_multi_value())
        assert(type(v) in [UserObject] + get_supported_Literal_python_types())
        if v in self.values:
            return        
        self.values.add(v)
        if supress_marking_as_changed == False:
            self.uo.get_impl().g.changed_uo_members.add(self)

    def multi_value_update(self, vs:list[object], supress_marking_as_changed = False):
        assert(self.is_multi_value())
        any_changes = False
        for v in vs:
            assert(type(v) in [UserObject] + get_supported_Literal_python_types())
            if v in self.values:
                continue
            self.values.add(v)
            any_changes = True
        if supress_marking_as_changed == False and any_changes == True:
            self.uo.get_impl().g.changed_uo_members.add(self)
        
    def multi_value_remove(self, v:object, supress_marking_as_changed = False) -> bool:
        assert(self.is_multi_value())
        assert(type(v) in [UserObject] + get_supported_Literal_python_types())
        try:
            self.values.remove(v)
            ret = true
            if supress_marking_as_changed == False:
                self.uo.get_impl().g.changed_uo_members.add(self)
        except KeyError:
            ret = false

        return ret

    def clear(self, supress_marking_as_changed = False):
        if len(self.values) == 0:
            return
        self.values.clear()
        if supress_marking_as_changed == False:
            self.uo.get_impl().g.changed_uo_members.add(self)
        
    def __iter__(self):
        assert(self.is_multi_value())
        return iter(self.values)
    
    def load_setup_values__(self, new_values:list[object]):
        #ipdb.set_trace()
        if self.is_single_value():
            assert(len(new_values) == 1)
            s_v = new_values[0]
            if len(self.values) != 0:
                existing_v = [x for x in self.values][0]
                if existing_v != s_v:
                    raise Exception("inconsistent scalar data found during load_setup_initial_value, prev and new value are not the same")
            else:
                self.single_value_set(s_v, supress_marking_as_changed = True)
                self.sync__()
        else:
            c_vs = new_values
            if len(self.values) == 0:
                self.multi_value_update(c_vs, supress_marking_as_changed = True)
                self.sync__()
            else:
                if self.values != c_vs:
                    raise Exception("inconsistent set data found during load_setup_initial_value, prev and new value are not the same")

    def sync__(self):
        self.loaded_values = set(self.values)
        
    def create_RDFObject__(self, v:object) -> RDFObject:
        if isinstance(v, UserObject):
            ret = RDFObject(v.get_impl().uo_uri)
        else:
            ret = RDFObject(from_python_to_Literal(v))
        return ret

    def get_dels_inss__(self): # returns (set<RDFTriple>, set<RDFTriple>)
        dels_T = self.loaded_values - self.values
        inss_T = self.values - self.loaded_values
        dels = {RDFTriple(self.uo.get_uri(), self.m_path_uri, self.create_RDFObject__(x)) for x in dels_T}
        inss = {RDFTriple(self.uo.get_uri(), self.m_path_uri, self.create_RDFObject__(x)) for x in inss_T}
        return (dels, inss)

class UOImpl:
    def __init__(self, g, uo_uri, uc):
        self.g = g
        self.uo_uri = uo_uri
        self.uc = uc
    
class UserObject:
    def __init__(self, g:"KGMGraph", uo_uri, uc):
        assert(isinstance(uc, UserClass))
        self._uo_impl = UOImpl(g, uo_uri, uc)
        self._storage = {}  # py member name -> UserObjectmemberEditor
        for k, v in uc.members.items():
            #ipdb.set_trace()
            py_m_name = get_py_m_name(v.m_path_uri)
            if py_m_name in self._storage:
                raise Exception(f"dup member name {py_m_name} on member path URI {m_path_uri.to_turtle()}")
            self._storage[py_m_name] = UserObjectMemberEditor(self, v.m_path_uri, v.m_type_uri, v.min_c, v.max_c)

    def get_uri(self):
        return self.get_impl().uo_uri

    def get_g(self):
        return self.get_impl().g
    
    def get_impl(self):
        return getattr(self, "_uo_impl")

    def add_member_editor__(self, m_path_uri, m_type_uri, min_c, max_c):
        #ipdb.set_trace()
        assert(isinstance(m_path_uri, URI))
        m_name = get_py_m_name(m_path_uri)
        self._storage[m_name] = UserObjectMemberEditor(self, m_path_uri, m_type_uri, min_c, max_c)
        
    def get_member_editor(self, m_name):
        assert(isinstance(m_name, str))
        assert(m_name in self._storage)
        return self._storage.get(m_name)

    # special access to member editor objects
    def __dir__(self):
        return self._storage.keys()
    
    def __setattr__(self, name, value):
        # Handle attributes allowed in the restricted list
        if name in {"_storage", "_uo_impl"}:
            # Bypass restriction for internal attributes
            super().__setattr__(name, value)
        else:
            if not name in self._storage:
                raise Exception(f"member {name} was never added")

            uo_me = self._storage[name]
            print("setting value:", value)
            if uo_me.is_single_value():
                uo_me.single_value_set(value)
            else:
                raise Exception("can't assign to set")
    
    def __getattr__(self, name):
        # Provide access to restricted attributes
        if name in self._storage:
            #ipdb.set_trace()
            uo_me = self._storage.get(name)
            if uo_me.is_single_value():
                return uo_me.single_value_get() # will return python object
            else:
                return uo_me # will return UOMemberEditor

        # Raise AttributeError if attribute not found or restricted
        raise AttributeError(f"member '{name}' is not accessible.")
