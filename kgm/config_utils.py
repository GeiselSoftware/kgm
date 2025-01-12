import os.path
import configparser

class Config:    
    @staticmethod
    def default_config_file_content__():
        return """\
[DEFAULT]
backend-url: http://localhost:3030/kgm-default-dataset
"""

    def load_config(self, create_ini = True):
        config_fn = os.path.expanduser("~/.kgm.ini")
        if not os.path.exists(config_fn):
            if create_ini == True:
                print(f"creating default ini file: {config_fn}")
                with open(config_fn, "w") as ofd:
                    ofd.write(self.default_config_file_content__())                    
            else:
                raise Exception(f"failed to load kgm config from ~/.kgm.ini")

        config_fd = open(config_fn, "r")        
        self.configs = configparser.ConfigParser()
        self.configs.read(config_fn)
    
    def get_config_keys(self):
        return [x for x in self.configs.keys()]

    def get_config(self, config_name = "DEFAULT"):
        w_config = self.configs[config_name]
        return {x:w_config[x] for x in w_config.keys()}

config = Config()
config.load_config()

def get_config(config_name = "DEFAULT"):
    return config.get_config(config_name)
