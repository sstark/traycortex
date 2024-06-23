from traycortex import defaults
from multiprocessing.connection import Client
from multiprocessing.context import AuthenticationError
import argparse
import sys
from traycortex.config import Config
from traycortex.config import ConfigError
from traycortex.log import err, debug


def send_msg(msg: str, c: Config, port: int = defaults.DEFAULT_PORT):
    conn = Client((defaults.LISTEN_HOST, port), authkey=c.authkey)
    conn.send(msg)
    conn.close()


def close_checker(c: Config):
    send_msg(defaults.MSG_CLOSE, c)


def cli():
    parser = argparse.ArgumentParser(
        prog=defaults.CLIENT_NAME, description="Tray icon for borgmatic (client)"
    )
    parser.add_argument(
        "-c", "--config", help=f"{defaults.CLIENT_NAME} configuration file"
    )
    parser.add_argument(
        "-i",
        "--ini",
        action="store_true",
        help=f"generate minimal configuration file at default location",
    )
    parser.add_argument("message", nargs="?", choices=defaults.ALLOWED_CLIENT_MESSAGES)
    args = parser.parse_args()

    if args.ini:
        try:
            Config.create_initial_config()
            sys.exit(0)
        except ConfigError as e:
            err(f"Error creating initial config: {e}")
            sys.exit(1)

    try:
        if args.config:
            c = Config(args.config)
        else:
            c = Config.findConfig()
    except ConfigError:
        sys.exit(1)
    debug(c)

    if args.message not in defaults.ALLOWED_CLIENT_MESSAGES:
        err("no message or invalid message given")
        sys.exit(2)
    try:
        send_msg(args.message, c)
    except ConnectionRefusedError as e:
        err(f"Connection error: {e}. Did you start {defaults.APP_NAME}?")
        sys.exit(3)
    except AuthenticationError as e:
        err(f"Authentication error: {e}")
        sys.exit(3)
    except ConnectionError as e:
        err(f"Connection error: {e}.")
        sys.exit(3)
    sys.exit(0)
