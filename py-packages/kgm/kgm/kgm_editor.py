import platform, site, os
import sys

def main():
    # linux:
    
    # mac: /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64
    # mac: ./kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl
    # import site; site.getsitepackages()
    #
    # /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64/kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl
    p = platform.system()
    if p == "Darwin":
        fuseki_query_url = "http://localhost:3030/kgm-default-dataset/query"
        kgm_path = sys.argv[1]
        electron_app_dir = os.path.join(site.getsitepackages()[0], "kgm/electron-dist/darwin-arm64")
        kgm_editor_cmd = f"{electron_app_dir}/kgm-editor.app/Contents/MacOS/Electron -- {fuseki_query_url} {kgm_path}"
        print(kgm_editor_cmd)
        os.system(kgm_editor_cmd)
    else:
        raise Exception(f"not supported platform {p}")

