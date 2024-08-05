To generate .png files used in KGM docs use commands below:

```
kgm misc graphviz --ttl-file ../alice-bob/ab.data.ttl
kgm misc graphviz --ttl-file ../alice-bob/ab.shacl.ttl --construct-query construct-shacl-viz-graph.rq
kgm misc sparql-select --ttl-file ./ab.shacl.ttl --select-query show-shacl.rq
```

SHACL cli download: https://repo1.maven.org/maven2/org/topbraid/shacl/1.4.3/shacl-1.4.3-bin.zip

SHACL validation run:
```
sh ~/local/shacl-1.4.3/bin/shaclvalidate.sh -datafile ./ab.data.ttl -shapesfile ./ab.shacl.ttl
```

Misc queries:

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
prefix gse: <gse:>
prefix ab: <ab:>

select ?s ?s_name ?pet_name where {
 ?g gse:path "/alice-bob/simple"
 graph ?g {
    ?s rdf:type ab:Human; ab:name ?s_name .
    ?s ab:likes ab:pop-music.
   optional {?pet ab:ownedBy ?s; ab:name ?pet_name}
 }
}
```

