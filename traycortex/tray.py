from collections.abc import Callable
import pystray
from PIL import Image
import threading
import time
import queue
from importlib import resources
import traycortex.images
from multiprocessing.connection import Listener
from multiprocessing.context import AuthenticationError
from traycortex.client import close_checker
from traycortex import defaults
import traycortex.log
from traycortex.log import debug, notice, err
from traycortex.config import ConfigError, Config
import argparse
from traycortex.borgmatic import run_borgmatic

title = "Borgmatic"
darkmode = True

res = resources.files(traycortex.images)
# standard image and image while running
image = Image.open(res / "borgmatic.png")
image_r = Image.open(res / "borgmatic_r.png")
# same for darkmode (inverted)
image_i = Image.open(res / "borgmatic_i.png")
image_i_r = Image.open(res / "borgmatic_i_r.png")


def get_image(running: bool = False, darkmode: bool = darkmode) -> Image.Image:
    """Return a suitable image for the tray icon"""
    if running:
        return image_i_r if darkmode else image_r
    else:
        return image_i if darkmode else image


def create_menu(c: Config, runq: queue.Queue) -> pystray.Menu:
    """Populate the tray icon menu"""
    return pystray.Menu(
        pystray.MenuItem("Engage", menu_click(runq, c)),
        pystray.MenuItem("Discard", menu_click(runq, c)),
    )


def menu_click(runq: queue.Queue, c: Config) -> Callable:
    """Return a function that will andle tray icon menu events"""

    def _menu_click(icon: pystray.Icon, query: pystray.MenuItem):
        global run_checker
        global run_runner
        if str(query) == "Engage":
            debug("runq put")
            runq.put(True)
        elif str(query) == "Discard":
            close_checker(c)
            runq.put(False)
            icon.stop()

    return _menu_click


def borgmatic_checker(icon: pystray.Icon, c: Config, port: int = defaults.DEFAULT_PORT):
    """Return a function that will report the status of borgmatic

    This will listen on a socket for incoming messages and notify the user
    or change the tray icon according to the current status of borgmatic.
    """

    def _borgmatic_checker():
        listener = Listener((defaults.LISTEN_HOST, port), authkey=c.authkey)
        notice("accepting connections")
        while True:
            try:
                conn = listener.accept()
            except AuthenticationError as e:
                err(f"Authentication error: {e}")
                continue
            msg = conn.recv()
            debug(f"msg: {msg}")
            if msg == defaults.MSG_JOB_STARTED:
                icon.icon = get_image(running=True)
                icon.notify("Backup started")
                conn.close()
            if msg == defaults.MSG_JOB_FINISHED:
                icon.icon = get_image()
                icon.notify("Finished backup")
                conn.close()
            if msg == defaults.MSG_CLOSE:
                debug("closing")
                conn.close()
                break
        listener.close()
        notice("stop listening")

    return _borgmatic_checker


def borgmatic_runner(icon: pystray.Icon, c: Config, runq: queue.Queue) -> Callable:
    """Return a function that will run borgmatic when receiving a True value in runq"""

    def _borgmatic_runner():
        while True:
            if runq.get():
                icon.icon = get_image(running=True)
                icon.notify("Commencing backup...")
                notice("Running borgmatic...")
                run_borgmatic(c)
                notice("Done.")
                icon.icon = get_image()
                icon.notify("Finished backup")
            else:
                debug("runq is false")
                break

    return _borgmatic_runner


def app() -> int:
    """A tray app showing the status of borgmatic and offering a few actions"""
    parser = argparse.ArgumentParser(
        prog=defaults.APP_NAME, description="Tray icon for borgmatic"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument(
        "-c", "--config", help=f"{defaults.APP_NAME} configuration file"
    )
    args = parser.parse_args()
    traycortex.log.DEBUG = args.debug
    try:
        if args.config:
            c = Config(args.config)
        else:
            c = Config.findConfig()
    except ConfigError:
        return 1
    runq = queue.Queue()
    icon = pystray.Icon(
        defaults.APP_NAME, get_image(), title, menu=create_menu(c, runq)
    )
    checker = threading.Thread(target=borgmatic_checker(icon, c))
    checker.start()
    runner = threading.Thread(target=borgmatic_runner(icon, c, runq))
    runner.start()
    icon.run()
    return 0
