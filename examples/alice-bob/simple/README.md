```
sh ~/local/shacl-1.4.3/bin/shaclvalidate.sh -datafile ./data.ttl -shapesfile ./data.shacl.ttl
```

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

```
python -m rdflib.tools.rdf2dot ./data.ttl | xdot -
```
