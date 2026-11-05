import pytest
from traycortex.borgmatic import run_borgmatic
from traycortex.borgmatic import find_ssh_agent_socket
from traycortex.borgmatic import interpret_error, get_last_error
import socket


@pytest.mark.parametrize(
    "borgmatic_command, return_value",
    [
        ("true", 0),
        ("false", 1),
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


def test_run_borgmatic_clears_last_error_on_success(populated_config_object):
    populated_config_object.config.add_section("borgmatic")
    populated_config_object.config.set(
        "borgmatic", "command", value="echo 'Permission denied (publickey).' >&2; false"
    )
    run_borgmatic(populated_config_object)
    assert get_last_error() is not None
    populated_config_object.config.set("borgmatic", "command", value="true")
    run_borgmatic(populated_config_object)
    assert get_last_error() is None


@pytest.mark.parametrize(
    "message, expected_fragment",
    [
        ("Permission denied (publickey).", "ssh-agent"),
        ("Could not resolve hostname example.com", "hostname could not be resolved"),
        ("Connection refused", "refused or timed"),
        ("Connection closed by remote host", "ssh-agent"),
    ],
)
def test_interpret_error_known_patterns(message, expected_fragment):
    result = interpret_error(message)
    assert expected_fragment in result
    assert message in result


def test_interpret_error_unknown_passthrough():
    assert interpret_error("  some unrelated failure  ") == "some unrelated failure"


def test_find_ssh_agent_socket(monkeypatch, tmpdir):
    sockname = tmpdir / "ssh-XXXasdf" / "agent.007"
    make_socket_server(sockname)
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr("os.path.expanduser", lambda x: "/dev/null")
    assert find_ssh_agent_socket() == sockname


def test_find_ssh_agent_socket2(monkeypatch, tmpdir):
    monkeypatch.setattr("os.path.expanduser", lambda x: tmpdir / "home" / "user")
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    sock1 = tmpdir / "home" / "user" / ".ssh" / "agent" / "sock"
    make_socket_server(sock1)
    sock2 = tmpdir / "ssh-XXXasdf" / "agent.007"
    make_socket_server(sock2)
    assert find_ssh_agent_socket() == sock1
    assert find_ssh_agent_socket() != sock2


def make_socket_server(p):
    p.parent.mkdir(parents=True)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(str(p))
    return server


def test_find_ssh_agent_socket_notfound(monkeypatch, tmpdir):
    monkeypatch.setenv("TMPDIR", str(tmpdir))
    monkeypatch.setattr("os.path.expanduser", lambda x: "/dev/null")
    assert find_ssh_agent_socket() is None
