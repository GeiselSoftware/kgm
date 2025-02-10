import ipdb
from kgm.rdf_terms import URI, Literal
from kgm.rdf_utils import RDFObject, RDFTriple, get_py_m_name

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

    def add_member__(self, m_path_uri, m_type_uri, min_c:int, max_c:int, just_created:bool = True):
        assert(type(min_c) == int)
        if isinstance(m_path_uri, str):
            m_path_uri = self.g.rdftf.restore_prefix(":" + m_path_uri)
        if isinstance(m_type_uri, str):
            m_type_uri = self.g.rdftf.restore_prefix(m_type_uri)
        assert(isinstance(m_path_uri, URI))
        assert(isinstance(m_type_uri, URI))
        
        if m_path_uri in self.members:
            ipdb.set_trace()
            raise Exception(f"this member already added: {m_path_uri.to_turtle(self.g.rdftf)}")
        #ipdb.set_trace()
        new_uc_m = UserClassMember(self, m_path_uri, m_type_uri, min_c, max_c)
        self.members[m_path_uri] = new_uc_m
        if just_created:
            self.g.just_created_uc_members.add(new_uc_m)

    def load_create_user_object__(self, uo_uri:URI) -> "UserObject":
        ret = UserObject(self.g, uo_uri, self)
        for k, v in self.members.items():
            ret.load_add_member__(v.m_path_uri, v.m_type_uri, v.min_c, v.max_c)
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
        self.loaded_s = set()
        self.s = set()

    def is_scalar(self):
        return self.max_c == 1
    
    def set_scalar(self, v:object):
        assert(self.is_scalar())
        self.uo.get_impl().g.changed_uo_members.add(self)
        self.s.clear()
        if isinstance(v, Literal):
            v = v.as_python()
        self.s.add(v)

    def load_set_scalar(self, v:object):
        assert(self.is_scalar() and len(self.s) <= 1)
        if isinstance(v, Literal):
            v = v.as_python()

        if len(self.s) > 0:
            existing_v = [x for x in self.s][0]
            if existing_v == v:
                return
            raise Exception("inconsistent data found during load_set_scalar, prev and new value are not the same")
            
        self.s.add(v)
        self.sync__()
        
    def get_scalar(self):
        assert(self.is_scalar())
        for el in self.s:
            return el

    def add(self, v):
        assert(not self.is_scalar())
        self.uo.get_impl().g.changed_uo_members.add(self)
        if isinstance(v, Literal):
            v = v.as_python()
        self.s.add(v)

    def load_add(self, v):
        assert(not self.is_scalar() and len(self.s) == 0)
        if isinstance(v, Literal):
            v = v.as_python()
        self.s.add(v)
        self.sync__()

    def sync__(self):
        self.loaded_s = set(self.s)
        
    def remove(self, v):
        assert(not self.is_scalar())
        self.uo.get_impl().g.changed_uo_members.add(self)
        try:
            self.s.remove(v)
            ret = true
        except KeyError:
            ret = false
        return ret

    def clear(self):
        assert(not self.is_scalar())
        self.uo.get_impl().g.changed_uo_members.add(self)
        self.s.clear()

    def has_value(self, v):
        assert(not self.is_scalar())
        return v in self.s
        
    def __iter__(self):
        assert(not self.is_scalar())
        return iter(self.s)

    def create_RDFObject__(self, v:object) -> RDFObject:
        if isinstance(v, UserObject):
            ret = RDFObject(v.get_impl().uo_uri)
        else:
            rdftf = self.uo.get_impl().uc.g.rdftf
            ret = RDFObject(rdftf.from_python_to_Literal(v))
        return ret

    def get_dels_inss__(self): # returns (set<RDFTriple>, set<RDFTriple>)
        dels_T = self.loaded_s - self.s
        inss_T = self.s - self.loaded_s
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
            
    def __setattr__(self, name, value):
        # Handle attributes allowed in the restricted list
        if name in {"_storage", "_uo_impl"}:
            # Bypass restriction for internal attributes
            super().__setattr__(name, value)
        else:
            if not name in self._storage:
                raise Exception(f"member {name} was never added")

            uoe = self._storage[name]
            print("setting value:", value)
            if uoe.is_scalar():
                uoe.set_scalar(value)
            else:
                uoe.Add(value)
    
    def __getattr__(self, name):
        # Provide access to restricted attributes
        if name in self._storage:
            #ipdb.set_trace()
            uoe = self._storage.get(name)
            if uoe.is_scalar():
                return uoe.get_scalar() # will return python object
            else:
                return uoe # will return UOMemberEditor

        # Raise AttributeError if attribute not found or restricted
        raise AttributeError(f"member '{name}' is not accessible.")
    
    def load_add_member__(self, m_path_uri, m_type_uri, min_c, max_c):
        #ipdb.set_trace()
        assert(isinstance(m_path_uri, URI))
        m_name = get_py_m_name(m_path_uri)
        self._storage[m_name] = UserObjectMemberEditor(self, m_path_uri, m_type_uri, min_c, max_c)
        
    def get_member__(self, m_name):
        assert(isinstance(m_name, str))
        return self._storage.get(m_name)

    def __dir__(self):
        return self._storage.keys()
    
