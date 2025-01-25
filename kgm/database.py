#import ipdb
from kgm.rdf_utils import PrefixManager
from kgm.rdf_utils import rdf, xsd, URI, Literal, RDFObject, RDFTriple
from kgm.rdf_utils import rdfs, sh, dash, BNode
import kgm.sparql_utils as sparql_utils

class Database:
    def __init__(self, fuseki_url):
        self.fuseki_url = fuseki_url
        self.prefix_man = PrefixManager()
        self.init_prefix_manager__()

    def init_prefix_manager__(self):
        """
        rq = "select prefix, prefix_uri { kgm:dsg kgm:prefixes [ kgm:prefix ?prefix; kgm:prefix_uri ?prefix_uri ] }"
        """

        # this version uses constants defined in rdf_utils
        # NB: replace with query to DSG prefixes set
        from kgm.rdf_utils import known_prefixes
        for prefix, prefix_uri in known_prefixes.items():
            self.prefix_man.prefixes[prefix] = prefix_uri

        for prefix, prefix_uri in [('', 'http://www.geisel-software.com/RDF/KGM/TestUser#')]:
            self.prefix_man.prefixes[prefix] = prefix_uri
            
        self.prefix_man.is_initialized = True

    def rq_select(self, query:str):
        return sparql_utils.rq_select__(self.prefix_man, query, config = {'backend-url': self.fuseki_url})

    def rq_update(self, query:str):
        return sparql_utils.rq_update__(self.prefix_man, query, config = {'backend-url': self.fuseki_url})

    def rq_construct(self, query:str):
        return sparql_utils.rq_construct__(self.prefix_man, query, config = {'backend-url': self.fuseki_url})
    
    def rq_insert_triples(self, graph_uri:URI, triples:list[RDFTriple]):
        # Serialize the graph to a string in N-Triples format
        ntriples_data = []
        #ipdb.set_trace()
        for t in triples:        
            ntriples_data.append(f"{t[0].as_turtle()} {t[1].as_turtle()} {t[2].as_turtle()} .")

        ntriples_data_s = "\n".join(ntriples_data)
        if graph_uri:
            assert(type(graph_uri) == URI)
            update_query = f"""
            INSERT DATA {{
            GRAPH {graph_uri.as_turtle()} {{
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

        delete_triples = [f"{t.subject.as_turtle()} {t.pred.as_turtle()} {t.object_.as_turtle()} ." for t in dels_inss[0]]
        insert_triples = [f"{t.subject.as_turtle()} {t.pred.as_turtle()} {t.object_.as_turtle()} ." for t in dels_inss[1]]

        rq = ""
        if len(delete_triples) > 0:
            delete_triples_s = '\n'.join(delete_triples)
            rq += f"""\
            delete {{
             graph {graph_uri.as_turtle()}
             {{
              {delete_triples_s}
             }}
            }}
            """
        if len(insert_triples) > 0:
            insert_triples_s = '\n'.join(insert_triples)
            rq += f"""\
            insert {{
             graph {graph_uri.as_turtle()}
             {{
              {insert_triples_s}
             }}
            }}
            """
        rq += "where {}"
        
        print(rq)

        self.rq_update(rq)
