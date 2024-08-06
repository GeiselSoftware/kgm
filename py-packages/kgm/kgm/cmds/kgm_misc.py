#import ipdb
import os.path
import rdflib
from .. import graphviz_utils

import http.server
import socketserver
import socket
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


class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socketserver.TCPServer.server_bind(self)

def launch_http_server(host, port, directory):
    # Change the working directory to serve files from the specified directory
    os.chdir(directory)
    
    # Define handler to serve the files
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Create the server with specified host and port using the custom TCPServer
    httpd = ReuseAddrTCPServer((host, port), Handler)
    
    print(f"Serving HTTP on {host} port {port} (http://{host}:{port}/) ...")
    
    # Serve until process is interrupted
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print("Server stopped.")                                                                                                
            
def do_misc_wasmtest():
    #ipdb.set_trace()
    HOST = "0.0.0.0"
    PORT = 8000
    DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kgm-wasm"))
    print("DIRECTORY:", DIRECTORY)

    launch_http_server(HOST, PORT, DIRECTORY)
