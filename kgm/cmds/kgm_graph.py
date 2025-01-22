import ipdb
import sys
import rdflib
import urllib
import pandas as pd
from ..sparql_utils import make_rq, rq_select, rq_insert_graph, rq_update
from ..kgm_utils import *


# initialize new fuseki server dataset
def do_server_init(w_config):
    # this list of prefixes used only in update queries during init to create kgm server defult graph
    w_prefixes = """\
    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
    prefix sh: <http://www.w3.org/ns/shacl#>
    prefix kgm: <http://www.geisel-software.com/RDF/KGM#>
    """

    #ipdb.set_trace()
    rq_res = rq_select(f"""\
    {w_prefixes}
    select ?s {{ ?s rdf:type kgm:DefaultServerGraph }}
    """, config = w_config)

    if len(rq_res["s"]) > 0:
        raise Exception("kgm init failed: dataset is already initialized")

    # start shaping kgm default graph
    """
    class kgm:RDFPrefix
      kgm:prefix xsd:string
      kgm:prefix_uri xsd:string
    end

    class kgm:DefaultServerGraph
      kgm:fuseki_dataset_name xsd:string
      kgm:known_prefixes kgm:RDFPrefix[0..n]
    end

    class kgm:Graph
      kgm:path xsd:string
    end
    """

    raw_rq = []
    
    raw_rq.append("""\
    kgm:RDFPrefix rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:prefix; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    sh:property [ sh:path kgm:prefix_uri; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    .

    kgm:DefaultServerGraph rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:fuseki_dataset_name; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1 ];
    sh:property [ sh:path kgm:known_prefixes; sh:class kgm:RDFPrefix; sh:minCount 0 ];
    .
    
    kgm:Graph rdf:type rdfs:Class; rdf:type sh:NodeShape; sh:closed true;
    sh:property [ sh:path kgm:path; sh:datatype xsd:string; sh:minCount 1; sh:maxCount 1];
    .
    """)

    raw_rq.append("""\
    kgm:dsg rdf:type kgm:DefaultServerGraph; kgm:fuseki_dataset_name "kgm-default-dataset" .
    """)

    default_kgm_dataset_prefixes = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "sh": "http://www.w3.org/ns/shacl#",
        "dash": "http://datashapes.org/dash#",
        "kgm": "http://www.geisel-software.com/RDF/KGM#"
    }

    for prefix, prefix_uri in default_kgm_dataset_prefixes.items():
        raw_rq.append(f"""\
        kgm:dsg kgm:prefix [ 
          rdf:type kgm:RDFPrefix; 
          kgm:prefix "{prefix}"; 
          kgm:prefix_uri "{prefix_uri}"
        ].
        """)        

    raw_rq = "\n".join(raw_rq)
    update_rq = f"""\
    {w_prefixes}
    insert data {{
      {raw_rq}
    }}
    """
    #ipdb.set_trace()
    rq_update(update_rq, config = w_config)


def do_ls(w_config, path):
    #print("do_ls:", path)
    query = make_rq("""
    select ?kgm_path ?g { ?g rdf:type kgm:Graph; kgm:path ?kgm_path } 
    """)
    #print(query)
    #ipdb.set_trace()
    
    res = rq_select(query, config = w_config)
    print(pd.DataFrame(res).map(lambda x: x.as_turtle()))

def do_new(w_config, path):
    print("do_graph_new:", path)

    graph_uri = get_kgm_graph(w_config, path)
    if graph_uri is not None:
        print(f"graph exists on path {path}, giving up, graph was {graph_uri.uri}")
        return
    del graph_uri

    #ipdb.set_trace()
    graph_uri = create_kgm_graph(w_config, path)
    print(f"created graph at path {path}: {graph_uri}")

def do_cat(w_config, path):
    graph_uri = get_kgm_graph(w_config, path)
    if graph_uri is None:
        print(f"can't find graph at path {path}", file = sys.stderr)
        return

    rq = make_rq(f"""
    construct {{ 
      ?s ?p ?o 
    }} where {{
       graph {graph_uri} {{ 
         ?s ?p ?o
       }}
    }} order by ?s ?p ?o
    """)
    #print(rq)
    g = rq_construct(rq, config = w_config)
    #print(len(g))
    #print(type(g))

    if 0:
        print(g.serialize(format="ttl"))
    else:
        # this is other end of hack to insert bnodes as URIs with dummy: as prefix
        res_g = rdflib.Graph()
        for s, p, o in g:
            #print(s, p, o)
            if s.toPython().startswith("dummy:"):
                s = rdflib.BNode(s)
            if type(o) == rdflib.URIRef and o.toPython().startswith("dummy:"):
                o = rdflib.BNode(o)
            res_g.add((s, p, o))
        print(res_g.serialize(format="ttl"))

