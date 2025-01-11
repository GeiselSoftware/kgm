# KGM - Knowledge Graph Management

KGM is set of command line tools to help users to cope with complexities of graph database system design and usage.
It focuses on RDF-based knowledge graph DBs databases and management of its data using SHACL as core instrument.

# kgm python package

editable install

```
python3 -m venv ~/venv/kgm
source ~/venv/kgm/bin/activate
cd py-packages/kgm
pip install -e .
```

wheel distribution build. before this steps build.wasm must be build as described below (build wasm version):
```
python3 -m venv ~/venv/kgm-distrib
source ~/venv/kgm-distrib/bin/activate
pip install build

cd py-packages/kgm
python -m build --wheel
cd dist

```

*.whl is binary distribution, *.tar.gz is source distribution.

It is possible to use gh to place distribution file into GitHub repo releases.

```
cd <repo>
gu auth login
cd py-packages/kgm/dist
gh release create <tag> --generate-notes <file-to-release>
```
