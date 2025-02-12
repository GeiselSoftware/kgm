import ipdb
from . import gen_nanoid
from kgm.rdf_terms import RDFTermFactory, URI, Literal, BNode
from kgm.rdf_terms import rdf, xsd, kgm
from kgm.rdf_utils import RDFObject, RDFTriple
import kgm.sparql_utils as sparql_utils

class Database:
    def __init__(self, fuseki_url, clickhouse_client = None):
        self.fuseki_url = fuseki_url
        self.clickhouse_client = clickhouse_client
        self.rdftf = RDFTermFactory()
        self.load_dsg_prefixes__()

    def load_dsg_prefixes__(self):
        # :prefix_list_uri kgm:RDFPrefix[0..n]
        # at this point kgm: and std rdf prefixes are loaded so query below will be well-formed sparql        
        rq = f"""
        select ?prefix ?prefix_uri {{
          kgm:dsg rdf:type kgm:Graph; kgm:prefixes ?prefixes .
          ?prefixes rdf:type kgm:RDFPrefix; kgm:prefix ?prefix; kgm:prefix_uri ?prefix_uri
        }}
        """
        rq_res = self.rq_select(rq, rdftf = self.rdftf)
        self.rdftf.add_prefixes(rq_res)
    
    def rq_select(self, query:str, rdftf:RDFTermFactory):
        rq = rdftf.make_rq(query)
        raw_rq_res = sparql_utils.rq_select__(rq, config = {'backend-url': self.fuseki_url})
        return rdftf.handle_rq_select_result(raw_rq_res)

    def rq_update(self, query:str, rdftf:RDFTermFactory):
        rq = rdftf.make_rq(query)
        return sparql_utils.rq_update__(rq, config = {'backend-url': self.fuseki_url})

    def rq_construct(self, query:str, rdftf:RDFTermFactory):
        rq = rdftf.make_rq(query)
        return sparql_utils.rq_construct__(rq, config = {'backend-url': self.fuseki_url})
    
    def rq_insert_triples(self, graph_uri:URI, triples):
        # Serialize the graph to a string in N-Triples format
        ntriples_data = []
        ipdb.set_trace()
        for t in triples:        
            ntriples_data.append(" ".join(t + ["."]))

        ntriples_data_s = "\n".join(ntriples_data)
        if graph_uri:
            assert(type(graph_uri) == URI)
            update_query = f"""
            INSERT DATA {{
            GRAPH <{graph_uri}> {{
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

        ipdb.set_trace()
        self.rq_update(update_query, rdftf = self.rdftf)

    def rq_delete_insert(self, graph_uri:URI, dels_inss, rdftf):
        if len(dels_inss[0]) == 0 and len(dels_inss[1]) == 0:
            return None

        delete_triples = []; insert_triples = []
        for t in dels_inss[0]:
            delete_triples.append(t.to_turtle(rdftf))
        for t in dels_inss[1]:
            insert_triples.append(t.to_turtle(rdftf))

        rq = ""
        if len(delete_triples) > 0:
            delete_triples_s = '\n'.join(delete_triples)
            rq += f"""\
            delete {{
             graph {graph_uri.to_turtle(rdftf)}
             {{
              {delete_triples_s}
             }}
            }}
            """
        if len(insert_triples) > 0:
            insert_triples_s = '\n'.join(insert_triples)
            rq += f"""\
            insert {{
             graph {graph_uri.to_turtle(rdftf)}
             {{
              {insert_triples_s}
             }}
            }}
            """
        rq += "where {}"

        ipdb.set_trace()
        print(rq)

        self.rq_update(rq, rdftf = rdftf)

    def create_kgm_graph(self, kgm_path_s:str) -> URI:
        descr_g = []
        new_graph_uri = URI("urn:kgm::" + gen_nanoid()) # created in empty kgm namespace
        descr_g.append((new_graph_uri, rdf.type, RDFObject(kgm.Graph)))
        descr_g.append((new_graph_uri, kgm.path, RDFObject(self.rdftf.make_Literal(kgm_path_s, xsd.string))))

        ipdb.set_trace()
        descr_g = [[x.to_turtle(None) for x in y] for y in descr_g]
        self.rq_insert_triples(None, descr_g)
        return new_graph_uri
    
    def get_kgm_graph(self, path) -> URI:
        #ipdb.set_trace()
        rq = f'select ?s where {{ ?s kgm:path "{path}"; rdf:type kgm:Graph }}'
        #print(rq)

        rq_res = self.rq_select(rq, rdftf = self.rdftf)
        graph_uris = rq_res['s']
        #print(rq_res)
        if len(graph_uris) > 1:
            raise Exception(f"path leads to multiple kgm graphs: {rq_res}")

        return None if len(graph_uris) == 0 else graph_uris[0]
