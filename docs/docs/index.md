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

[RDF (Resource Definition Framework)](https://www.w3.org/TR/rdf11-concepts/) is the standardized way to create knowledge graphs. The idea of RDF is simple: all facts are stored as triples i.e. statement which always has three parts: *subject*, *predicate* and *object*. E.g. first triple in example above introduces triple with subject `:alice`, predicate `rdf:type` and object `foaf:Human`.

You may think about RDF triples as extention of an idea of key-value pairs. Key-value pair has two parts: kay and value. The type of key and value may vary. You may have keys as strings and values as numbers, string - anything you can type into the file editor. E.g. you may have such KV pairs shown as CSV file fragment:

```
Key,Value
Alice,Human
Alice_height,5 feet 9 inch
Bob,Human
Bob_height,6 feet
```

RDF makes two changes to key-value pairs idea. First it adds third element so you now will have subject-predicate-object triples instead of key-value pairs. And then RDF restricts what could be subject, predicate and object. In most cases the parts of RDF triple will be either [URIs](https://en.wikipedia.org/wiki/Uniform_Resource_Identifier) or [xsd literals](https://www.w3.org/TR/xmlschema-2/#built-in-datatypes).

I.e. to have RDF triples to be compliant you have to make sure that subject 

In this first triple we see example where all three part are *URIs* (Universal Resource Identifier). RDF/turtle allows to use URI in shortened form. The same example where all URIs are complete would look like this:

```
<http://example.com/#alice> <...:type> <...:Human> .
<http://example.com/#alice> <...:name> "Alice" .
```

In this example URIs are strings between angle brackets - but brakets are not part of URI. E.g. first line subject is URI `http://example.com/#alice`. URI is very often look like URL. However it is very likely you will not be able to get anything from such URI if you try to point your internet browser to that location. URI are just strings with certain requirements, they are used to identify the `resource`.

In second line of the example you've seen that object could also be present as *literal*. In RDF/turle literals are in double-quotes to distibguish them from URIs. Doble-quotes are not part of the literal: second statement object is string `Alice`.

If you want to shorten the statement you can use *prefix* defined on top of RDF/turtle file. Prefixes are used to construct full URI from shortened form. The shortened form was used in first example: you can just substitute prefix value with prefix URI as given at the top of the file. Shortened URI look different from full URI: then never enclosed to angle brakets. They are also different from literals: no double-quote encloser.

## Graph store explorer (gse)

### Installation

```
python3 -m venv ~/venv/gse
source ~/venv/gse/bin/activate
cd shacled/utils

```

### Usage

**gse** is command-line utility to facilitate the tasks which could be described as 'graph store exploration'.

Given .ttl file it is possible to upload the content into GDB using `gse insert` command. This operation allow to specify **gse path** to resulting graph in GDB.

```
> ./gse insert --gse-path /alice-bob/simple --ttl-file ../examples/alice-bob/simple/data.ttl
... tbc
> ./gse ls
         gse_path                                         graph_uri
/alice-bob/simple <gse:Graph##03027263-2242-454b-8d4d-7aaecb9990ae>
```

## Fuseki

[Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) is open-source RDF/SPARQL server.

### Fuseki server install and operation

Use archive apache-jena-fuseki-5.0.0. Unpack that to location `FUSEKI_HOME`.

To create run database server use command:

```
cd $FUSEKI_HOME
./fuseki-server --update --loc=run/databases /gse
```

At this point you should be able to access fuseki server via webbrowers at port 3030. You should find single dataset /gse.

Logging destination: $FUSEKI_HOME/run/logs/stderrout.log
To observe http requests modify file ${FUSEKI_HOME}/webapp/log4j2.properties. You need to set property `logger.fuseki-request.level`:

```
logger.fuseki-request.level                  = DEBUG
```
