# shacled
We do need better name for this project
SHACL editor

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
export IMGUI_ROOT_DIR=$HOME/local/cloned/imgui
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

# Misc

The description of emcc runtime debugging facilities is in [Debugging with Sanitizers](https://emscripten.org/docs/debugging/Sanitizers.html#debugging-with-sanitizers) section of emscripten docs. It includes description of how to enable [seg fault at zero address](https://emscripten.org/docs/debugging/Sanitizers.html#catching-null-dereference) - it is different from usuall abort/coredump behaviour of native build.
