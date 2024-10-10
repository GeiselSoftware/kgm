"""
cd build.wasm/electron-dist
aws s3 cp kgm-editor--linux-x64.zip s3://yaooas69-scratch
aws s3 cp kgm-editor--win32-x64.zip s3://yaooas69-scratch
aws s3 cp kgm-editor--darwin-arm64.zip s3://yaooas69-scratch
"""

import os

def make_distrib(dist):
    electron_distrib_url = f"https://github.com/electron/electron/releases/download/v31.7.0/electron-v31.7.0-{dist}.zip"
    dist_dir = os.path.realpath("build.wasm/electron-dist/" + dist)
    
    if 1:
        if os.path.exists(dist_dir):
            raise Exception(f"distrib dir {dist_dir} exists, giving up")
        os.makedirs(dist_dir)

    cmd = f"cd {dist_dir} && wget {electron_distrib_url}"
    if 1:
        print(cmd)
        os.system(cmd)

    if 1:
        zip_fn = os.path.basename(electron_distrib_url)
        cmd = f"cd {dist_dir} && unzip {zip_fn} && rm {zip_fn}"
        print(cmd)
        os.system(cmd)

    cmds = []
    if dist == "linux-x64":
        cmds.append(f"cd {dist_dir} && mv electron kgm-editor")
        cmds.append(f"cd {dist_dir} && mkdir -p resources/app")
        electron_app_dir = f"{dist_dir}/resources/app"
    elif dist == "win32-x64":
        cmds.append(f"cd {dist_dir} && mv electron.exe kgm-editor.exe")
        cmds.append(f"cd {dist_dir} && mkdir -p resources/app")        
        electron_app_dir = f"{dist_dir}/resources/app"
    elif dist == "darwin-arm64":
        cmds.append(f"cd {dist_dir} && mv Electron.app kgm-editor.app")
        cmds.append(f"cd {dist_dir} && mkdir -p kgm-editor.app/Contents/Resources/app")
        electron_app_dir = f"{dist_dir}/kgm-editor.app/Contents/Resources/app"
    else:
        raise Exception(f"unknown dist {dist}")

    cmds.append(f"cd apps/shacled-electron && cp main.js package.json {electron_app_dir}")
    cmds.append(f"cp build.wasm/apps/shacled/run-shacled.* {electron_app_dir}")
    for cmd in cmds:
        print(cmd)
        os.system(cmd)
    

if __name__ == "__main__":
    for dist in ["linux-x64", "win32-x64", "darwin-arm64"]:
        make_distrib(dist)
        os.system(f"cd build.wasm/electron-dist && mv {dist} kgm-editor--{dist}")
        os.system(f"cd build.wasm/electron-dist && zip -r kgm-editor--{dist}.zip kgm-editor--{dist}")
        os.system(f"cd build.wasm/electron-dist && rm -rf kgm-editor--{dist}")

    print("all done.")
    
