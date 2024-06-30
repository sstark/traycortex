from pathlib import Path
from platformdirs import user_config_path

DEFAULT_PORT = 35234
LISTEN_HOST = "localhost"
MSG_JOB_STARTED = "job_started"
MSG_JOB_FINISHED = "job_finished"
MSG_JOB_ERROR = "job_error"
MSG_CLOSE = "close"
CLIENT_NAME = "traycortex-cli"
APP_NAME = "traycortex"
CONFIG_NAME = APP_NAME + ".ini"
ALLOWED_CLIENT_MESSAGES = [MSG_JOB_STARTED, MSG_JOB_FINISHED, MSG_JOB_ERROR]
# args allowed
BORGMATIC_COMMAND = "borgmatic"
MENU_ENGAGE = "Engage"
MENU_ENGAGE_RUNNING = "Engage: Running..."
MENU_DISCARD = "Discard"
# According to borgmatic source: borgmatic/config/collect.py
BORGMATIC_YAML_PATHS = [
    Path("/etc/borgmatic/config.yaml"),
    Path("/etc/borgmatic.d"),
    user_config_path() / "borgmatic/config.yaml",
    user_config_path() / "borgmatic.d",
]
