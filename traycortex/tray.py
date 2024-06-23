from collections.abc import Callable
import pystray
from PIL import Image
import threading
import time
import queue
from importlib import resources
import traycortex.images
from multiprocessing.connection import Listener
from traycortex.client import close_checker
from traycortex import defaults
from traycortex.log import debug, notice
from traycortex.config import ConfigError, Config
import argparse
import sys

title = "Borgmatic"
darkmode = True

res = resources.files(traycortex.images)
# standard image and image while running
image = Image.open(res / "borgmatic.png")
image_r = Image.open(res / "borgmatic.png")
# same for darkmode (inverted)
image_i = Image.open(res / "borgmatic_i.png")
image_i_r = Image.open(res / "borgmatic_i_r.png")


def get_image(running: bool = False, darkmode: bool = darkmode) -> Image.Image:
    if running:
        return image_i_r if darkmode else image_r
    else:
        return image_i if darkmode else image


def create_menu(runq: queue.Queue) -> pystray.Menu:
    return pystray.Menu(
        pystray.MenuItem("Engage", menu_click(runq)),
        pystray.MenuItem("Discard", menu_click(runq)),
    )


def menu_click(runq: queue.Queue) -> Callable:

    def _menu_click(icon: pystray.Icon, query: pystray.MenuItem):
        global run_checker
        global run_runner
        if str(query) == "Engage":
            debug("runq put")
            runq.put(True)
        elif str(query) == "Discard":
            close_checker()
            runq.put(False)
            icon.stop()

    return _menu_click


def borgmatic_checker(icon: pystray.Icon, port: int = defaults.DEFAULT_PORT):

    def _borgmatic_checker():
        listener = Listener((defaults.LISTEN_HOST, port))
        notice("accepting connections")
        while True:
            conn = listener.accept()
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


def borgmatic_runner(icon: pystray.Icon, runq: queue.Queue) -> Callable:

    def _borgmatic_runner():
        while True:
            if runq.get():
                icon.icon = get_image(running=True)
                icon.notify("Commencing backup...")
                notice("Running borgmatic...")
                time.sleep(5)
                notice("Done.")
                icon.icon = get_image()
                icon.notify("Finished backup")
            else:
                debug("runq is false")
                break

    return _borgmatic_runner


def app():
    parser = argparse.ArgumentParser(
        prog=defaults.APP_NAME, description="Tray icon for borgmatic"
    )
    parser.add_argument(
        "-c", "--config", help=f"{defaults.APP_NAME} configuration file"
    )
    args = parser.parse_args()
    try:
        if args.config:
            c = Config(args.config)
        else:
            c = Config.findConfig()
    except ConfigError:
        sys.exit(1)
    runq = queue.Queue()
    icon = pystray.Icon(defaults.APP_NAME, get_image(), title, menu=create_menu(runq))
    checker = threading.Thread(target=borgmatic_checker(icon))
    checker.start()
    runner = threading.Thread(target=borgmatic_runner(icon, runq))
    runner.start()
    icon.run()
