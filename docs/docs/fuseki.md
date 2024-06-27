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

### Fuseki configuration

https://github.com/apache/jena/tree/main/jena-fuseki2/examples

### SHACL endpoint

https://jena.apache.org/documentation/shacl/index.html#integration-with-apache-jena-fuseki

upload shacl:

```
curl -XPOST --data-binary @ab.shacl.ttl --header 'Content-type: text/turtle' http://metis:3030/gse?default
```

