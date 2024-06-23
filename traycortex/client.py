from traycortex import defaults
from multiprocessing.connection import Client
import argparse


def send_msg(msg: str, port: int = defaults.DEFAULT_PORT):
    conn = Client((defaults.LISTEN_HOST, port))
    conn.send(msg)
    conn.close()


def close_checker():
    send_msg(defaults.MSG_CLOSE)


def cli():
    parser = argparse.ArgumentParser(
        prog=defaults.CLIENT_NAME, description="Tray icon for borgmatic"
    )
    parser.add_argument(
        "-c", "--config", help=f"{defaults.CLIENT_NAME} configuration file"
    )
    parser.add_argument("message", choices=defaults.ALLOWED_CLIENT_MESSAGES)
    args = parser.parse_args()
    send_msg(args.message)
