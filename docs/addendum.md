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

TopQuandrant SHACL implementation: https://github.com/TopQuadrant/shacl
Validate script located at `src/main/command/`, file `shaclvalidate.sh`
Use binary distrib from https://repo1.maven.org/maven2/org/topbraid/shacl/

## Appendix C: Alice-Bob RDF triples

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ab: <ab:>

ab:alice rdf:type ab:Human.
ab:bob rdf:type ab:Human.
ab:charlie rdf:type ab:Human.
ab:amy rdf:type ab:Dog.
ab:luna rdf:type ab:Cat.
ab:mona-lisa rdf:type ab:FamousPainting.
ab:night-watch rdf:type ab:FamousPainting.
ab:leonardo-da-vinci rdf:type ab:Human.
ab:rembrandt rdf:type ab:Human.
ab:paris rdf:type ab:Location.
ab:amsterdam rdf:type ab:Location.
ab:worcester rdf:type ab:Location.
ab:boston rdf:type ab:Location.
ab:pop-music rdf:type ab:MusicGenre.
ab:heavy-metal-music rdf:type ab:MusicGenre.

ab:alice ab:name "Alice"; gse:node_vis_color "green"; ab:livesIn ab:worcester;
         ab:likes ab:mona-lisa; ab:likes ab:pop-music .
ab:bob ab:name "Bob"; gse:node_vis_color "cyan"; ab:livesIn ab:boston;
       ab:likes ab:night-watch; ab:likes ab:heavy-metal-music .
ab:charlie ab:name "Charlie"; gse:node_vis_color "orange"; ab:livesIn ab:worcester;
       ab:likes ab:pop-music .

ab:amy ab:name "Amy"; gse:node_vis_color "brown"; ab:ownedBy ab:alice .
ab:luna ab:name "Luna"; gse:node_vis_color "white"; ab:ownedBy ab:bob .

ab:mona-lisa ab:name "Mona Lisa"; ab:author ab:leonardo-da-vinci; ab:location ab:paris.
ab:night-watch ab:name "Night Watch"; ab:author ab:rembrandt; ab:location ab:amsterdam.

ab:leonardo-da-vinci ab:name "Leonardo Da Vinci".
ab:rembrandt ab:name "Rembrandt".

ab:paris ab:city "Paris"; ab:country "France".
ab:worcester ab:city "Worcester"; ab:country "United States".
ab:boston ab:city "Boston"; ab:country "United Kingdom".
ab:amsterdam ab:city "Amsterdam"; ab:country "Netherlands".

ab:alice ab:friendOf ab:bob .
ab:bob ab:friendOf ab:alice .

ab:pop-music ab:name "Pop music"; ab:averageLength 3.5.
ab:heavy-metal-music ab:name "Heavy Metal"; ab:averageLength 8.0.

```