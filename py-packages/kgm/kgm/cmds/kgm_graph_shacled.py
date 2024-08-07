import http.server
import socketserver
import socket
import os
from ..kgm_utils import get_kgm_graph

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
            
def do_graph_shacled(w_config, path, public_access):
    print(f"checking path {path}")
    graph_curie, _ = get_kgm_graph(w_config, path)
    if graph_curie is None:
        print(f"can't find graph on path {path}, giving up")
        return
    
    #ipdb.set_trace()
    if public_access:
        bind_host = "0.0.0.0"
        HOST = socket.gethostname()
    else:
        bind_host = HOST = "localhost"
        
    PORT = 8000
    DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kgm-wasm"))
    print("DIRECTORY:", DIRECTORY)

    print(f"use this URL to access shacled: http://{HOST}:{PORT}/run-shacled.html?fuseki-host=h1&fuseki-port=3030&kgm-path={path}")
    launch_http_server(bind_host, PORT, DIRECTORY)
