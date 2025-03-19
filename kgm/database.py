#import ipdb
from kgm.prefixes import rdf, xsd, kgm
from kgm.rdf_terms import URI, Literal, BNode
from kgm.rdf_terms import RDFObject, RDFTriple
from kgm.rdf_utils import make_Literal
from kgm.prefix_manager import PrefixManager
import kgm.sparql_utils as sparql_utils
import nanoid

def gen_nanoid():
    return nanoid.generate("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ", 20)


class Database:
    def __init__(self, fuseki_url, db_id = "", clickhouse_client = None):
        self.fuseki_url = fuseki_url
        self.w_prefixes = PrefixManager(empty_prefix = db_id)
        self.clickhouse_client = clickhouse_client
            
    def rq_select(self, query:str):
        raw_rq_res = sparql_utils.rq_select(query, config = {'backend-url': self.fuseki_url}, w_prefixes = self.w_prefixes)
        return sparql_utils.rq_handle_select_result(raw_rq_res, w_prefixes = self.w_prefixes)

    def rq_update(self, query:str):
        return sparql_utils.rq_update(query, config = {'backend-url': self.fuseki_url}, w_prefixes = self.w_prefixes)

    def rq_construct(self, query:str):
        return sparql_utils.rq_construct(query, config = {'backend-url': self.fuseki_url}, w_prefixes = self.w_prefixes)

    def rq_delete_insert(self, graph_uri, dels_inss):
        return sparql_utils.rq_delete_insert(graph_uri, dels_inss, config = {'backend-url': self.fuseki_url}, w_prefixes = self.w_prefixes)
    
    def create_kgm_graph(self, kgm_path_s:str) -> URI:
        descr_g = []
        new_graph_uri = URI("urn:kgm::" + gen_nanoid()) # created in empty kgm namespace
        descr_g.append(RDFTriple(new_graph_uri, rdf.type, RDFObject(kgm.Graph)))
        descr_g.append(RDFTriple(new_graph_uri, kgm.path, RDFObject(make_Literal(kgm_path_s, xsd.string))))

        sparql_utils.rq_delete_insert(None, [[], descr_g], config = {'backend-url': self.fuseki_url}, w_prefixes = self.w_prefixes)
        return new_graph_uri
    
    def get_kgm_graph(self, path) -> URI:
        #ipdb.set_trace()
        rq = f'select ?s where {{ ?s kgm:path "{path}"; rdf:type kgm:Graph }}'
        #print(rq)

        rq_res = self.rq_select(rq)
        graph_uris = rq_res['s']
        #print(rq_res)
        if len(graph_uris) > 1:
            raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

        return None if len(graph_uris) == 0 else graph_uris[0]

    def get_graph_uris(self, kgm_pathes):
        g_uris = []
        for kgm_path in kgm_pathes:
            g_uri = self.get_kgm_graph(kgm_path)
            if g_uri is None:
                raise Exception(f"can't find kgm path {kgm_path}")
            g_uris.append(g_uri)
        return g_uris