def parse_ttl(source):
    g = rdflib.Graph()
    g.parse(source, format = "turtle")
    triples = []
    for s, p, o in g:
        new_spo = []
        for r in [s, p, o]:
            #print(r)
            if type(r) == rdflib.URIRef:
                new_spo.append(URI(collapse_prefix__(r.toPython())))
            elif type(r) == rdflib.BNode:
                new_spo.append(BNode(r.toPython()))
            elif type(r) == rdflib.Literal:
                new_spo.append(Literal(r.toPython(), URI(collapse_prefix__(r.datatype.toPython()))))
            else:
                raise Exception("parse_ttl conversion failed")
        triples.append(new_spo)
    
    return triples
        
def do_import(w_config, path, ttl_file):
    print("do_import:", path, ttl_file)
    #ipdb.set_trace()
    
    graph_uri = get_kgm_graph(w_config, path)
    if graph_uri is not None:
        print(f"graph at path {path} already exists:", graph_uri)
        return
    del graph_uri

    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            source_triples = parse_ttl(fd)
    else:
        source_triples = parse_ttl(ttl_file)
    
    #ipdb.set_trace()
    graph_uri = create_kgm_graph(w_config, path)
    rq_insert_graph(source_triples, graph_uri, config = w_config)

    print(path, graph_uri)
    
def do_remove(w_config, path):
    graph_uri = get_kgm_graph(w_config, path)
    if graph_uri is None:
        print(f"can't find graph at path {path}")
        return
    
    rq_queries = [make_rq(f"drop graph {graph_uri.as_turtle()}"),
                  make_rq(f'delete {{ ?s ?p ?o }} where {{ bind({graph_uri.as_turtle()} as ?s) {{ ?s ?p ?o }} }}')]

    #ipdb.set_trace()
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)

def do_copy(w_config, source_path, dest_path):
    print("do_copy:", source_path, dest_path)

    source_graph_uri = get_kgm_graph(w_config, source_path)
    if source_graph_uri is None:
        print(f"no graph at source path {source_path}")
        return

    dest_graph_uri = get_kgm_graph(w_config, dest_path)
    if dest_graph_uri is not None:
        print(f"there is a graph at dest path {dest_path}: {dest_graph_uri}, giving up")
        return    
    del dest_graph_uri
    
    dest_graph_uri = create_kgm_graph(w_config, dest_path)    
    rq_queries = [make_rq(f'insert {{ <{dest_graph_uri.uri}> kgm:path "{dest_path}"; ?p ?o }} where {{ <{source_graph_uri.uri}> ?p ?o filter(?p != kgm:path) }}'),
                  make_rq(f'copy <{source_graph_uri.uri}> to <{dest_graph_uri.uri}>')]
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)
    
    
def do_rename(w_config, path, new_path):
    print("do_rename:", path, new_path)

    graph_uri = get_kgm_graph(w_config, path)
    if graph_uri is None:
        print(f"no graph at path {path}")
        return

    new_graph_uri = get_kgm_graph(w_config, new_path)
    if new_graph_uri is not None:
        print(f"there is a graph at new path {new_path}: {new_graph_uri}, giving up")
        return
    del new_graph_uri
    
    rq_queries = [make_rq(f'delete data {{ {graph_uri.as_turtle()} kgm:path "{path}" }}'),
                  make_rq(f'insert data {{ {graph_uri.as_turtle()} kgm:path "{new_path}" }}')]
    for rq in rq_queries:
        print(rq)
        rq_update(rq, config = w_config)

def do_show(w_config, curie):
    rq = make_rq(f"""
    select ?uo ?uo_member ?uo_member_value {{ 
      graph ?g
      {{ 
        bind({curie} as ?s_uo)
        ?uo ?uo_member ?uo_member_value 
        filter(!(?uo_member in (sh:property, sh:path, sh:datatype, sh:class, sh:minCount, sh:maxCount, dash:closedByType, sh:closed)))
        filter(!(?uo_member_value in (sh:NodeShape, rdfs:Class)))
        ?s_uo (<>|!<>)* ?uo .
      }}
    }}
    """)
    #print(rq)

    #ipdb.set_trace()
    rq_res = rq_select(rq, config = w_config)
    print(pd.DataFrame(rq_res).map(lambda x: x.as_turtle()))

def do_graph_select(w_config, select_query):
    query_text = make_rq(select_query)

    print("got query:")
    print(query_text)
    print("---")
    rq_res = rq_select(query_text, config = w_config)
    print(rq_res)

