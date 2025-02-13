import ipdb
import pandas as pd
from . import gen_nanoid
from kgm.rdf_terms import URI, Literal, BNode, RDFTriple
from kgm.prefixes import rdf, rdfs, xsd, sh, dash, kgm
from kgm.rdf_utils import get_py_m_name, make_URI_from_parts, to_turtle, restore_prefix
from kgm.database import Database
from kgm.user_object import UserClass, UserObject

class KGMGraph:
    def __init__(self, db:Database, kgm_g:URI, additional_kgm_pathes:list[str] = None):
        assert(isinstance(kgm_g, URI))
        self.db = db
        self.g = kgm_g
        self.dep_gs = additional_kgm_pathes
        
        self.all_user_classes = {} # URI -> UserClass
        self.all_user_objects = {} # URI -> UserObject
        self.just_created_uo = set()
        self.just_created_uc = set()
        self.just_created_uc_members = set()
        self.changed_uo_members = set()

        #ipdb.set_trace()
        self.load_user_classes__()
            
    def get_user_class(self, uc_curie:str) -> UserClass:
        assert(isinstance(uc_curie, str))
        uc_uri = restore_prefix(uc_curie, self.db.w_prefixes)
        if not uc_uri in self.all_user_classes:
            raise Exception(f"no such user class defined: {uc_uri}")
        return self.all_user_classes.get(uc_uri)
        
    def create_user_object(self, uc_curie:str) -> UserObject:
        uc = self.get_user_class(uc_curie)
        new_uri = make_URI_from_parts(uc.uc_uri, "--" + gen_nanoid()) # object id made of class and nanoid
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
            
        for uc_m in self.just_created_uc_members:
            prop = BNode(kgm.gen_nanoid())
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
                print("del: ", to_turtle(t, self.db.w_prefixes))
            for t in dels_inss[1]:
                print("ins: ", to_turtle(t, self.db.w_prefixes))

        self.db.rq_delete_insert(self.g, dels_inss)

        self.just_created_uo.clear()
        self.just_created_uc.clear()
        self.just_created_uc_members.clear()
        for m in self.changed_uo_members:
            m.sync__()
        self.changed_uo_members.clear()

    def get_from_clause__(self, include_dep_graphs = True):
        #ipdb.set_trace()
        from_parts = [self.g]
        if self.dep_gs is not None and include_dep_graphs == True:
            for g in self.dep_gs:
                from_parts.append(to_turtle(g, self.db.w_prefixes))
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
            rq_res = pd.DataFrame.from_dict(self.db.rq_select(rq))
            for ii, r in rq_res.iterrows():
                uc_uri = r['uc']; super_uc_uri = r['super_uc']
                if not uc_uri in self.all_user_classes:
                    self.all_user_classes[uc_uri] = UserClass(self, uc_uri)
                uc = self.all_user_classes.get(uc_uri); 

                super_uc = None
                if super_uc_uri is not None:
                    if not super_uc_uri in self.all_user_classes:
                        self.all_user_classes[super_uc_uri] = UserClass(self, super_uc_uri)
                    super_uc = self.all_user_classes.get(super_uc_uri)

                if super_uc is not None:
                    uc.super_uc_uris.add(super_uc_uri)
                    super_uc.sub_uc_uris.add(uc_uri)
        
        # load user class members
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
        rq_res = pd.DataFrame.from_dict(self.db.rq_select(rq))
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

        ipdb.set_trace()
        if 1:
            # NB:
            # walk class hierarchy and inserts parent members to child subclasses
            # it could be done on server side by enabled reasoner. then warning suppose to show up
            # indicating that certain class members dict already have entries from superclasses
            all_top_classes = [uc for uc in self.all_user_classes.values() if len(uc.super_uc_uris) == 0]
            for top_class in all_top_classes:
                #ipdb.set_trace()
                stack = [(top_class, [top_class])]
                visited_uc_uris = set()
                while len(stack) > 0:
                    curr_uc, path = stack.pop()
                    if curr_uc.uc_uri not in visited_uc_uris:
                        #print("curr_uc:", curr_uc.uc_uri, ", path:", [x.uc_uri for x in path])
                        for cfa in path[:-1]:
                            #print("update from ", cfa.uc_uri, " to ", curr_uc.uc_uri)
                            #ipdb.set_trace()
                            if len(set(curr_uc.members.keys()) & set(cfa.members.keys())) > 0:
                                print("WARNING: reasoning on server might be enabled")
                            curr_uc.members.update(cfa.members)
                        visited_uc_uris.add(curr_uc.uc_uri)
                        for sub_uc_uri in curr_uc.sub_uc_uris:
                            if sub_uc_uri not in visited_uc_uris:
                                sub_uc = self.all_user_classes.get(sub_uc_uri)
                                stack.append((sub_uc, path + [sub_uc]))
                    
    def load_user_object(self, req_uo_uri: URI) -> UserObject:
        ipdb.set_trace()
        if isinstance(req_uo_uri, str):
            req_uo_uri = URI(req_uo_uri)
        
        rq = f"""\
        select ?uo ?uo_member ?uo_member_value
        {self.get_from_clause__()}
        where {{
          bind({to_turtle(req_uo_uri, self.db.w_prefixes)} as ?s_uo)
          ?uo ?uo_member ?uo_member_value
          filter(!(?uo_member in (rdfs:subClassOf, sh:property, sh:path, sh:datatype, sh:class, sh:minCount, sh:maxCount, sh:closed, dash:closedByType)))
          filter(!(?uo_member_value in (sh:NodeShape, rdfs:Class)))
          ?s_uo (<>|!<>)* ?uo
        }}
        """
        #print(rq)
        res = self.db.rq_select(rq)
        res_df = pd.DataFrame.from_dict(res)
        print(res_df)

        F = res_df['uo_member'] == rdf.type
        types_df = res_df[F]
        members_gdf = res_df[~F].groupby(['uo', 'uo_member'], sort = False)
        
        #ipdb.set_trace()
        for ii, r in types_df.iterrows():
            uo_uri = r['uo']; uo_m_uri = r['uo_member']
            uo_uc_uri = r['uo_member_value']
            if uo_uri not in self.all_user_objects:
                uc = self.all_user_classes.get(uo_uc_uri)
                uo = uc.load_create_user_object__(uo_uri)
                self.all_user_objects[uo_uri] = uo

        ipdb.set_trace()
        for gid, gdf in members_gdf:
            uo_uri, uo_m_uri = gid
            uo_m_value = gdf['uo_member_value']
            
            #ipdb.set_trace()
            uo = self.all_user_objects.get(uo_uri)
            uo_m_name = get_py_m_name(uo_m_uri)
            uo_m = uo.get_member__(uo_m_name)
            uo_m.load_setup_initial_value__(self.all_user_objects, uo_m_value)
                    
        return self.all_user_objects[req_uo_uri]

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
