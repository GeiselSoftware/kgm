import ipdb
import uuid
from kgm.prefix_manager import PrefixManager
from kgm.rdf_terms import URI, Literal, BNode, RDFObject, RDFTriple
from kgm.rdf_utils import to_turtle
from kgm.known_prefixes import rdf, xsd, rdfs, sh, dash, kgm, well_known_prefixes
import kgm.sparql_utils as sparql_utils

class Database:
    def __init__(self, fuseki_url, clickhouse_client = None):
        self.fuseki_url = fuseki_url
        self.clickhouse_client = clickhouse_client
        self.well_known_prefixes = {}
        self.init_well_known_prefixes__()

    def init_well_known_prefixes__(self):
        for prefix, prefix_uri in well_known_prefixes.items():
            self.well_known_prefixes[prefix] = prefix_uri
        
    def rq_select(self, query:str):
        return sparql_utils.rq_select__(self.well_known_prefixes, query, config = {'backend-url': self.fuseki_url})

    def rq_update(self, query:str):
        return sparql_utils.rq_update__(self.well_known_prefixes, query, config = {'backend-url': self.fuseki_url})

    def rq_construct(self, query:str):
        return sparql_utils.rq_construct__(self.well_known_prefixes, query, config = {'backend-url': self.fuseki_url})
    
    def rq_insert_triples(self, graph_uri:URI, triples):
        # Serialize the graph to a string in N-Triples format
        ntriples_data = []
        ipdb.set_trace()
        for t in triples:        
            ntriples_data.append(f"{to_turtle(t[0])} {to_turtle(t[1])} {to_turtle(t[2])} .")

        ntriples_data_s = "\n".join(ntriples_data)
        if graph_uri:
            assert(type(graph_uri) == URI)
            update_query = f"""
            INSERT DATA {{
            GRAPH {to_turtle(graph_uri)} {{
            {ntriples_data_s}
            }}
            }}
            """
        else:
            update_query = f"""
            INSERT DATA {{
            {ntriples_data_s}
            }}
            """

        self.rq_update(update_query)

    def rq_delete_insert(self, graph_uri:URI, dels_inss):
        if len(dels_inss[0]) == 0 and len(dels_inss[1]) == 0:
            return None

        delete_triples = [f"{to_turtle(t.subject)} {to_turtle(t.pred)} {to_turtle(t.object_)} ." for t in dels_inss[0]]
        insert_triples = [f"{to_turtle(t.subject)} {to_turtle(t.pred)} {to_turtle(t.object_)} ." for t in dels_inss[1]]

        rq = ""
        if len(delete_triples) > 0:
            delete_triples_s = '\n'.join(delete_triples)
            rq += f"""\
            delete {{
             graph {to_turtle(graph_uri)}
             {{
              {delete_triples_s}
             }}
            }}
            """
        if len(insert_triples) > 0:
            insert_triples_s = '\n'.join(insert_triples)
            rq += f"""\
            insert {{
             graph {to_turtle(graph_uri)}
             {{
              {insert_triples_s}
             }}
            }}
            """
        rq += "where {}"
        
        print(rq)

        self.rq_update(rq)

    def create_kgm_graph(self, kgm_path):
        descr_g = []
        new_graph_uri = URI(kgm.Graph.uri + "--" + str(uuid.uuid4()))
        descr_g.append((new_graph_uri, rdf.type, RDFObject(kgm.Graph)))
        descr_g.append((new_graph_uri, kgm.path, RDFObject(Literal(kgm_path, xsd.string))))

        #ipdb.set_trace()
        self.rq_insert_triples(None, descr_g)
        return new_graph_uri

    def get_kgm_graph(db, path) -> URI:
        #ipdb.set_trace()
        rq = f'select ?s where {{ ?s kgm:path "{path}"; rdf:type kgm:Graph }}'
        #print(rq)

        rq_res = db.rq_select(rq)
        graph_uris = rq_res['s']
        #print(rq_res)
        if len(graph_uris) > 1:
            raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

        return None if len(graph_uris) == 0 else graph_uris[0]
    
