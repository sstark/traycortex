from dataclasses import dataclass
from traycortex.defaults import (
    ALLOWED_CLIENT_MESSAGES,
    APP_NAME,
    MSG_CLOSE,
    CLIENT_NAME,
    LISTEN_HOST,
)
from multiprocessing.connection import Client
from multiprocessing.context import AuthenticationError
import argparse
from traycortex.config import Config
from traycortex.config import ConfigError
from traycortex.log import err, debug
import traycortex.log


@dataclass
class TCMessage:
    msg: str
    arg: str

    def __post_init__(self):
        if self.msg not in ALLOWED_CLIENT_MESSAGES + [MSG_CLOSE]:
            raise ValueError(f"Invalid message: {self.msg}")


def send_msg(msg: TCMessage, c: Config):
    """Send a message to the tray component"""
    conn = Client((LISTEN_HOST, c.port), authkey=c.authkey)
    conn.send(msg)
    conn.close()


def close_checker(c: Config):
    """Send a close message to the tray component
    This is just a shortcut for properly ending the app
    """
    msg = TCMessage(MSG_CLOSE, "")
    send_msg(msg, c)


def createArgumentParser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=CLIENT_NAME, description="Tray icon for borgmatic (client)"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument("-c", "--config", help=f"{CLIENT_NAME} configuration file")
    parser.add_argument(
        "-i",
        "--ini",
        action="store_true",
        help="generate minimal configuration file at default location",
    )
    parser.add_argument("message", nargs="?", choices=ALLOWED_CLIENT_MESSAGES)
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

    if args.message not in ALLOWED_CLIENT_MESSAGES:
        err("no message or invalid message given")
        return 2
    try:
        send_msg(TCMessage(args.message, ""), c)
    except ConnectionRefusedError as e:
        err(f"Connection error: {e}. Did you start {APP_NAME}?")
        return 3
    except AuthenticationError as e:
        err(f"Authentication error: {e}")
        return 3
    except ConnectionError as e:
        err(f"Connection error: {e}.")
        return 3
    return 0
