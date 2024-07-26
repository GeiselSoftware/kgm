# Addendum
## Appendix A: prefixes

Prefixes often mentioned in KGM docs, code and examples are:

- *kgm:* - main KGM prefix. Used to construct KGM definitions stored in default graph. It also containes some auxiliarly predicates which are used by KGM vizual applications.
- *ab:* - Alice-Bob examples
- *nw:* - NorthWind examples

### Prefix *kgm:*

*kgm:* is prefix introduced for KGM users. It defines set of RDF predicates used to specify how certain RDF graph is stored in GDB server:
```
@prefix kgm: <http://www.geisel-software.com/RDF/KGM#> .
@prefix mydata: <mydata:> .

mydata:g1 rdf:type kgm:DataGraph .
mydata:g1 kgm:path "/G1" .
mydata:g2 rdf:type kgm:SHACLGraph .
mydata:g2 kgm:path "/G1.shacl" .
mydata:g2 kgm:is-shacl-graph-for mydata:g1 .
```

kgm predicates:

- kgm:has-a
- kgm:path
- kgm:graph-uri


### Well-known prefixes
```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix dash: <http://datashapes.org/dash#> .
```

### KGM example prefixes
```
@prefix ab: <http://www.geisel-software.com/RDF/alice-bob#> .
@prefix nw: <http://www.geisel-software.com/RDF/NorthWind#> .
```

## Appendix B: SHACL notes

Example of SHACL definitions: [https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl](https://github.com/pyjanitor-devs/pyjviz/blob/main/rdflog.shacl.ttl)

TopQuandrant SHACL implementation: [https://github.com/TopQuadrant/shacl](https://github.com/TopQuadrant/shacl)

Validate script located at `src/main/command/`, file `shaclvalidate.sh`
Use binary distrib from https://repo1.maven.org/maven2/org/topbraid/shacl/


