import platform, site, os
import sys

def main():
    fuseki_url = "http://localhost:3030/kgm-default-dataset/query"
    kgm_path = sys.argv[1]

    # linux:
    
    # mac: /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64
    # mac: ./kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl
    # import site; site.getsitepackages()
    #
    # /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64/kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl
    p = platform.system()
    if p == "Darwin":
        electron_app = os.path.join(site.getsitepackages()[0], "kgm/electron-dist/darwin-arm64/kgm-editor.app/Contents/MacOS/Electron")
        kgm_editor_cmd = f"{electron_app} -- {fuseki_url} {kgm_path}"
    elif p == "Windows":
        electron_app = os.path.join(site.getsitepackages()[0], "kgm/electron-dist/win32-x64/kgm-editor.exe")
        kgm_editor_cmd = f"{electron_app} -- {fuseki_url} {kgm_path}"
    elif p == "Linux":
        electron_app = os.path.join(site.getsitepackages()[0], "kgm/electron-dist/linux-x64/kgm-editor")
        kgm_editor_cmd = f"{electron_app} -- {fuseki_url} {kgm_path}"
    else:
        raise Exception(f"not supported platform {p}")

    print(kgm_editor_cmd)
    os.system(kgm_editor_cmd)
