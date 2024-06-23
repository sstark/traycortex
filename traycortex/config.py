from platformdirs import user_config_path
from pathlib import Path
from configparser import ConfigParser
from traycortex import defaults
from traycortex.log import debug, err

class ConfigError(Exception):
    pass

class Config:

    def __init__(self, f: Path):
        self.configFileName = f
        self.sourceConfigFile(f)

    def sourceConfigFile(self, f: Path):
        ini = ConfigParser()
        try:
            with open(f) as cf:
                ini.read_file(cf)
        except OSError as e:
            err(f"Could not open configuration file {f}: {e}")
            raise ConfigError
        self.config = ini

    def check_config(self):
        pass

    def create_initial_config(self):
        pass

    @classmethod
    def findConfig(cls) -> "Config":
        configfile = user_config_path(defaults.CONFIG_NAME)
        debug(configfile)
        return cls(configfile)
