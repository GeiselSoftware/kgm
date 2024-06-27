#import ipdb
import sys, io
import rdflib
import rdflib.tools.rdf2dot
import graphviz

if __name__ == "__main__":
    init_bindings = {}
    if len(sys.argv) > 1:
        init_bindings = {'s': rdflib.URIRef("ab:alice")}
    else:
        init_bindings = {'s': rdflib.URIRef("rdf:nil")}
        
    ttl_files = ["./data.shacl.ttl", "./data.ttl"]
    #ttl_files = ttl_files[:-1]
    g = rdflib.Graph()
    for ttl_file in ttl_files:
        print(ttl_file, file = sys.stderr)
        g.parse(ttl_file)

    ng = g.query("""
    prefix ab: <ab:>
    construct {
      #?st rdf:type rdfs:Class.
      ?st ?dm_name_uri ?dm_t_s.
      ?st ?cm_name_uri ?cm_t; ?cm_name_uri ?cm_t_s .
      ?s rdf:type ?sst . ?o rdf:type ?ot .
      ?s ?p ?o. ?o ?pp ?oo
    } where { 
      ?st rdf:type rdfs:Class .
      optional {?st sh:property [sh:path ?dm_name_uri; sh:dataclass ?dm_t] bind (str(?dm_t) as ?dm_t_s)}
      optional {?st sh:property [sh:path ?cm_name_uri; sh:class ?cm_t] bind (str(?cm_t) as ?cm_t_s)}
      optional {?s rdf:type ?sst .
      ?s ?p ?o . ?o ?pp ?oo filter(?pp not in (sh:property, rdf:type)) . ?o rdf:type ?ot }
    }
    """, initBindings = init_bindings)

    pdf_file = "graph.pdf"
    #print("\n".join([f"{t}" for t in ng.graph]))
    dot_output = io.StringIO()
    rdflib.tools.rdf2dot.rdf2dot(ng.graph, dot_output)
    dot_output.seek(0)

    dot_data = dot_output.getvalue()
    if not dot_data.strip():
        print("No DOT data was generated.")
        sys.exit(2)
        
    graph = graphviz.Source(dot_data)
    pdf_data = graph.pipe(format='pdf')
    
    with open(pdf_file, "wb") as f:
        f.write(pdf_data)        
        print(f"PDF generated: {pdf_file}")
        

    
