
from traycortex import defaults
from multiprocessing.connection import Client


def send_msg(msg: str, port: int = defaults.DEFAULT_PORT):
    conn = Client((defaults.LISTEN_HOST, port))
    conn.send(msg)
    conn.close()


def close_checker():
    send_msg(defaults.MSG_CLOSE)


