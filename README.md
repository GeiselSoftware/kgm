# VRGS - Versatile and Robust Graph Supervision

VRGS is set of UI and command line tools to help users to cope with complexities of graph database system design and usage. It focuses on RDF-based graph databases and SHACL-driven approach.


# python venv setup

To use python utils and other code you better setup venv called `vrgs` using commands below:

```
python3 -m venv ~/venv/vrgs
source ~/venv/vrgs/bin/activate
pip install -r ./requirements.txt
```

# mkdocs

```
mkdocs server -a 0.0.0.0:8001
```

# Ubuntu 22.04

```
sudo apt install emscripten # for wasm build
```

```
mkdir -p ~/local/cloned
cd ~/local/cloned
git clone https://github.com/fmtlib/fmt.git
git clone https://github.com/nlohmann/json.git
git clone https://github.com/ocornut/imgui.git
git clone https://github.com/thedmd/imgui-node-editor.git
```

Have env vars defined as below:

```
export FMT_ROOT_DIR=${HOME}/local/cloned/fmt
export NLOHMANN_ROOT_DIR=${HOME}/local/cloned/json
export IMGUI_ROOT_DIR=${HOME}/local/cloned/imgui
export IMGUI_NODE_EDITOR_ROOT_DIR=${HOME}/local/cloned/imgui-node-editor
```

# Builds

to build desktop version:

```
mkdir build
cd build
cmake ..
make
```

to build wasm version:
```
mkdir build.wasm
cd build.wasm
emcmake cmake ..
make
python3 -m http.server # use http://localhost:8000 then navigate to apps
```

# Docs

```
source ~/venv/gse/bin/activate
mkdocs serve -a 0.0.0.0:8001
```

# Misc

The description of emcc runtime debugging facilities is in [Debugging with Sanitizers](https://emscripten.org/docs/debugging/Sanitizers.html#debugging-with-sanitizers) section of emscripten docs. It includes description of how to enable [seg fault at zero address](https://emscripten.org/docs/debugging/Sanitizers.html#catching-null-dereference) - it is different from usuall abort/coredump behaviour of native build.
