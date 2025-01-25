import ipdb
import click
import pandas as pd
from kgm.database import Database
from kgm.kgm_utils import *
from kgm.kgm_graph import KGMGraph

@click.command("init", help = "initialize server")
@click.option("-r", "--reset", is_flag = True, help = "reset already initialized server")
@click.pass_context
def do_init(ctx, reset):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    
    #ipdb.set_trace()
    rq = "select ?s { ?s rdf:type kgm:DefaultServerGraph }"
    rq_res = db.rq_select(rq)

    if len(rq_res["s"]) > 0:
        if not reset:
            raise Exception("kgm init failed: server is already initialized")
        else:            
            print("removing default graph")
            ipdb.set_trace()
            rq = "delete { ?s ?p ?o } where { ?s ?p ?o }"
            db.rq_update(rq)
        
    print("making kgm default graph")

    """
    # this docsstring is for references only
    class kgm:RDFPrefix
      kgm:prefix xsd:string
      kgm:prefix_uri xsd:string
    end

    class kgm:DefaultServerGraph
      kgm:fuseki_dataset_name xsd:string
      kgm:well_known_prefixes kgm:RDFPrefix[6..6]
      kgm:locally_known_prefixes kgm:RDFPrefix[0..n]
    end

    class kgm:Graph
      kgm:path xsd:string
      kgm:dependent_graphs xsd:string[0..n] # dependent graphs idenitied by pathes
    end
    """
    
    ipdb.set_trace()    
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
    sh:property [ sh:path kgm:included_graphs; sh:datatype xsd:string; sh:minCount 0];
    .
    """)

    raw_rq.append('kgm:dsg rdf:type kgm:DefaultServerGraph; kgm:fuseki_dataset_name "kgm-default-dataset" .')

    for prefix, prefix_uri in db.prefix_man.prefixes.items():
        raw_rq.append(f"""\
        kgm:dsg kgm:known_prefixes [ 
          rdf:type kgm:RDFPrefix; 
          kgm:prefix "{prefix}"; 
          kgm:prefix_uri "{prefix_uri}"
        ].
        """)        

    raw_rq = "\n".join(raw_rq)
    update_rq = f"""\
    insert data {{
      {raw_rq}
    }}
    """

    ipdb.set_trace()
    db.rq_update(update_rq)    
    
@click.command("show-config")
@click.pass_context
def show_config(ctx):
    w_config_name, w_config = ctx.obj["config"]
    print("current config name:", w_config_name)
    print("current config:", w_config)

@click.command("ls", help = "lists available graphs")
@click.argument("path", required = False)
@click.pass_context
def graph_ls(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    do_ls(db, path_mask = path)

def do_ls(db, path_mask):
    #print("do_ls:", path)
    query = "select ?kgm_path ?g { ?g rdf:type kgm:Graph; kgm:path ?kgm_path }"
    #print(query)
    #ipdb.set_trace()
    
    res = db.rq_select(query)
    print(pd.DataFrame(res).map(lambda x: x.as_turtle()))
    
@click.command("new", help = "creates new empty graph at given path")
@click.argument("path", required = True)
@click.pass_context
def graph_new(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    do_new(db, path)

def do_new(db, path):
    print("do_graph_new:", path)
    graph_uri = get_kgm_graph(db, path)
    if graph_uri is not None:
        print(f"graph exists on path {path}, giving up, graph was {graph_uri}")
        return
    del graph_uri

    #ipdb.set_trace()
    graph_uri = create_kgm_graph(db, path)
    print(f"created graph at path {path}: {graph_uri}")
    
@click.command("cat", help = "prints graph to stdout")
@click.argument("path", required = True)
@click.option("--as-ksd", is_flag = True)
@click.pass_context
def graph_cat(ctx, path, as_ksd):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    if as_ksd:
        mod_ksd_parser.KSDParser.dump_ksd(db, path)
    else:
        do_cat(db, path)

def do_cat(db, path):
    graph_uri = get_kgm_graph(db, path)
    if graph_uri is None:
        print(f"can't find graph at path {path}", file = sys.stderr)
        return

    kgm_g = KGMGraph(db, graph_uri, None)
    
    rq = f"""
    construct {{ 
      ?s ?p ?o 
    }}
    {kgm_g.get_from_clause__()}
    where {{
      ?s ?p ?o
    }} order by ?s ?p ?o
    """
    print(rq)
    g = db.rq_construct(rq)
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

@click.command("remove", help = "removes graph")
@click.argument("path", required = True)
@click.pass_context
def graph_remove(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    do_remove(db, path)

def do_remove(db, path):
    graph_uri = get_kgm_graph(db, path)
    if graph_uri is None:
        print(f"can't find graph at path {path}")
        return
    
    rq_queries = [f"drop graph {graph_uri.as_turtle()}",
                  f'delete {{ ?s ?p ?o }} where {{ bind({graph_uri.as_turtle()} as ?s) {{ ?s ?p ?o }} }}']

    #ipdb.set_trace()
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)

    
@click.command("copy", help = "copy graph to new path")
@click.argument("source-path", required = True)
@click.argument("dest-path", required = True)
@click.pass_context
def graph_copy(ctx, source_path, dest_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    do_copy(db, source_path, dest_path)

def do_copy(db, source_path, dest_path):
    print("do_copy:", source_path, dest_path)

    source_graph_uri = get_kgm_graph(db, source_path)
    if source_graph_uri is None:
        print(f"no graph at source path {source_path}")
        return

    dest_graph_uri = get_kgm_graph(db, dest_path)
    if dest_graph_uri is not None:
        print(f"there is a graph at dest path {dest_path}: {dest_graph_uri}, giving up")
        return    
    del dest_graph_uri
    
    dest_graph_uri = create_kgm_graph(db, dest_path)    
    rq_queries = [f'insert {{ {dest_graph_uri.as_turtle()} kgm:path "{dest_path}"; ?p ?o }} where {{ {source_graph_uri.as_turtle()} ?p ?o filter(?p != kgm:path) }}',
                  f'copy {source_graph_uri.as_turtle()} to {dest_graph_uri.as_turtle()}']
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)

    
@click.command("rename", help = "changes the path of the graph leaving graph content intact")
@click.argument("path", required = True)
@click.argument("new-path", required = True)
@click.pass_context
def graph_rename(ctx, path, new_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    do_rename(db, path, new_path)

def do_rename(db, path, new_path):
    print("do_rename:", path, new_path)

    graph_uri = get_kgm_graph(db, path)
    if graph_uri is None:
        print(f"no graph at path {path}")
        return

    new_graph_uri = get_kgm_graph(db, new_path)
    if new_graph_uri is not None:
        print(f"there is a graph at new path {new_path}: {new_graph_uri}, giving up")
        return
    del new_graph_uri
    
    rq_queries = [f'delete data {{ {graph_uri.as_turtle()} kgm:path "{path}" }}',
                  f'insert data {{ {graph_uri.as_turtle()} kgm:path "{new_path}" }}']
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)

@click.command("import", help = "import ttl file into the graph")
@click.argument("path", required = True)
@click.argument("ttl_file", required = True)
@click.pass_context
def graph_import(ctx, path, ttl_file):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    do_import(db, path, ttl_file)

def parse_ttl(prefix_man, source):
    g = rdflib.Graph()
    g.parse(source, format = "turtle")
    triples = []
    for s, p, o in g:
        new_spo = []
        for r in [s, p, o]:
            #print(r)
            if type(r) == rdflib.URIRef:
                new_spo.append(URI(prefix_man.collapse_prefix(r.toPython())))
            elif type(r) == rdflib.BNode:
                new_spo.append(BNode(r.toPython()))
            elif type(r) == rdflib.Literal:
                new_spo.append(Literal(r.toPython(), URI(prefix_man.collapse_prefix(r.datatype.toPython()))))
            else:
                raise Exception("parse_ttl conversion failed")
        triples.append(new_spo)
    
    return triples
        
def do_import(db, path, ttl_file):
    print("do_import:", path, ttl_file)
    #ipdb.set_trace()
    
    graph_uri = get_kgm_graph(db, path)
    if graph_uri is not None:
        print(f"graph at path {path} already exists:", graph_uri)
        return
    del graph_uri

    #ipdb.set_trace()
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            source_triples = parse_ttl(db.prefix_man, fd)
    else:
        source_triples = parse_ttl(db.prefix_man, ttl_file)
    
    #ipdb.set_trace()
    graph_uri = create_kgm_graph(db, path)
    db.rq_insert_triples(source_triples, graph_uri)

    print(path, graph_uri)

    
@click.command("show", help = "shows details about given URI")
@click.argument("uri", required = True)
@click.pass_context
def graph_show(ctx, uri):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    do_show(db, uri)

def do_show(db, curie):
    rq = f"""
    select ?uo ?uo_member ?uo_member_value {{ 
      graph ?g
      {{ 
        bind({curie} as ?s_uo)
        ?uo ?uo_member ?uo_member_value .
        ?s_uo (<>|!<>)* ?uo .
      }}
    }}
    """
    #print(rq)

    #ipdb.set_trace()
    rq_res = db.rq_select(rq)
    print(pd.DataFrame(rq_res).map(lambda x: x.as_turtle()))

