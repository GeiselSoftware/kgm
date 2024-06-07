# SHACL editor

[SHACL examples](https://www.slideshare.net/jelabra/shacl-by-example) - not very good one, we need to find or build better.

## Graph store explorer (gse)

**gse** could be one of:

- command-line utility to facilitate the tasks which could be described as 'graph store exploration'. E.g.

```
gse ls
```
- set of RDF predicates used to specify how certain RDF graph is stored in either GDB server or at local filesystem location:
```
@prefix mydata: <..prefix for someone's data graphs..> .
@prefix gse: <https://www.geisel-software.com/RDFprefix/gse#> .

mydata:g1 rdf:type gse:PlainGraph .
mydata:g1 gse:graph-name "G1" .
mydata:g1 gse:graph-uri <...> .
mydata:g2 rdf:type gse:SHACLGraph .
mydata:g2 gse:graph-uri <...> .
mydata:g1 gse:shacl-graph mydata:g2 .
```

## Fuseki

[Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) is open-source RDF/SPARQL server.

### Useful commands

```
./fuseki # will start fuseki server in background
ls -ltr run/logs
less run/logs/stderrout.log
```
