import rdflib
from rdflib import ConjunctiveGraph, Dataset

#g = ConjunctiveGraph() -- default graph is union of all graphs
g = Dataset()

# Load the TriG file
g.parse("trig.trig", format="trig")

# Define the SPARQL query
query = """
   PREFIX eg: <http://example.com/person/>

   SELECT * WHERE { 
      { GRAPH ?g { ?s ?p ?o } }
      union { bind(<g:g> as ?g) ?s ?p ?o }      
   }  
"""

#query = 'select ?g ?s ?p ?o { ?s ?p ?o bind("gg" as ?g) }'

results = g.query(query)

# Print the results
for row in results:
    print(f"Graph: {row.g}, Subject: {row.s}, Predicate: {row.p}, Object: {row.o}")
    #print(row)

