from traycortex import defaults
from multiprocessing.connection import Client
from multiprocessing.context import AuthenticationError
import argparse
from traycortex.config import Config
from traycortex.config import ConfigError
from traycortex.log import err, debug
import traycortex.log


def send_msg(msg: str, c: Config, port: int = defaults.DEFAULT_PORT):
    """Send a message to the tray component"""
    conn = Client((defaults.LISTEN_HOST, port), authkey=c.authkey)
    conn.send(msg)
    conn.close()


def close_checker(c: Config):
    """Send a close message to the tray component
       This is just a shortcut for properly ending the app
    """
    send_msg(defaults.MSG_CLOSE, c)


def createArgumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=defaults.CLIENT_NAME, description="Tray icon for borgmatic (client)"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
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
    return parser


def cli() -> int:
    args = createArgumentParser().parse_args()
    traycortex.log.DEBUG = args.debug

    if args.ini:
        try:
            Config.create_initial_config()
            return 0
        except ConfigError as e:
            err(f"Error creating initial config: {e}")
            return 1

    try:
        if args.config:
            c = Config(args.config)
        else:
            c = Config.findConfig()
    except ConfigError:
        return 1
    debug(c)

    if args.message not in defaults.ALLOWED_CLIENT_MESSAGES:
        err("no message or invalid message given")
        return 2
    try:
        send_msg(args.message, c)
    except ConnectionRefusedError as e:
        err(f"Connection error: {e}. Did you start {defaults.APP_NAME}?")
        return 3
    except AuthenticationError as e:
        err(f"Authentication error: {e}")
        return 3
    except ConnectionError as e:
        err(f"Connection error: {e}.")
        return 3
    return 0
