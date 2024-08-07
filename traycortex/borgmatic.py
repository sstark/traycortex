from collections.abc import Iterable
from itertools import chain
from subprocess import run, CalledProcessError
from traycortex import defaults
from traycortex.config import Config
from traycortex.log import err, debug
from pathlib import Path
from typing import Optional
import os


def find_ssh_agent_socket() -> Optional[Path]:
    """Search for an ssh-agent socket in the expected directory

    Return the path if found, otherwise return None
    """
    # According to ssh-agent(1) this is where the socket should be located
    tmpdir = Path(os.environ.get("TMPDIR", "/tmp"))
    debug(f"tmpdir: {tmpdir}")
    # A bit more guesswork and sanity check that we have a socket. Return
    # the first agent found, because we have no clue which one is correct
    # anyway.
    return next((x for x in tmpdir.glob("ssh-*/agent.*") if x.is_socket()), None)


def borgmatic_environment() -> dict:
    """Create the environment for borgmatic

    Start with a 1:1 copy of the traycortex environment, then modify
    or augment as needed.
    """
    env = os.environ.copy()
    if sock := find_ssh_agent_socket():
        # TODO: This behaviour needs to be optional
        debug(f"Found ssh-agent at {sock}")
        env["SSH_AUTH_SOCK"] = str(sock)
    return env


def run_borgmatic(c: Config, configname: str = "") -> int:
    """Run borgmatic"""
    debug(f"configname: {configname}")
    cmd = c.get_command(configname)
    debug(f"cmd: {cmd}")
    try:
        result = run(
            cmd, shell=True, text=True, capture_output=True, env=borgmatic_environment()
        )
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
        if result.stdout:
            debug("running borgmatic worked. stdout:")
            debug(result.stdout)
            print(result.stdout)
    except OSError as e:
        err(f"borgmatic could not be run: {e}")
        return -1
    except CalledProcessError as e:
        err(f"borgmatic error: {e}")
        return e.returncode
    return result.returncode


def find_all_borgmatic_yaml() -> Iterable[Path]:
    for path in defaults.BORGMATIC_YAML_PATHS:
        if path.is_dir():
            yield from chain(path.glob("*.yml"), path.glob("*.yaml"))
        else:
            yield path
