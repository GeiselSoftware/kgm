#import ipdb
import os.path
import rdflib
from .. import graphviz_utils

import http.server
import socketserver
import os

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

def do_misc_select(ttl_file, select_query):
    g = rdflib.Graph()
    g.parse(ttl_file)
    print("loaded", len(g), "triples")

    with open(select_query) as fd:
        query_text = fd.read()
        print("got query:")
        print(query_text)
        print("---")
        rq_res = g.query(query_text)
        ipdb.set_trace()
        #df = pd.DataFrame(columns = [str(x) for x in rq_res.vars], 
        print([str(x) for x in rq_res.vars])
        print("-------")
        for row in rq_res:
            print([str(x) for x in row], len(row))

def do_misc_wasmtest():
    #ipdb.set_trace()
    HOST = "0.0.0.0"
    PORT = 8000
    DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kgm-wasm"))
    print("DIRECTORY:", DIRECTORY)
    
    # Change the current working directory to the serve directory
    os.chdir(DIRECTORY)

    # Create the handler to serve files
    Handler = http.server.SimpleHTTPRequestHandler

    # Create and start the HTTP server
    with socketserver.TCPServer((HOST, PORT), Handler) as httpd:
        print(f"Serving HTTP on {HOST} port {PORT} (http://{HOST}:{PORT}/) ...")
        httpd.serve_forever()
