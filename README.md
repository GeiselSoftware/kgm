# KGM - Knowledge Graph Management

KGM is set of UI and command line tools to help users to cope with complexities of graph database system design and usage.
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
cd py-packages/kgm
pip install build
python -m build
cd dist
```

*.whl is binary distribution, *.tar.gz is source distribution.


# mkdocs

```
python3 -m venv ~/venv/kgm-docs
source ~/venv/kgm-docs
cd docs
pip install -r ./requirements.txt
mkdocs serve -a 0.0.0.0:8001
```

# build - ubuntu 22.04

Pull all the submodules to use as dependencies

```
git submodule update --init --recursive
```

to build desktop version:

```
mkdir build
cd build
cmake ..
make
```

to build wasm version:
```
sudo apt install emscripten
mkdir build.wasm
cd build.wasm
emcmake cmake ..
make
python3 -m http.server # use http://localhost:8000 then navigate to apps
```

# Misc

The description of emcc runtime debugging facilities is in [Debugging with Sanitizers](https://emscripten.org/docs/debugging/Sanitizers.html#debugging-with-sanitizers) section of emscripten docs. It includes description of how to enable [seg fault at zero address](https://emscripten.org/docs/debugging/Sanitizers.html#catching-null-dereference) - it is different from usuall abort/coredump behaviour of native build.
