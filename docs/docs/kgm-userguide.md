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
> kgm insert --kgm-path /alice-bob/simple --ttl-file ../examples/alice-bob/simple/data.ttl
... tbc
> kgm ls
         kgm_path                                         graph_uri
/alice-bob/simple <kgm:Graph##03027263-2242-454b-8d4d-7aaecb9990ae>
```

## Examples

### Alice-Bob

data files location:

 - [KGM/examples/alice-bob/ab.ttl](https://github.com/GeiselSoftware/KGM/blob/main/examples/alice-bob/ab.ttl) -- data RDF triples
 - [KGM/examples/alice-bob/ab.shacl.ttl](https://github.com/GeiselSoftware/KGM/blob/main/examples/alice-bob/ab.shacl.ttl) -- SHACL structure

Alice-Bob queries:

```
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
prefix kgm: <kgm:>
prefix ab: <ab:>

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


