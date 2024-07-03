## kgm command-line

### Installation

```
python3 -m venv ~/venv/kgm
source ~/venv/kgm/bin/activate
```

### Usage

**kgm** is command-line utility to facilitate the tasks which could be described as 'graph store exploration'.

Given .ttl file it is possible to upload the content into GDB using `kgm insert` command. This operation allow to specify **kgm path** to resulting graph in GDB.

```
> ./kgm insert --kgm-path /alice-bob/simple --ttl-file ../examples/alice-bob/simple/data.ttl
... tbc
> ./kgm ls
         kgm_path                                         graph_uri
/alice-bob/simple <kgm:Graph##03027263-2242-454b-8d4d-7aaecb9990ae>
```

