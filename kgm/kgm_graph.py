import ipdb
import uuid
import pandas as pd
from kgm.rdf_terms import URI, Literal, BNode, RDFTermFactory
from kgm.rdf_terms import rdf, rdfs, xsd, sh, dash, kgm, well_known_prefixes
from kgm.rdf_utils import RDFTriple, get_py_m_name
from kgm.database import Database
from kgm.user_object import UserClass, UserObject

class KGMGraph:
    def __init__(self, db:Database, kgm_g:URI, additional_kgm_pathes:list[str] = None):
        assert(isinstance(kgm_g, URI))
        self.db = db
        self.g = kgm_g
        self.dep_gs = additional_kgm_pathes
        self.rdftf = RDFTermFactory()
        if not "" in self.rdftf.prefixes:
            self.rdftf.prefixes[""] = URI("urn:kgm::") # this is prefix with empty kgm namespace
        
        self.all_user_classes = {} # URI -> UserClass
        self.all_user_objects = {} # URI -> UserObject
        self.just_created_uo = set()
        self.just_created_uc = set()
        self.just_created_uc_members = set()
        self.changed_uo_members = set()

        #ipdb.set_trace()
        self.load_user_classes__()
            
    def create_user_class(self, uc_curie:str) -> UserClass:
        assert(isinstance(uc_curie, str))
        uc_uri = self.rdftf.restore_prefix(uc_curie)
        if uc_uri in self.all_user_classes:
            raise Exception(f"such user class already defined: {uc_uri.to_turtle()}")
        new_uc = UserClass(self, uc_uri)
        self.all_user_classes[uc_uri] = new_uc
        self.just_created_uc.add(new_uc)
        return new_uc

    def has_user_class(self, uc_curie:str) -> bool:
        assert(isinstance(uc_curie, str))
        uc_uri = self.rdftf.restore_prefix(uc_curie)
        return uc_uri in self.all_user_classes
    
    def get_user_class(self, uc_curie:str) -> UserClass:
        assert(isinstance(uc_curie, str))
        uc_uri = self.rdftf.restore_prefix(uc_curie)
        if not uc_uri in self.all_user_classes:
            raise Exception(f"no such user class defined: {uc_uri}")
        return self.all_user_classes.get(uc_uri)
        
    def create_user_object(self, uc_curie:str) -> UserObject:
        uc = self.get_user_class(uc_curie)
        new_uri = self.rdftf.make_URI_from_parts(uc.uc_uri, "--" + str(uuid.uuid4())) # object id made of class and uuid
        ret = UserObject(self, new_uri, uc)
        self.just_created_uo.add(ret)
        return ret

    def get_dels_inss__(self):
        dels = []; inss = []

        #ipdb.set_trace()
        for uc in self.just_created_uc:
            inss.append(RDFTriple(uc.uc_uri, rdf.type, rdfs.Class))
            inss.append(RDFTriple(uc.uc_uri, rdf.type, sh.NodeShape))
            inss.append(RDFTriple(uc.uc_uri, dash.closedByType, RDFTermFactory.from_python_to_Literal(True)))
            
        ipdb.set_trace()
        for uc_m in self.just_created_uc_members:
            prop = BNode(str(uuid.uuid4()))
            inss.append(RDFTriple(uc_m.user_class.uc_uri, sh.property, prop))
            inss.append(RDFTriple(prop, sh.path, uc_m.m_path_uri))
            #if uc_m.m_type_uri.get_prefix() == xsd.prefix__:
            if uc_m.m_type_uri.uri_s.find(well_known_prefixes.get("xsd")[0]) == 0:
                inss.append(RDFTriple(prop, sh.datatype, uc_m.m_type_uri))
            else:
                inss.append(RDFTriple(prop, sh.class_, uc_m.m_type_uri))
            inss.append(RDFTriple(prop, sh.minCount, RDFTermFactory.from_python_to_Literal(uc_m.min_c)))
            if uc_m.max_c != -1:
                inss.append(RDFTriple(prop, sh.maxCount, RDFTermFactory.from_python_to_Literal(uc_m.max_c)))

        #ipdb.set_trace()
        for uo in self.just_created_uo:
            inss.append(RDFTriple(uo.get_impl().uo_uri, rdf.type, uo.get_impl().uc.uc_uri))
            
        for uo_m in self.changed_uo_members:
            m_dels_inss = uo_m.get_dels_inss__()
            for t in m_dels_inss[0]:
                dels.append(RDFTriple(t.subject, t.pred, t.object_))
            for t in m_dels_inss[1]:
                inss.append(RDFTriple(t.subject, t.pred, t.object_))

        return (dels, inss)
        
    def save(self):
        ipdb.set_trace()
        dels_inss = self.get_dels_inss__()
        if 1:
            for t in dels_inss[0]:
                print("del: ", t.to_turtle(None))
            for t in dels_inss[1]:
                print("ins: ", t.to_turtle(None))

        self.db.rq_delete_insert(self.g, dels_inss, self.rdftf)

        self.just_created_uo.clear()
        self.just_created_uc.clear()
        self.just_created_uc_members.clear()
        for m in self.changed_uo_members:
            m.sync__()
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
        #ipdb.set_trace()
        from_parts = [self.g]
        if self.dep_gs is not None and include_dep_graphs == True:
            for g in self.dep_gs:
                from_parts.append(g.to_turtle())
        return "\n".join([f"from <{g_uri.uri_s}>" for g_uri in from_parts])
    
    def load_user_classes__(self):
        if 1: # create all user classes including empty ones. next query will not retreive empty rdfs classes
            rq = f"""
            select ?uc ?super_uc
            {self.get_from_clause__()}
            {{
             ?uc rdf:type rdfs:Class.
             optional {{ ?uc rdfs:subClassOf ?super_uc }}
            }}
            """
            ipdb.set_trace()
            rq_res = pd.DataFrame.from_dict(self.db.rq_select(rq, rdftf = self.rdftf))
            for ii, r in rq_res.iterrows():
                uc_uri = r['uc']
                if not uc_uri in self.all_user_classes:
                    self.all_user_classes[uc_uri] = UserClass(self, uc_uri)
                uc = self.all_user_classes[uc_uri]
                
                super_uc_uri = r['super_uc']
                if super_uc_uri is not None:
                    if super_uc_uri in uc.super_uc_uris:
                        raise Exception(f"such class is already superclass of {uc_uri}: {super_uc_uri}")
                    uc.super_uc_uris.add(super_uc_uri)
        
        # load user class members if any
        rq = f"""\
        select ?uc ?uc_m_name ?uc_m_class ?uc_m_datatype ?uc_m_minc ?uc_m_maxc
        {self.get_from_clause__()}
        {{
           ?uc rdf:type rdfs:Class.
           ?uc sh:property ?uc_p.
           ?uc_p sh:path ?uc_m_name filter(?uc_m_name != rdf:type).
           ?uc_p sh:minCount ?uc_m_minc.
           optional {{ ?uc_p sh:maxCount ?uc_m_maxc }}
           optional {{ ?uc_p sh:datatype ?uc_m_datatype }}
           optional {{ ?uc_p sh:class ?uc_m_class }}
        }}
        """
        ipdb.set_trace()
        rq_res = pd.DataFrame.from_dict(self.db.rq_select(rq, rdftf = self.rdftf))
        #print(rq_res)
        #ipdb.set_trace()
        
        for ii, r in rq_res.iterrows():            
            uc_uri = r['uc']
            if not uc_uri in self.all_user_classes:
                raise Exception("logic error: all classes should have been defined at this point")
                #self.all_user_classes[uc_uri] = UserClass(self, uc_uri)
            uc = self.all_user_classes.get(uc_uri)

            # we assume that query will return either datatype or class
            if r['uc_m_class'] is None and r['uc_m_datatype'] is None:
                raise Exception(f"for member {r['uc_m_name']} both class and datatype are None")
            if r['uc_m_class'] is not None and r['uc_m_datatype'] is not None:
                raise Exception(f"for member {r['uc_m_name']} both class and datatype are both not None")
            
            uc_m_type = r['uc_m_class'] if r['uc_m_class'] is not None else r['uc_m_datatype']
            uc_m_class = r['uc_m_class']
            max_c = r['uc_m_maxc'].as_python() if r['uc_m_maxc'] is not None else -1
            uc.add_member__(r['uc_m_name'], uc_m_type, r['uc_m_minc'].as_python(), max_c, just_created = False)

        if 1: # inserts superclass members
            ipdb.set_trace()
            # NB: it would be better to implement deep search to compose subclass members out of child superclasses
            for uc in self.all_user_classes.values():
                for super_uc_uri in uc.super_uc_uris:
                    if not super_uc_uri in self.all_user_classes:
                        raise Exception(f"super_uc_uri not found in loaded classes: {super_uc_uri}")
                    super_uc = self.all_user_classes.get(super_uc_uri)
                    print(uc.uc_uri, super_uc.uc_uri)
                    for super_uc_m in super_uc.members.values():
                        if not super_uc_m.m_path_uri in uc.members:
                            uc.add_member__(super_uc_m.m_path_uri, super_uc_m.m_type_uri, super_uc_m.min_c, super_uc_m.max_c)
                    
    def load_user_object(self, req_uo_uri: URI) -> UserObject:
        ipdb.set_trace()
        if isinstance(req_uo_uri, str):
            req_uo_uri = URI(req_uo_uri)
        
        rq = f"""\
        select ?uo ?uo_member ?uo_member_value
        {self.get_from_clause__()}
        where {{
          bind({req_uo_uri.to_turtle(self.rdftf)} as ?s_uo)
          ?uo ?uo_member ?uo_member_value
          filter(!(?uo_member in (rdfs:subClassOf, sh:property, sh:path, sh:datatype, sh:class, sh:minCount, sh:maxCount, sh:closed, dash:closedByType)))
          filter(!(?uo_member_value in (sh:NodeShape, rdfs:Class)))
          ?s_uo (<>|!<>)* ?uo
        }}
        """
        #print(rq)
        res = self.db.rq_select(rq, rdftf = self.rdftf)
        res_df = pd.DataFrame.from_dict(res)
        print(res_df)

        #ipdb.set_trace()
        for ii, r in res_df.iterrows():
            uo_uri = r['uo']; uo_m_uri = r['uo_member']
            uo_m_value = r['uo_member_value']
            if uo_m_uri == rdf.type:
                uc = self.all_user_classes.get(uo_m_value)
                uo = uc.load_create_user_object__(uo_uri)
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
                        raise Exception(f"unable to find user object with URI {m_uo_uri.to_turtle()}")
                elif isinstance(uo_m_value, Literal):
                    m_v = uo_m_value
                else:
                    raise Exception(f"unexpected type on {uo_m_uri.to_turtle()}, user object {uo_uri.to_turtle()}")

                #ipdb.set_trace()
                uo_m_name = get_py_m_name(uo_m_uri) # uo_m_uri.get_suffix()
                uo_m = uo.get_member__(uo_m_name)
                if uo_m.is_scalar():
                    uo_m.load_set_scalar(m_v)
                else:
                    uo_m.load_add(m_v)
                    
        return self.all_user_objects[req_uo_uri]

    def select_in_current_graph(self, rq_over_current_graph, include_dep_graphs = True):
        rq = f"""\
        select *
        {self.get_from_clause__(include_dep_graphs)}
        {{
           {rq_over_current_graph}          
        }}
        """

        rq_res = self.db.rq_select(rq, rdftf = self.rdftf)
        return pd.DataFrame.from_dict(rq_res)
