from traycortex.config import Config
from traycortex.config import ConfigError
import pytest
from traycortex.defaults import CONFIG_NAME


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
