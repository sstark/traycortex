import pytest
from traycortex.borgmatic import run_borgmatic
from traycortex.borgmatic import find_ssh_agent_socket
import socket


@pytest.mark.parametrize(
    "borgmatic_command, return_value",
    [
        ("/bin/true", 0),
        ("/bin/false", 1),
        ("exit 9", 9),
    ],
)
def test_run_borgmatic_return_value(
    populated_config_object, borgmatic_command, return_value
):
    populated_config_object.config.add_section("borgmatic")
    populated_config_object.config.set("borgmatic", "command", value=borgmatic_command)
    assert run_borgmatic(populated_config_object) == return_value


def test_run_borgmatic_nonexisting_cmd(populated_config_object):
    populated_config_object.config.add_section("borgmatic")
    populated_config_object.config.set("borgmatic", "command", value="/does/not/exist")
    assert run_borgmatic(populated_config_object) == 127


def test_find_ssh_agent_socket(monkeypatch, tmpdir):
    sockname = tmpdir / "ssh-XXXasdf" / "agent.007"
    sockname.parent.mkdir()
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(sockname))
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    assert find_ssh_agent_socket() == sockname


def test_find_ssh_agent_socket_notfound(monkeypatch, tmpdir):
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    assert find_ssh_agent_socket() == None
