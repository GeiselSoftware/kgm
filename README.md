# KGM - Knowledge Graph Management

KGM is set of UI and command line tools to help users to cope with complexities of graph database system design and usage.
It focuses on RDF-based knowledge graph DBs databases and management of its data using SHACL as core instrument.

# kgm python package

```
python3 -m venv ~/venv/kgm
source ~/venv/kgm
cd py-packages/kgm
pip install .
```

# mkdocs

```
python3 -m venv ~/venv/kgm-docs
source ~/venv/kgm-docs
cd docs
pip install -r ./requirements.txt
mkdocs server -a 0.0.0.0:8001
```

# build - ubuntu 22.04

Pull all the submodules to use as dependencies

```
git submodule update --init --recursive
```

Or link to your own local dependency clones with these environment variables

```
export FMT_ROOT_DIR=${HOME}/local/cloned/fmt
export NLOHMANN_ROOT_DIR=${HOME}/local/cloned/json
export IMGUI_ROOT_DIR=${HOME}/local/cloned/imgui
export IMGUI_NODE_EDITOR_ROOT_DIR=${HOME}/local/cloned/imgui-node-editor
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
