# KGM - User Guide

*kgm* is command-line processor utility which allows user to control and manipulate KGM-controlled graphs in backend graph database.

## Installation

*kgm* is part [kgm python package](https://github.com/GeiselSoftware/KGM/tree/main/py-packages/kgm). It can be installed using usual procedures of python package installations.

### local `pip install`

```
python3 -m venv ~/venv/kgm
source ~/venv/kgm/bin/activate
pip install py-packages/kgm
```

## Usage

Given .ttl file it is possible to upload the content into GDB using `kgm insert` command. This operation allow to specify **kgm path** to resulting graph in GDB.

```
> kgm graph add /alice-bob http://geiselsoftware.github.io/KGM-docs/examples/alice-bob/ab.data.ttl
/alice-bob kgm:DataGraph--375b27d0-4ce7-4ae6-a930-3e014d413835
> kgm graph add --kgm-graph-type shacl /alice-bob.shacl http://geiselsoftware.github.io/KGM-docs/examples/alice-bob/ab.shacl.ttl
/alice-bob.shacl kgm:SHACLGraph--6b21e3d9-ee71-484d-b6ab-1f57080f2026

> kgm ls /
        kgm_path                                         graph_uri
      /alice-bob <kgm:DataGraph--375b27d0-4ce7-4ae6-a930-3e014d413835>
/alice-bob.shacl <kgm:SHACLGraph--6b21e3d9-ee71-484d-b6ab-1f57080f2026>

```

## Examples

### Alice-Bob

data files location:

 - [ab.data.ttl] -- data RDF triples
 - [ab.shacl.ttl] -- SHACL structure

Alice-Bob queries:

```
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix kgm: <http://www.geisel-software.com/RDF/KGM#>
prefix ab: <http://www.geisel-software.com/RDF/alice-bob#>

select ?owner_name ?pet_name ?pet_class
where {
  ?g kgm:path "/alice-bob"
  graph ?g {
      ?pet rdf:type ?pet_class;
           ab:name ?pet_name;
           ab:ownedBy ?owner;
      .
      ?owner ab:name ?owner_name .
  }
}
```

### northwind


