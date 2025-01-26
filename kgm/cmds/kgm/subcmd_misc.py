#import ipdb
import click
import os.path
import rdflib
import kgm.graphviz_utils

@click.group("misc")
def misc():
    pass

@misc.command("graphviz")
@click.option("--ttl-file", required = True, help = "RDF/Turtle file")
@click.option("--construct-rq", help = "construct query file")
def do_misc_graphvis(ttl_file, construct_rq):
    do_misc_gv(ttl_file, construct_rq)

def do_misc_gv(ttl_file, construct_query):
    output_png_file = os.path.basename(ttl_file) + ".png"
    
    g = rdflib.Graph()
    g.parse(ttl_file)
    print("loaded", len(g), "triples")

    #ipdb.set_trace()
    if not construct_query is None:
        with open(construct_query) as fd:
            query_text = fd.read()
            print("got query:")
            print(query_text)
            print("---")
            rq_res = g.query(query_text)
            rq_res.graph.namespace_manager = g.namespace_manager # to fix missing namespace bind after construct

            print(f"after contruct: {len(rq_res.graph)} triples")
            #for row in rq_res.graph: print([str(x) for x in row])
            print(f"saving to {output_png_file}")
            graphviz_utils.generate_png(rq_res.graph, png_file = output_png_file)
    else:
        print(f"saving to {output_png_file}")
        graphviz_utils.generate_png(g, png_file = output_png_file)

    print("all done.")        

