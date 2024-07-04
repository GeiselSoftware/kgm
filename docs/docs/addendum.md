# Addendum
## Appendix A: kgm: prefix definitions

kgm prefix URI - `http://www.geisel-software.com/kgm#`

kgm root subject is to be stored in default graph and has URI `kgm:root`, full URI `<http://www.geisel-software.com/kgm#root>`.

kgm predicates:

- kgm:has-a
- kgm:path
- kgm:graph-uri

### kgm: prefix

**kgm:** is prefix introduced for KGM users. It defines set of RDF predicates used to specify how certain RDF graph is stored in GDB server:
```
@prefix mydata: <mydata:> .
@prefix kgm: <http://www.geisel-software.com/kgm#> .

mydata:g1 rdf:type kgm:PlainGraph .
mydata:g1 kgm:path "/G1" .
mydata:g1 kgm:graph-uri <...> .
mydata:g2 rdf:type kgm:SHACLGraph .
mydata:g2 kgm:graph-uri <...> .
mydata:g1 kgm:shacl-graph mydata:g2 .
```

## Appendix B: SHACL notes

Example of SHACL definitions: [https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl](https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl)

TopQuandrant SHACL implementation: https://github.com/TopQuadrant/shacl
Validate script located at `src/main/command/`, file `shaclvalidate.sh`
Use binary distrib from https://repo1.maven.org/maven2/org/topbraid/shacl/


