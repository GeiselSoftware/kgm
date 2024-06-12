# shacled
We do need better name for this project
SHACL editor

# Ubuntu 22.04

```
git clone --depth 1 https://github.com/nlohmann/json.git
sudo apt install emscripten # for wasm build
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
mkdir build.wasm
cd build.wasm
emcmake cmake ..
make
python3 -m http.server # use http://localhost:8000 then navigate to apps
```
