from platformdirs import user_config_path
from pathlib import Path
from configparser import ConfigParser
from traycortex import defaults
from traycortex.log import debug, err
import secrets

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

    @property
    def authkey(self) -> bytes:
        return self.config["connection"]["authkey"].encode("UTF-8")

    @staticmethod
    def create_authkey() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def create_initial_config():
        configfile = user_config_path(defaults.CONFIG_NAME)
        if configfile.exists():
            raise ConfigError(f"{configfile} already exists")
        ini = ConfigParser()
        ini.add_section("connection")
        ini.set("connection", "authkey", Config.create_authkey())
        try:
            with open(configfile, "w+") as cf:
                ini.write(cf)
        except OSError as e:
            raise ConfigError(f"{configfile} could not be written: {e}")

    @classmethod
    def findConfig(cls) -> "Config":
        configfile = user_config_path(defaults.CONFIG_NAME)
        debug(configfile)
        return cls(configfile)
