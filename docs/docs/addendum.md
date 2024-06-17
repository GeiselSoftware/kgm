# Addendum
## Appendix A: gse: prefix definitions

gse prefix URI - `http://www.geisel-software.com/gse#`

gse root subject is to be stored in default graph and has URI `gse:root`, full URI `<http://www.geisel-software.com/gse#root>`.

gse predicates:

- gse:has-a
- gse:path
- gse:graph-uri

### gse: prefix

**gse:** is prefix introduced for GSE users. It defines set of RDF predicates used to specify how certain RDF graph is stored in GDB server:
```
@prefix mydata: <mydata:> .
@prefix gse: <http://www.geisel-software.com/gse#> .

mydata:g1 rdf:type gse:PlainGraph .
mydata:g1 gse:path "/G1" .
mydata:g1 gse:graph-uri <...> .
mydata:g2 rdf:type gse:SHACLGraph .
mydata:g2 gse:graph-uri <...> .
mydata:g1 gse:shacl-graph mydata:g2 .
```

## Appendix B: SHACL notes

Example of SHACL definitions: [https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl](https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl)
