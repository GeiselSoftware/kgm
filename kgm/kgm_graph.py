#import ipdb
import uuid
import pandas as pd
from kgm.rdf_utils import URI, Literal, BNode, RDFTriple
from kgm.rdf_utils import rdf, rdfs, xsd, sh, dash
from kgm.database import Database
from kgm.user_object import UserClass, UserObject

class KGMGraph:
    def __init__(self, db:Database, g:URI, dep_gs:list[URI]):
        assert(isinstance(g, URI))
        self.db = db
        self.g = g
        self.dep_gs = dep_gs

        self.all_user_classes = {} # URI -> UserClass
        self.all_user_objects = {} # URI -> UserObject
        self.just_created_uo = set()
        self.just_created_uc = set()
        self.just_created_uc_members = set()
        self.changed_uo_members = set()

        self.load_user_classes__()
        
    def create_user_class(self, uc_uri:URI) -> UserClass:
        if uc_uri in self.all_user_classes:
            raise Exception(f"such user class already defined: {uc_uri.as_turtle()}")
        new_uc = UserClass(self, uc_uri)
        self.all_user_classes[uc_uri] = new_uc
        self.just_created_uc.add(new_uc)

    def has_user_class(self, uc_uri:URI) -> bool:
        return uc_uri in self.all_user_classes
    
    def get_user_class(self, uc_uri:URI) -> UserClass:
        if not uc_uri in self.all_user_classes:
            raise Exception(f"no such user class defined: {uc_uri.as_turtle()}")
        return self.all_user_classes.get(uc_uri)        
        
    def create_user_object(self, uc_uri:URI) -> UserObject:
        new_uri = URI(":" + uc_uri.get_suffix() + "--" + str(uuid.uuid4()))
        ret = UserObject(self, new_uri, uc_uri)
        self.just_created_uo.add(ret)
        return ret

    def get_dels_inss__(self):
        dels = []; inss = []

        for uc in self.just_created_uc:
            inss.append(RDFTriple(uc.uc_uri, rdf.type, rdfs.Class))
            inss.append(RDFTriple(uc.uc_uri, rdf.type, sh.NodeShape))
            inss.append(RDFTriple(uc.uc_uri, dash.closedByType, Literal.from_python(True)))
            
        for uc_m in self.just_created_uc_members:
            prop = BNode(str(uuid.uuid4()))
            inss.append(RDFTriple(uc_m.user_class.uc_uri, sh.property, prop))
            inss.append(RDFTriple(prop, sh.path, uc_m.m_path_uri))
            if uc_m.m_type_uri.get_prefix() == xsd.prefix__:
                inss.append(RDFTriple(prop, sh.datatype, uc_m.m_type_uri))
            else:
                inss.append(RDFTriple(prop, sh.class_, uc_m.m_type_uri))
            inss.append(RDFTriple(prop, sh.min_c, Literal.from_python(uc_m.min_c)))
            if uc_m.max_c != -1:
                inss.append(RDFTriple(prop, sh.max_c, Literal.from_python(uc_m.max_c)))
        
        for uo in self.just_created_uo:
            inss.append(RDFTriple(uo.get_impl().uo_uri, rdf.type, uo.get_impl().uc_uri))
            
        for uo_m in self.changed_uo_members:
            m_dels_inss = uo_m.get_dels_inss__()
            for t in m_dels_inss[0]:
                dels.append(RDFTriple(t.subject, t.pred, t.object_))
            for t in m_dels_inss[1]:
                inss.append(RDFTriple(t.subject, t.pred, t.object_))

        return (dels, inss)
        
    def save(self):
        #ipdb.set_trace()
        dels_inss = self.get_dels_inss__()
        if 1:
            for t in dels_inss[0]:
                print("del: ", t.subject.as_turtle(), t.pred.as_turtle(), t.object_.as_turtle())
            for t in dels_inss[1]:
                print("ins: ", t.subject.as_turtle(), t.pred.as_turtle(), t.object_.as_turtle())

        self.db.rq_delete_insert(self.g, dels_inss)

        self.just_created_uo.clear()
        self.just_created_uc.clear()
        self.just_created_uc_members.clear()
        self.changed_uo_members.clear()

    def add_user_object__(self, uo: UserObject, is_just_created: bool):
        self.all_user_objects[uo.get_uri()] = uo
        if is_just_created:
            self.just_created_uo.add(uo)

    def get_user_object__(self, uri:URI) -> UserObject:
        if uri in self.all_user_objects:
            return self.all_user_objects.get(uri)
        return None

    def get_from_clause__(self, include_dep_graphs = True):
        from_parts = [self.g.as_turtle()]
        if self.dep_gs is not None and include_dep_graphs == True:
            for g in self.dep_gs:
                from_parts.append(g.as_turtle())
        return "\n".join(["from " + g_uri for g_uri in from_parts])
    
    def load_user_classes__(self):
        rq = f"""\
        select ?uc ?uc_m_name ?uc_m_is_class ?uc_m_type ?uc_m_minc ?uc_m_maxc
        {self.get_from_clause__()}
        {{
           ?uc rdf:type rdfs:Class.
           ?uc sh:property ?uc_p.
           ?uc_p sh:path ?uc_m_name filter(?uc_m_name != rdf:type).
           ?uc_p sh:minCount ?uc_m_minc.
           optional {{ ?uc_p sh:maxCount ?uc_m_maxc }}
           {{ optional {{ ?uc_p sh:datatype ?uc_m_type bind(false as ?uc_m_is_class) }} }}
              union {{ optional {{ {{ ?uc_p sh:class ?uc_m_type bind(true as ?uc_m_is_class)}} }}
           }}
        }}
        """

        rq_res = pd.DataFrame.from_dict(self.db.rq_select(rq))
        #print(rq_res)
        #ipdb.set_trace()
        
        for ii, r in rq_res.iterrows():            
            uc_uri = r['uc']
            if not uc_uri in self.all_user_classes:
                self.all_user_classes[uc_uri] = UserClass(self, uc_uri)
            uc = self.all_user_classes.get(uc_uri)
            max_c = r['uc_m_maxc'].as_python() if r['uc_m_maxc'] is not None else -1
            uc.add_member(r['uc_m_name'], r['uc_m_type'], r['uc_m_minc'].as_python(), max_c, just_created = False)
    
    def load_user_object(self, uo_uri: URI) -> UserObject:
        #ipdb.set_trace()
        if isinstance(uo_uri, str):
            uo_uri = URI(uo_uri)
        
        rq = f"""\
        select ?uo ?uo_member ?uo_member_value
        {self.get_from_clause__()}
        where {{
          bind({uo_uri.as_turtle()} as ?s_uo)
          ?uo ?uo_member ?uo_member_value
          filter(!(?uo_member in (sh:property, sh:path, sh:datatype, sh:class, sh:minCount, sh:maxCount, dash:closedByType)))
          filter(!(?uo_member_value in (sh:NodeShape, rdfs:Class)))
          ?s_uo (<>|!<>)* ?uo
        }}
        """
        print(rq)
        res = self.db.rq_select(rq)
        res_df = pd.DataFrame.from_dict(res)
        print(res_df)

        #ipdb.set_trace()
        for ii, r in res_df.iterrows():
            uo_uri = r['uo']; uo_m_uri = r['uo_member']
            uo_m_value = r['uo_member_value']
            if uo_m_uri == rdf.type:
                uc = self.all_user_classes.get(uo_m_value)
                uo = uc.load_create_user_object(uo_uri)
                self.all_user_objects[uo_uri] = uo

        #ipdb.set_trace()
        for ii, r in res_df.iterrows():
            uo_uri = r['uo']
            uo_m_uri = r['uo_member']
            uo_m_value = r['uo_member_value']
            uo = self.all_user_objects.get(uo_uri)
            if uo_m_uri != rdf.type:
                if isinstance(uo_m_value, URI):
                    m_uo_uri = uo_m_value
                    if m_uo_uri in self.all_user_objects:
                        m_v = self.all_user_objects.get(m_uo_uri)
                    else:
                        raise Exception(f"unable to find user object with URI {m_uo_uri.as_turtle()}")
                elif isinstance(uo_m_value, Literal):
                    m_v = uo_m_value
                else:
                    raise Exception(f"unexpected type on {uo_m_uri.as_turtle()}, user object {uo_uri.as_turtle()}")

                #ipdb.set_trace()
                uo_m = uo.get_member(uo_m_uri)
                if uo_m.is_scalar():
                    uo_m.set_scalar(m_v)
                else:
                    uo_m.add(m_v)
                    
        return self.all_user_objects[uo_uri]

    def select_in_current_graph(self, rq_over_current_graph, include_dep_graphs = True):
        rq = f"""\
        select *
        {self.get_from_clause__(include_dep_graphs)}
        {{
           {rq_over_current_graph}          
        }}
        """

        rq_res = self.db.rq_select(rq)
        return pd.DataFrame.from_dict(rq_res)
