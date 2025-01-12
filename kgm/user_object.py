from kgm.rdf_utils import rdf, xsd, URI, Literal, RDFObject, RDFTriple

class UserClassMember:
    def __init__(self, uc, m_path_uri, m_type_uri, min_c, max_c):
        self.user_class = uc
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c
        self.max_c = max_c

class UserClass:
    def __init__(self, db:"Database", uc_uri:URI):
        self.db = db
        self.uc_uri = uc_uri
        self.members = {} # m_path_uri => member attrs

    def add_member(self, m_path_uri:URI, m_type_uri:URI, min_c:int, max_c:int, just_created:bool = True):
        if m_path_uri in self.members:
            raise Exception(f"this member already added: {m_path_uri.as_turtle()}")
        new_uc_m = UserClassMember(self, m_path_uri, m_type_uri, min_c, max_c)
        self.members[m_path_uri] = new_uc_m
        if just_created:
            self.db.just_created_uc_members.add(new_uc_m)

    def load_create_user_object(self, uo_uri:URI) -> "UserObject":
        ret = UserObject(self.db, uo_uri, self.uc_uri)
        for k, v in self.members.items():
            ret.load_add_member(v.m_path_uri, v.m_type_uri, v.min_c, v.max_c)
        return ret
        
class UserObjectMemberEditor:
    def __init__(self, uo, m_path_uri, m_type_uri, min_c, max_c):
        self.uo = uo
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c; self.max_c = max_c
        self.loaded_s = set()
        self.s = set()

    def is_scalar(self):
        return self.max_c == 1
    
    def set_scalar(self, v:object):
        assert(self.is_scalar())
        self.uo.get_impl().db.changed_uo_members.add(self)
        self.s.clear()
        if isinstance(v, Literal):
            v = v.as_python()
        self.s.add(v)

    def get_scalar(self):
        assert(self.is_scalar())
        for el in self.s:
            return el

    def add(self, v):
        assert(not self.is_scalar())
        self.uo.get_impl().db.changed_uo_members.add(self)
        if isinstance(v, Literal):
            v = v.as_python()
        self.s.add(v)

    def remove(self, v):
        assert(not self.is_scalar())
        self.uo.get_impl().db.changed_uo_members.add(self)
        try:
            self.s.remove(v)
            ret = true
        except KeyError:
            ret = false
        return ret

    def clear(self):
        assert(not self.is_scalar())
        self.uo.get_impl().db.changed_uo_members.add(self)
        self.s.clear()

    def has_value(self, v):
        assert(not self.is_scalar())
        return v in self.s
        
    def __iter__(self):
        assert(not self.is_scalar())
        return iter(self.s)

    @staticmethod
    def create_RDFObject__(v:object) -> RDFObject:
        if isinstance(v, UserObject):
            ret = RDFObject(v.get_impl().uo_uri)
        else:
            ret = RDFObject(Literal.from_python(v))
        return ret

    def get_dels_inss__(self): # returns (set<RDFTriple>, set<RDFTriple>)
        dels_T = self.loaded_s - self.s
        inss_T = self.s - self.loaded_s
        dels = {RDFTriple(self.uo.get_uri(), self.m_path_uri, self.create_RDFObject__(x)) for x in dels_T}
        inss = {RDFTriple(self.uo.get_uri(), self.m_path_uri, self.create_RDFObject__(x)) for x in inss_T}
        return (dels, inss)
    
class UOImpl:
    def __init__(self, db, uo_uri, uc_uri):
        self.db = db
        self.uo_uri = uo_uri
        self.uc_uri = uc_uri
    
class UserObject:
    def __init__(self, db, uo_uri, uc_uri):
        self._uo_impl = UOImpl(db, uo_uri, uc_uri)
        self._storage = {}  # m_path URI -> UserObjectmemberEditor

    def get_uri(self):
        return self.get_impl().uo_uri
        
    def get_impl(self):
        return getattr(self, "_uo_impl")
        
    def __setattr__(self, name, value):
        # Handle attributes allowed in the restricted list
        if name in {"_storage", "_uo_impl"}:
            # Bypass restriction for internal attributes
            super().__setattr__(name, value)
        else:
            uri = URI(":" + name)
            if uri in self._storage:
                uoe = self._storage[uri]
                print("setting value:", value)
                if uoe.is_scalar():
                    uoe.set_scalar(value)
                else:
                    uoe.Add(value)
            else:
                # Allow unrestricted attributes to behave normally
                super().__setattr__(name, value)
    
    def __getattr__(self, name):
        # Provide access to restricted attributes
        uri = URI(":" + name)
        if uri in self._storage:
            #ipdb.set_trace()
            uoe = self._storage.get(uri)
            if uoe.is_scalar():
                return uoe.get_scalar() # will return python object
            else:
                return uoe # will return UOMemberEditor

        # Raise AttributeError if attribute not found or restricted
        raise AttributeError(f"member '{uri.as_turtle()}' is not accessible.")
    
    def add_member(self, m_path_s:str, m_type_uri:URI, min_c, max_c):
        """Add new attributes to the accessible list."""
        assert(isinstance(m_path_s, str))
        m_path_uri = URI(":" + m_path_s)
        db = self.get_impl().db
        uc = db.get_user_class(self.get_impl().uc_uri)
        uc.add_member(m_path_uri, m_type_uri, min_c, max_c)
        self._storage[m_path_uri] = UserObjectMemberEditor(self, m_path_uri, m_type_uri, min_c, max_c)

    def load_add_member(self, m_path_uri, m_type_uri, min_c, max_c):
        assert(isinstance(m_path_uri, URI))
        self._storage[m_path_uri] = UserObjectMemberEditor(self, m_path_uri, m_type_uri, min_c, max_c)

        
    def get_member(self, m_path_uri):
        return self._storage.get(m_path_uri)
