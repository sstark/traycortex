from traycortex.config import Config


def test_findConfig(monkeypatch, populated_config_file):

    def mock_user_config_path(_):
        return populated_config_file

    # https://stackoverflow.com/questions/31306080/pytest-monkeypatch-isnt-working-on-imported-function
    monkeypatch.setattr("traycortex.config.user_config_path", mock_user_config_path)
    c = Config.findConfig()
    assert c.config["connection"]["authkey"] == "1111111f8911bc39deec0641faf71111"


# def test_create_initial_config(fake_home):
