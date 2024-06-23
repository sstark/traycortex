from io import StringIO
from platformdirs import user_config_path
from pathlib import Path
from configparser import ConfigParser
from traycortex import defaults
from traycortex.log import debug, err
import secrets

class ConfigError(Exception):
    pass


class Config:
    """Class holding the whole configuration

    It can read, write and generate a configuration.

    Config.config will hold the actual ConfigParser object.
    """

    def __init__(self, f: Path):
        self.configFileName = f
        self.sourceConfigFile(f)

    def sourceConfigFile(self, f: Path):
        """Parse a configuration file and populate the Config object"""
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
        """Key for socket authentication"""
        return self.config["connection"]["authkey"].encode("UTF-8")

    @staticmethod
    def create_authkey() -> str:
        """Create a random key used for socket authentication"""
        return secrets.token_hex(16)

    @staticmethod
    def create_initial_config():
        """Create a minimal configuration file"""
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
        """Search a valid config file and return a Config object"""
        configfile = user_config_path(defaults.CONFIG_NAME)
        debug(configfile)
        return cls(configfile)

    def __str__(self) -> str:
        """Print a string representing a valid configuration"""
        s = StringIO()
        s.write(f"# {defaults.APP_NAME} configuration\n")
        self.config.write(s)
        return s.getvalue()
