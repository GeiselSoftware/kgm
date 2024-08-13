import http.server
import socketserver
import socket
import os, base64
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
        FUSEKI_HOST = HOST
        FUSEKI_PORT = 3030
    else:
        FUSEKI_HOST = bind_host = HOST = "localhost"
        FUSEKI_PORT = 3030
        
    PORT = 8000
    DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "kgm-wasm"))
    print("DIRECTORY:", DIRECTORY)

    backend_url = w_config["backend-url"]
    args_d = {"BACKEND_URL": backend_url, "KGM_PATH": path}
    args = base64.b64encode(",".join([f"{k}={v}" for k, v in args_d.items()]).encode('ascii')).decode('ascii')
    #print(args)

    print(f"backend_url: {backend_url}")
    print(f"use this URL to access shacled: http://{HOST}:{PORT}/run-shacled.html?{args}")
    launch_http_server(bind_host, PORT, DIRECTORY)
