#import ipdb
import click, sys
import pandas as pd
import rdflib
from kgm.database import Database
from kgm.kgm_graph import KGMGraph
from kgm.rdf_terms import URI, BNode, Literal, RDFTriple
from kgm.rdf_utils import to_turtle
from kgm.prefixes import xsd

from . import ksd_parser as mod_ksd_parser
from . import kgm_validate

@click.group()
def graph():
    pass

@graph.command("ls", help = "lists available graphs")
@click.argument("path", required = False)
@click.pass_context
def graph_ls(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)

    #print("do_ls:", path)
    #ipdb.set_trace()
    query = "select ?kgm_path ?g { ?g rdf:type kgm:Graph; kgm:path ?kgm_path }"
    res = db.rq_select(query)
    print(pd.DataFrame(res).map(lambda x: to_turtle(x, db.w_prefixes)))


@graph.command("new", help = "creates new empty graph at given path")
@click.argument("path", required = True)
@click.pass_context
def graph_new(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    graph_uri = db.get_kgm_graph(path)
    if graph_uri is not None:
        print(f"graph exists on path {path}, giving up, graph was {graph_uri}")
        return
    del graph_uri

    #ipdb.set_trace()
    graph_uri = db.create_kgm_graph(path)
    print(f"created graph at path {path}: {graph_uri}")

@graph.command("remove", help = "removes graph")
@click.argument("path", required = True)
@click.pass_context
def graph_remove(ctx, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    graph_uri = db.get_kgm_graph(path)
    if graph_uri is None:
        print(f"can't find graph at path {path}")
        return

    rq_queries = [f"drop graph {to_turtle(graph_uri, db.w_prefixes)}",
                  f'delete {{ ?s ?p ?o }} where {{ bind({to_turtle(graph_uri, db.w_prefixes)} as ?s) {{ ?s ?p ?o }} }}']

    #ipdb.set_trace()
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)
    
@graph.command("copy", help = "copy graph to new path")
@click.argument("source-path", required = True)
@click.argument("dest-path", required = True)
@click.pass_context
def graph_copy(ctx, source_path, dest_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    print("do_copy:", source_path, dest_path)

    source_graph_uri = db.get_kgm_graph(source_path)
    if source_graph_uri is None:
        print(f"no graph at source path {source_path}")
        return

    dest_graph_uri = db.get_kgm_graph(dest_path)
    if dest_graph_uri is not None:
        print(f"there is a graph at dest path {dest_path}: {dest_graph_uri}, giving up")
        return    
    del dest_graph_uri
    
    dest_graph_uri = db.create_kgm_graph(dest_path)    
    rq_queries = [f'''
                  insert {{
                    {to_turtle(dest_graph_uri, db.w_prefixes)} kgm:path "{dest_path}"; ?p ?o
                  }}
                  where {{
                    {to_turtle(source_graph_uri, db.w_prefixes)} ?p ?o filter(?p != kgm:path)
                  }}
                  ''',
                  f'''
                  insert {{
                    graph {to_turtle(dest_graph_uri, db.w_prefixes)} {{ ?s ?p ?o }}
                  }} where {{
                    graph {to_turtle(source_graph_uri, db.w_prefixes)} {{ ?s ?p ?o }}
                  }}
                  '''
                  ]
    #ipdb.set_trace()
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)
    
@graph.command("rename", help = "changes the path of the graph leaving graph content intact")
@click.argument("path", required = True)
@click.argument("new-path", required = True)
@click.pass_context
def graph_rename(ctx, path, new_path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)
    print("do_rename:", path, new_path)

    graph_uri = db.get_kgm_graph(path)
    if graph_uri is None:
        print(f"no graph at path {path}")
        return

    new_graph_uri = db.get_kgm_graph(new_path)
    if new_graph_uri is not None:
        print(f"there is a graph at new path {new_path}: {new_graph_uri}, giving up")
        return
    del new_graph_uri
    
    rq_queries = [f'delete data {{ {to_turtle(graph_uri, db.w_prefixes)} kgm:path "{path}" }}',
                  f'insert data {{ {to_turtle(graph_uri, db.w_prefixes)} kgm:path "{new_path}" }}']
    for rq in rq_queries:
        print(rq)
        db.rq_update(rq)
    
    
@graph.command("select")
@click.argument("path", required = True)
@click.argument("query", required = True)
@click.pass_context
def do_graph_select(ctx, path, query):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    kgm_g_uri = db.get_kgm_graph(path)
    if kgm_g_uri is None:
        raise Exception(f"can't find kgm path {path}")
    kgm_g = KGMGraph(db, kgm_g_uri, None)
    rq_res = kgm_g.select_in_current_graph(query)
    print(pd.DataFrame(rq_res))


@graph.command("cat", help = "prints graph to stdout")
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
    graph_uri = db.get_kgm_graph(path)
    if graph_uri is None:
        print(f"can't find graph at path {path}", file = sys.stderr)
        return

    rq = f"""
    construct {{ 
      ?s ?p ?o 
    }}
    from <{graph_uri}>
    where {{
      ?s ?p ?o
    }} order by ?s ?p ?o
    """
    #print(rq)
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

def parse_ttl(source):
    #ipdb.set_trace()
    g = rdflib.Graph()
    g.parse(source, format = "turtle")
    triples = []
    for s, p, o in g:
        new_spo = []
        for r in [s, p, o]:
            #print(r)
            if type(r) == rdflib.URIRef:
                new_spo.append(URI(r.toPython()))
            elif type(r) == rdflib.BNode:
                new_spo.append(BNode(r.toPython()))
            elif type(r) == rdflib.Literal:
                #ipdb.set_trace()
                value, datatype = r.n3().split("^^")
                new_spo.append(Literal(value[1:-1], URI(datatype[1:-1])))
            else:
                raise Exception("parse_ttl conversion failed")
            
        t = RDFTriple(*new_spo)
        triples.append(t)
    
    return triples
        

@graph.command("import", help = "import ttl file into the graph")
@click.argument("path", required = True)
@click.argument("ttl_file", required = True)
@click.pass_context
def graph_import(ctx, path, ttl_file):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(fuseki_url)    
    print("do_import:", path, ttl_file)
    #ipdb.set_trace()
    
    graph_uri = db.get_kgm_graph(path)
    if graph_uri is not None:
        print(f"graph at path {path} already exists:", graph_uri)
        return
    del graph_uri

    #ipdb.set_trace()
    if ttl_file.startswith("http"):
        ttl_file_url = ttl_file
        with urllib.request.urlopen(ttl_file_url) as fd:
            source_triples = parse_ttl(fd)
    else:
        source_triples = parse_ttl(ttl_file)
    
    #ipdb.set_trace()
    graph_uri = db.create_kgm_graph(path)
    db.rq_delete_insert(graph_uri, [[],source_triples])

    print(path, graph_uri)

@graph.command("validate")
@click.argument("shacl-path")
@click.argument("path")
@click.pass_context
def do_validate(ctx, shacl_path, path):
    _, w_config = ctx.obj["config"]
    fuseki_url = w_config['backend-url']
    db = Database(path, fuseki_url)    
    kgm_validate.do_validate(db, shacl_path, path)
