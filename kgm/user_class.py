from kgm.rdf_terms import URI

class UserClassMember:
    def __init__(self, uc, m_path_uri, m_type_uri, min_c, max_c, is_class:bool):
        self.user_class = uc
        self.m_path_uri = m_path_uri
        self.m_type_uri = m_type_uri
        self.min_c = min_c
        self.max_c = max_c
        self.is_class = is_class # member could be either sh:class or sh:datatype

class UserClass:
    def __init__(self, g:"KGMGraph", uc_uri:URI):
        self.g = g
        self.uc_uri = uc_uri
        self.super_uc_uris = set()
        self.sub_uc_uris = set()
        self.members = {} # m_path_uri => member attrs

    def add_member__(self, m_path_uri, m_type_uri, min_c:int, max_c:int, is_class):
        assert(type(min_c) == int)
        assert(isinstance(m_path_uri, URI))
        assert(isinstance(m_type_uri, URI))
        
        if m_path_uri in self.members:
            #ipdb.set_trace()
            raise Exception(f"this member already added: {to_turtle(m_path_uri)}")

        #ipdb.set_trace()
        new_uc_m = UserClassMember(self, m_path_uri, m_type_uri, min_c, max_c, is_class)
        self.members[m_path_uri] = new_uc_m

    def load_create_user_object__(self, uo_uri:URI) -> "UserObject":
        from kgm.user_object import UserObject
        ret = UserObject(self.g, uo_uri, self)
        for k, v in self.members.items():
            ret.add_member_editor__(v.m_path_uri, v.m_type_uri, v.min_c, v.max_c)
        return ret

    def show(self):
        print("uc_uri:", self.uc_uri)
        for k, v in self.members.items():
            print(k, "   ", v)
