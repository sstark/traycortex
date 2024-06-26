
from subprocess import run, CalledProcessError
from traycortex.config import Config
from traycortex.log import err, debug
from traycortex.defaults import BORGMATIC_COMMAND

def run_borgmatic(c: Config) -> int:
    """Run borgmatic"""
    cmd = c.config.get("borgmatic", "command", fallback=BORGMATIC_COMMAND)
    try:
        result = run(cmd, shell=True, text=True, capture_output=True)
        result.check_returncode()
        if result.stderr:
            err(f"{result.returncode}\n{result.stderr}")
        if result.stdout:
            debug("running borgmatic worked. stdout:")
            debug(result.stdout)
            print(result.stdout)
    except (CalledProcessError, OSError) as e:
        err(f"borgmatic could not be run: {e}")
        return -1
    return result.returncode
