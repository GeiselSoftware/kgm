import os.path
import configparser

def do_config_show():
    config_fn = os.path.expanduser("~/.kgm.ini")
    if not os.path.exists(config_fn):
        raise Exception("can't find kgm ini file")

    print("config file:", config_fn)
    config_fd = open(config_fn, "r")
        
    config = configparser.ConfigParser()
    config.read(config_fn)
    backend_config_name = config["DEFAULT"]["backend"]
    print("backend_config_name:", backend_config_name)
    backend_config = config[backend_config_name]

    #print([x for x in backend_config])
    #print(backend_config["endpoint"])
    print([backend_config[x] for x in backend_config.keys()])
    
