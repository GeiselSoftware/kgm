import os.path
import configparser

"""
expected config file layout:
------
[DEFAULT]
default-config-name: localhost-fuseki

[localhost-fuseki]
backend-url: http://localhost:3030/kgm-default-dataset/query

[<config-name>]
...
config
...

"""

class Config:
    def load_all_configs(self):
        config_fn = os.path.expanduser("~/.kgm.ini")
        if not os.path.exists(config_fn):
            return False

        config_fd = open(config_fn, "r")        
        self.configs = configparser.ConfigParser()
        self.configs.read(config_fn)
        return True
    
    def get_all_config_keys(self):
        return [x for x in self.configs.keys()]

    def get_config(self, config_name):
        if config_name == None:
            default_entries = self.configs["DEFAULT"]
            w_config_name = default_entries["default-config-name"]
        else:
            w_config_name = config_name
        
        w_config = self.configs[w_config_name]
        return w_config_name, {x:w_config[x] for x in w_config.keys() if x != 'default-config-name'}
    
def load_config(config_name):
    c = Config()
    if not c.load_all_configs():
        print("can't find config file ~/.kgm.ini, will create one with default content")
        with open(os.path.expanduser("~/.kgm.ini"), "w") as out_fd:
            print("[DEFAULT]", file = out_fd)
            print("default-config-name: localhost-fuseki", file = out_fd)
            print("", file = out_fd)
            print("[localhost-fuseki]", file = out_fd)
            print("backend-url: http://localhost:3030/kgm-default-dataset", file = out_fd)
        if not c.load_all_configs():
            #raise Exception("can't proceed after load_all_configs failed")
            return None

    return c.get_config(config_name)
