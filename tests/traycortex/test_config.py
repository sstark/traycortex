from traycortex.config import Config
from traycortex.config import ConfigError
import pytest
from traycortex.defaults import BORGMATIC_COMMAND, CONFIG_NAME, EXPANDO_CONFIG


def test_findConfig(monkeypatch, populated_config_file):

    def mock_user_config_path(_):
        return populated_config_file

    # https://stackoverflow.com/questions/31306080/pytest-monkeypatch-isnt-working-on-imported-function
    monkeypatch.setattr("traycortex.config.user_config_path", mock_user_config_path)
    c = Config.findConfig()
    assert c.config["connection"]["authkey"] == "1111111f8911bc39deec0641faf71111"


def test_create_initial_config(monkeypatch, config_dir):

    def mock_user_config_path(_):
        return config_dir / CONFIG_NAME

    monkeypatch.setattr("traycortex.config.user_config_path", mock_user_config_path)
    Config.create_initial_config()
    assert (config_dir / CONFIG_NAME).exists()


def test_create_initial_config_exists(monkeypatch, populated_config_file):

    def mock_user_config_path(_):
        return populated_config_file

    monkeypatch.setattr("traycortex.config.user_config_path", mock_user_config_path)
    _ = Config.findConfig()
    with pytest.raises(ConfigError) as e:
        Config.create_initial_config()

    assert str(e.value) == f"{populated_config_file} already exists"


def test_get_command_normal(populated_config_file):
    c = Config(populated_config_file)
    assert c.get_command() == BORGMATIC_COMMAND


def test_get_command_individual_expando(populated_config_file):
    c = Config(populated_config_file)
    c.config.add_section("borgmatic")
    c.config["borgmatic"]["command"] = f"borgmatic {EXPANDO_CONFIG}"
    assert c.get_command(configname="/tmp/foo.yml") == "borgmatic -c /tmp/foo.yml"


def test_get_command_individual_noexpando(populated_config_file):
    """Here we want to see that it is still ok to call an individual file
    with no expando configured. In this case the request to run an individual
    file is ignored and just bormatic is run
    """
    c = Config(populated_config_file)
    c.config.add_section("borgmatic")
    c.config["borgmatic"]["command"] = "borgmatic"
    assert c.get_command(configname="/tmp/foo.yml") == "borgmatic"
