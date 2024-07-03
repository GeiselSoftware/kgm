import io
import rdflib
import rdflib.tools.rdf2dot
import graphviz

def generate_png(g: rdflib.Graph, png_file):
    #print("\n".join([f"{t}" for t in ng.graph]))
    dot_output = io.StringIO()
    rdflib.tools.rdf2dot.rdf2dot(g, dot_output)
    dot_output.seek(0)

    dot_data = dot_output.getvalue()
    if not dot_data.strip():
        print("No DOT data was generated.")
        sys.exit(2)
        
    g_source = graphviz.Source(dot_data)
    png_data = g_source.pipe(format='png')
    
    with open(png_file, "wb") as f:
        f.write(png_data)        

