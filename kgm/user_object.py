import ipdb
from kgm.rdf_terms import URI, Literal, RDFObject, RDFTriple
from kgm.rdf_utils import get_py_m_name, get_supported_Literal_python_types, from_python_to_Literal
from kgm.user_class import UserClass

class UserObjectMemberEditor:
    def __init__(self, uo, m_path_uri, m_type_uri, min_c, max_c):
        self.uo = uo
        #self.m_uc = m_uc # it points to actual rdfs class where member was introduced in rdfs class hierarchy
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c; self.max_c = max_c
        self.loaded_values = set()
        self.values = set()
        
    def sync__(self):
        self.loaded_values = set(self.values)

    @staticmethod
    def create_RDFObject__(v:object) -> RDFObject:
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

    def load_setup_values__(self, new_values:list[object]):
        #ipdb.set_trace()
        if self.is_01() or self.is_11():
            assert(len(new_values) == 1)
            s_v = new_values[0]
            if len(self.values) == 0:
                self.values.add(s_v)
                self.sync__()
            elif len(self.values) == 1:
                existing_v = [x for x in self.values][0]
                if existing_v != s_v:
                    raise Exception("inconsistent scalar data found during load_setup_initial_value, prev and new value are not the same")
            else:
                raise Exception("inconsistent scalar data found during load_setup_initial_value, prev and new value are not the same")
        else:
            c_vs = new_values
            if len(self.values) == 0:
                self.values.update(c_vs)
                self.sync__()
            else:
                if self.values != c_vs:
                    raise Exception("inconsistent set data found during load_setup_initial_value, prev and new value are not the same")

    def is_01(self):
        return self.min_c == 0 and self.max_c == 1

    def is_11(self):
        return self.min_c == 1 and self.max_c == 1

    def svalue_set(self, value):
        uo_me = self
        len_values = len(uo_me.values)
        g = self.uo.get_impl().g
        if uo_me.is_01():
            g.changed_uo_members.add(uo_me)
            if value is None:
                uo_me.values.clear()
            elif type(value) in [UserObject] + get_supported_Literal_python_types():
                uo_me.values.clear(); uo_me.values.add(value)
            elif type(value) in (list, set):
                raise Exception("expected scalar")
            else:
                raise Exception("unexpected type of value")
        elif uo_me.is_11():
            g.changed_uo_members.add(uo_me)
            if value is None:
                raise Exception("cardinality violation")
            elif type(value) in [UserObject] + get_supported_Literal_python_types():
                uo_me.values.clear(); uo_me.values.add(value)
            elif type(value) in (list, set):
                raise Exception("expected scalar")
            else:
                raise Exception("unexpected type of value")
        else:
            raise Exception("svalue_set is not allowed for non-scalar members")

    def svalue_get(self):
        uo_me = self
        len_values = len(uo_me.values)
        if uo_me.is_01():
            if len_values == 0:
                return None
            elif len_values == 1:
                return [x for x in uo_me.values][0]
            else:
                raise Exception("cardinality violation")
        elif uo_me.is_11():
            if len_values == 0:
                raise Exception("cardinality violation")
            elif len_values == 1:
                return [x for x in uo_me.values][0]
            else:
                raise Exception("cardinality violation")
        else:
            raise Exception("svalue_get is not allowed for non-scalar members")

    def __iter__(self):
        if self.is_01() or self.is_11():
            raise Exception("__iter__ is not supported for scalar members")
        return iter(self.values)

    def mvalue_get(self):
        if self.is_01() or self.is_11():
            raise Exception("mvalue_get is not supported for scalar members")
        return self.values

    def mvalue_has(self, v):
        if self.is_01() or self.is_11():
            raise Exception("mvalue_has is not supported for scalar members")
        return v in self.values
    
    def mvalue_add(self, v):
        if self.is_01() or self.is_11():
            raise Exception("mvalue_add is not supported for scalar members")
        g = self.uo.get_impl().g
        g.changed_uo_members.add(self)
        self.values.add(v)

    def mvalue_clear(self):
        if self.is_01() or self.is_11():
            raise Exception("mvalue_add is not supported for scalar members")
        g = self.uo.get_impl().g
        g.changed_uo_members.add(self)
        self.values.clear()        
        
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

            #print("setting value:", value)

            uo_me = self._storage[name]
            uo_me.svalue_set(value)

    def __getattr__(self, name):
        # Provide access to restricted attributes
        if name not in self._storage:
            # Raise AttributeError if attribute not found or restricted
            raise AttributeError(f"member '{name}' is not accessible.")
            
        #ipdb.set_trace()
        uo_me = self._storage.get(name)
        if uo_me.is_01() or uo_me.is_11():
            ret = uo_me.svalue_get()
        else:
            ret = uo_me

        return ret
