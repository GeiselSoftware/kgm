import os
import sys
import subprocess
import venv
import argparse
import urllib.request, json

def get_latest_kgm_wheel_url():
    # curl -s https://api.github.com/repos/GeiselSoftware/kgm/releases/latest
    release_files = []
    with urllib.request.urlopen("https://api.github.com/repos/GeiselSoftware/kgm/releases/latest") as r:
        res_json = json.loads(r.read())
        for a in res_json['assets']:
            release_files.append(a['browser_download_url'])

    ret = None
    for r in release_files:
        if r.find(".whl") != -1:
            ret = r
            break
    return ret

def create_and_install_venv(wheel_url, venv_dir):
    venv.create(venv_dir, with_pip=True)

    # Activate virtual environment
    if os.name == "nt":  # Windows
        activate_script = os.path.join(venv_dir, "Scripts", "activate")
    else:  # Unix-based
        activate_script = os.path.join(venv_dir, "bin", "activate")

    # Download the wheel file
    wheel_file = os.path.join(venv_dir, wheel_url.split('/')[-1])
    urllib.request.urlretrieve(wheel_url, wheel_file)
    #wheel_file = wheel_url

    # Run pip install in virtual environment
    pip = os.path.join(venv_dir, 'bin', 'pip') if os.name != "nt" else '"' + os.path.join(venv_dir, 'Scripts', 'pip') + '"'
    wheel_file = wheel_file if os.name != "nt" else f'"{wheel_file}"'
    pip_install_cmd = f"{pip} install --force-reinstall --no-cache-dir {wheel_file}"
    subprocess.run(pip_install_cmd, shell=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a virtual environment and install a package from a wheel URL.")
    parser.add_argument("--wheel_url", help="The URL of the .whl package file", required = False)
    args = parser.parse_args()
    print(args)

    wheel_url = args.wheel_url
    if wheel_url is None:
        wheel_url = get_latest_kgm_wheel_url()
    print("wheel_url:", wheel_url)

    # Create virtual environment
    if os.name == "nt": # Windows
        # %USERPROFILE%\Scripts
        #raise Exception("not supported")
        venv_dir = os.path.join(os.environ["USERPROFILE"], "Scripts\\kgm")
    else: # linux and mac
        venv_dir = "/usr/local/kgm"

    print("kgm will be installed to dir", venv_dir)
    print("proceed? [Y/n]:")
    res = input()
    if len(res) == 0:
        res = 'y'

    if res == 'y':
        print("start kgm install")
        create_and_install_venv(wheel_url, venv_dir)
        print(f"kgm installed into {venv_dir}, to run use {venv_dir}/bin/kgm")
    else:
        print("aborted")
