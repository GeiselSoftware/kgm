# shacled
SHACL editor

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
