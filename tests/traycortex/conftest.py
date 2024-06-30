import pytest
import tempfile
from shutil import rmtree
from pathlib import Path
from traycortex.config import Config
from traycortex.defaults import CONFIG_NAME
from textwrap import dedent
from PIL import Image


@pytest.fixture
def fake_home():
    p = Path(tempfile.TemporaryDirectory(suffix="-HOME").name)
    p.mkdir()
    yield p
    rmtree(p)


@pytest.fixture
def config_dir(fake_home):
    confdir = fake_home / "dot.config"
    yield confdir
    rmtree(confdir)


@pytest.fixture
def populated_config_file(config_dir):
    config_dir.mkdir()
    config_file = config_dir / CONFIG_NAME
    min_config = '''
        [connection]
        authkey = 1111111f8911bc39deec0641faf71111
    '''
    with open(config_file, "w") as f:
        f.write(dedent(min_config))
    yield config_file
    config_file.unlink()


@pytest.fixture
def populated_config_object(monkeypatch, populated_config_file):

    def mock_user_config_path(_):
        return populated_config_file

    monkeypatch.setattr("traycortex.config.user_config_path", mock_user_config_path)
    return Config.findConfig()


class MockIcon():
    '''Mock very basic behaviour of a pystray icon'''

    def __init__(self):
        self.icon = Image.new('RGB', (150, 150), "green")
        self.notifications = []

    def notify(self, msg: str):
        self.notifications.append(msg)

    def update_menu(self):
        pass


@pytest.fixture
def mock_icon():
    return MockIcon()
