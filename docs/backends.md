# Fuseki Setup

[Apache Jena Fuseki](https://jena.apache.org/documentation/fuseki2/) is open-source RDF/SPARQL server. The steps below are to have Fuseki server configured and run to be used as shacled GSE backend.

## Install

Fuseki can be downloaded from [Apache Jena Releases](https://jena.apache.org/download/index.cgi)<br/>
Use binary distribution archive `apache-jena-fuseki-5.0.0.tar.gz` Unpack that to location `FUSEKI_HOME`.

## Server Setup

### Quick test run

To run database server use command:

```
cd $FUSEKI_HOME
./fuseki-server --update --loc=/tmp/test-databases /vgm
```

At this point you should be able to access fuseki server via webbrowers at port 3030. You will have single dataset /vgm.
If you want to observe http requests you need to modify file ${FUSEKI_HOME}/webapp/log4j2.properties. You need to set property `logger.fuseki-request.level`:

```
logger.fuseki-request.level                  = DEBUG
```

After that server log will include HTTP requests processed by server.

You should also be able to upload data using browser UI provided by server at port 3030.

## Setup using configuration file.

You can also run fuseki using config file instead of specifing command-line options. You can use `$FUSEKI_HOME/run/config.ttl` existing in distribution or create your own.
The reason why you might want to do that it allows you to configure fuseki server in the way not accessible using command-line options.

```
cd $FUSEKI_HOME
./fuseki-server
```

The command above uses top run directory `$FUSEKI_HOME/run` and takes default configuration from file `$FUSEKI_HOME/run/config.ttl`. Jena github has [exhaustive list of example configurations](https://github.com/apache/jena/tree/main/jena-fuseki2/examples) you can try to experiment with. You can copy log4j config file from `$FUSEKI/webapp` to that run directory and tune up logging. 

### Test SHACL endpoint

Place SHACL config file to `$FUSEKI_HOME/run` and start fuseki:

```
cd $FUSEKI_HOME
wget -O run/config-shacl.ttl https://raw.githubusercontent.com/apache/jena/main/jena-fuseki2/examples/config-shacl.ttl
./fuseki-server --config=run/config-shacl.ttl
```

This fuseki server configuration will create transient in-memory dataset named as `/dataset` and configure additional SHACL endpoint. You can use VGM supplied Alice-Bob example files to test SHACL validation:

```
curl -XPOST --data-binary @$VGM_HOME/examples/alice-bob/ab.ttl  --header 'Content-type: text/turtle' http://localhost:3030/dataset?default
curl -XPOST --data-binary @$VGM_HOME/examples/alice-bob/ab.shacl.ttl  --header 'Content-type: text/turtle' http://localhost:3030/dataset/shacl?graph=default
```
See also [Integration with Apache Jena Fuseki](https://jena.apache.org/documentation/shacl/index.html#integration-with-apache-jena-fuseki)

### Default VGM setup

By default VGM should have persistent `/vgm-default-dataset` dataset and SHACL endpoint configured as below. The location of TDB2 directory is `$FUSEKI_HOME/vgm-default-dataset`.

```
# based on https://github.com/apache/jena/tree/main/jena-fuseki2/examples

PREFIX :        <#>
PREFIX fuseki:  <http://jena.apache.org/fuseki#>
PREFIX rdf:     <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX ja:      <http://jena.hpl.hp.com/2005/11/Assembler#>
PREFIX tdb2:    <http://jena.apache.org/2016/tdb#>

[] rdf:type fuseki:Server; fuseki:services ( :service ). # see also https://www.w3.org/TR/rdf12-turtle/#collections

:service rdf:type fuseki:Service;
    fuseki:name "vgm-default-dataset";
    fuseki:dataset :dataset_tdb2;
    fuseki:endpoint [ fuseki:operation fuseki:query; fuseki:name "query" ];
    fuseki:endpoint [ fuseki:operation fuseki:update; fuseki:name "update" ];
    fuseki:endpoint [ fuseki:operation fuseki:shacl; fuseki:name "shacl" ];
.

:dataset_tdb2 rdf:type  tdb2:DatasetTDB2;
              tdb2:location "vgm-default-dataset"; # the tbd2 direction is relative to FUSEKI_HOME, look it up in server log output
## Optional - with union default for query and update WHERE matching.
## tdb2:unionDefaultGraph true ;
.
```

Save config above into `$FUSEKI_HOME/run/config-vgm.ttl`. Then run server:
```
cd $FUSEKI_HOME
./fuseki-server --config=run/config-vgm.ttl
```
   
Alice-Bob upload and SHACL validation test:
```
curl -XPOST --data-binary @$VGM_HOME/examples/alice-bob/ab.ttl  --header 'Content-type: text/turtle' http://localhost:3030/vgm-default-dataset?default
curl -XPOST --data-binary @$VGM_HOME/examples/alice-bob/ab.shacl.ttl  --header 'Content-type: text/turtle' http://localhost:3030/vgm-default-dataset/shacl?graph=default
```

Code location: https://github.com/apache/jena/blob/b31a480975d9cf511ae0d5f2c11a3898b453d664/jena-fuseki2/jena-fuseki-core/src/main/java/org/apache/jena/fuseki/servlets/SHACL_Validation.java#L66
