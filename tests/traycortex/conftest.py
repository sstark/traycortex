import pytest
import tempfile
from shutil import rmtree
from pathlib import Path
from traycortex.defaults import CONFIG_NAME
from textwrap import dedent


@pytest.fixture
def fake_home():
    p = Path(tempfile.TemporaryDirectory(suffix="-HOME").name)
    p.mkdir()
    yield p
    rmtree(p)


@pytest.fixture
def populated_config_file(fake_home):
    confdir = fake_home / "dot.config"
    confdir.mkdir()
    config_file = confdir / CONFIG_NAME
    min_config = '''
        [connection]
        authkey = 1111111f8911bc39deec0641faf71111
    '''
    with open(config_file, "w") as f:
        f.write(dedent(min_config))
    yield config_file
    rmtree(confdir)
