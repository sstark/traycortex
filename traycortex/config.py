from platformdirs import user_config_path
from pathlib import Path
from configparser import ConfigParser
from traycortex import defaults

class Config:

    def __init__(self, f: Path):
        self.configFileName = f
        self.sourceConfigFile(f)

    def sourceConfigFile(self, f: Path):
        ini = ConfigParser()
        with open(f) as cf:
            ini.read_file(cf)
        self.config = ini

    def check_config(self):
        pass

    def create_initial_config(self):
        pass

    @classmethod
    def findConfig(cls) -> "Config":
        configfile = user_config_path(defaults.CONFIG_NAME)
        print(configfile)
        return cls(configfile)

