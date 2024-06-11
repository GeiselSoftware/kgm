# SHACL editor


## Introduction to GDB

Graph databases store information using graph, more precisely `knowledge graph`. I.e. to store certain facts you don't need to define tables with columns. You can store the facts directly e.g. using `RDF/turtle` format:

```
@prefix rdf: ...
@prefix foaf: ...
@prefix : ...

:alice rdf:type foaf:Human .
:alice foaf:name "Alice".
```

In example above two facts are stored related to proverbal Alice-Bob pair: there is a human named Alice with identity :alice.

RDF (Resource Definition Framework) is the standardized way to create such graphs (also known as knowledge graphs). The idea of RDF is simple: all facts are stored as triples i.e. statement which always has three parts: subject, predicate and object. E.g. first triple in example above introduces triple with subject `:alice`, predicate `rdf:type` and object `foaf:Human`.

In this first triple we see example of triple where all three part are *URIs* (Universal Resource Identifier). RDF/turtle allows to use URI in shortened form. The same example where all URIs are complete would look like this:

```
<http://example.com/#alice> <...:type> <...:Human> .
<http://example.com/#alice> <...:name> "Alice" .
```

In this example URIs are strings between angle brackets - but brakets are not part of URI. E.g. first line subject is URI `http://example.com/#alice`. URI is very often look like URL. However it is very likely you will not be able to get anything from such URI if you try to point your internet browser to that location. URI are just strings with certain requirements, they are used to identify the `resource`.

In second line of the example you've seen that object could also be present as *literal*. In RDF/turle literals are in double-quotes to distibguish them from URIs. Doble-quotes are not part of the literal: second statement object is string `Alice`.

If you want to shorten the statement you can use *prefix* defined on top of RDF/turtle file. Prefixes are used to construct full URI from shortened form. The shortened form was used in first example: you can just substitute prefix value with prefix URI as given at the top of the file. Shortened URI look different from full URI: then never enclosed to angle brakets. They are also different from literals: no double-quote encloser.

## Graph store explorer (gse)

**gse** is command-line utility to facilitate the tasks which could be described as 'graph store exploration'. E.g.

```
> gse ls

  gse_path                                         graph_uri
/test-json <gse:Graph##eba477e9-005c-4eb3-b506-1a48a75726da>
```

The result shows graphs known to gse. For each such graph you will see gse path and graph URI. Graph URI can be used in subsequent SPARQL queries.

Given .ttl file it is possible to upload the content into GDB using `gse insert` command. This operation allow to specify **gse path** to resulting graph in GDB.


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

## Fuseki

[Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) is open-source RDF/SPARQL server.

### Useful commands

```
./fuseki # will start fuseki server in background
ls -ltr run/logs
less run/logs/stderrout.log
```
