#import ipdb
import click
import platform, os
import sys
import kgm
import importlib.metadata

class CustomHelp(click.Command):
    def format_help(self, ctx, formatter):
        # Add your custom message
        formatter.write(f"kgm version: {importlib.metadata.version('kgm')}\n")
        super().format_help(ctx, formatter)
        
@click.command(cls = CustomHelp)
@click.option('--dry-run', is_flag = True, help = "to show how electron app will be started")
@click.argument('kgm-path', required = True)
def run_app(dry_run, kgm_path):
    fuseki_url = "http://localhost:3030/kgm-default-dataset/query"
    #if version:
    #ipdb.set_trace()
    print("version:", importlib.metadata.version("kgm"))

    # linux:
    
    # mac: /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64
    # mac: ./kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl
    # import site; site.getsitepackages()
    #
    # /usr/local/kgm/lib/python3.13/site-packages/kgm/electron-dist/darwin-arm64/kgm-editor.app/Contents/MacOS/Electron -- http://localhost:3030/kgm-default-dataset/query /gimp-test.shacl

    p = platform.system()
    kgm_package_dir = kgm.__path__[0]
    if p == "Darwin":
        electron_app = os.path.join(kgm_package_dir, "electron-dist/darwin-arm64/kgm-editor.app/Contents/MacOS/Electron")
        kgm_editor_cmd = f"{electron_app} -- {fuseki_url} {kgm_path}"
    elif p == "Windows":
        electron_app = os.path.join(kgm_package_dir, "electron-dist/win32-x64/kgm-editor.exe")
        kgm_editor_cmd = f'"{electron_app}" -- {fuseki_url} {kgm_path}'
    elif p == "Linux":
        electron_app = os.path.join(kgm_package_dir, "electron-dist/linux-x64/kgm-editor")
        kgm_editor_cmd = f"{electron_app} -- {fuseki_url} {kgm_path}"
    else:
        raise Exception(f"not supported platform {p}")

    if dry_run:
        print(kgm_editor_cmd)
    else:
        print(kgm_editor_cmd)        
        os.system(kgm_editor_cmd)

def main():
    run_app()
