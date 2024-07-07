from collections.abc import Callable
import pystray
from PIL import Image
import threading
import queue
from importlib import resources
import traycortex.images
from multiprocessing.connection import Listener
from multiprocessing.context import AuthenticationError
from traycortex.client import close_checker
from traycortex.defaults import (
    APP_NAME,
    LISTEN_HOST,
    MENU_ENGAGE_ALL,
    MENU_PREFIX_ENGAGE,
    MENU_DISCARD,
    MSG_JOB_ERROR,
    MSG_JOB_STARTED,
    MSG_JOB_FINISHED,
    MSG_CLOSE,
)
import traycortex.log
from traycortex.log import debug, notice, err
from traycortex.config import ConfigError, Config
import argparse
from traycortex.borgmatic import run_borgmatic, find_all_borgmatic_yaml

title = "Borgmatic"
darkmode = True

res = resources.files(traycortex.images)
# standard image and image while running
image = Image.open(res / "borgmatic.png")
image_r = Image.open(res / "borgmatic_r.png")
# same for darkmode (inverted)
image_i = Image.open(res / "borgmatic_i.png")
image_i_r = Image.open(res / "borgmatic_i_r.png")
backup_running = False


def get_image(
    running: bool = False, darkmode: bool = darkmode, error: bool = False
) -> Image.Image:
    """Return a suitable image for the tray icon"""
    if error:
        # Add colored background to image. For the error image
        # we always use the "non running" version.
        img = image_i if darkmode else image
        img_b = Image.new("RGB", (img.width, img.height), "red")
        img_b.paste(img, (0, 0), img.convert("RGBA"))
        return img_b
    if running:
        return image_i_r if darkmode else image_r
    else:
        return image_i if darkmode else image


def engage_enabled(_) -> bool:
    global backup_running
    return not backup_running


def create_menu(c: Config, runq: queue.Queue) -> pystray.Menu:
    """Populate the tray icon menu"""
    yaml_items = [
        pystray.MenuItem(
            f"{MENU_PREFIX_ENGAGE}{yaml}",
            menu_click(runq, c),
            enabled=engage_enabled,
        )
        for yaml in find_all_borgmatic_yaml()
        if yaml.exists()
    ]
    debug(f"yaml_items: {yaml_items}")
    return pystray.Menu(
        pystray.MenuItem(
            f"{MENU_PREFIX_ENGAGE}{MENU_ENGAGE_ALL}",
            menu_click(runq, c),
            enabled=engage_enabled,
        ),
        *yaml_items,
        pystray.MenuItem(MENU_DISCARD, menu_click(runq, c)),
    )


def menu_click(runq: queue.Queue, c: Config) -> Callable:
    """Return a function that will andle tray icon menu events"""

    def _menu_click(icon: pystray.Icon, query: pystray.MenuItem):
        global engage_text
        msg = str(query)
        debug(msg)
        if msg.startswith(MENU_PREFIX_ENGAGE):
            debug("runq put")
            runq.put(msg.removeprefix(MENU_PREFIX_ENGAGE))
        elif msg == MENU_DISCARD:
            close_checker(c)
            runq.put("")
            icon.stop()

    return _menu_click


def borgmatic_checker(icon: pystray.Icon, c: Config) -> Callable:
    """Return a function that will report the status of borgmatic

    This will listen on a socket for incoming messages and notify the user
    or change the tray icon according to the current status of borgmatic.
    """

    def _borgmatic_checker():
        global backup_running
        listener = Listener((LISTEN_HOST, c.port), authkey=c.authkey)
        notice("accepting connections")
        while True:
            try:
                conn = listener.accept()
            except AuthenticationError as e:
                err(f"Authentication error: {e}")
                continue
            msg = conn.recv()
            debug(f"msg: {msg}")
            if msg == MSG_JOB_ERROR:
                backup_running = False
                icon.icon = get_image(error=True)
                icon.notify("Backup error")
                conn.close()
            if msg == MSG_JOB_STARTED:
                backup_running = True
                icon.icon = get_image(running=True)
                icon.notify("Backup started")
                conn.close()
            if msg == MSG_JOB_FINISHED:
                backup_running = False
                icon.icon = get_image()
                icon.notify("Finished backup")
                conn.close()
            if msg == MSG_CLOSE:
                debug("closing")
                conn.close()
                break
            icon.update_menu()
        listener.close()
        notice("stop listening")

    return _borgmatic_checker


def borgmatic_runner(icon: pystray.Icon, c: Config, runq: queue.Queue) -> Callable:
    """Return a function that will run borgmatic when receiving a True value in runq"""

    def _borgmatic_runner():
        global backup_running
        while True:
            if msg := runq.get():
                debug(f"got message {msg}")
                debug("set backup_running to True")
                backup_running = True
                icon.icon = get_image(running=backup_running)
                icon.update_menu()
                icon.notify("Commencing backup...")
                notice("Running borgmatic...")
                ret = run_borgmatic(c, "" if msg == MENU_ENGAGE_ALL else msg)
                notice("Done.")
                if ret == 0:
                    icon.icon = get_image()
                    icon.notify("Finished backup")
                else:
                    icon.icon = get_image(error=True)
                    icon.notify(f"Backup error ({ret})")
                backup_running = False
                icon.update_menu()
            else:
                debug("runq is false")
                break

    return _borgmatic_runner


def app() -> int:
    """A tray app showing the status of borgmatic and offering a few actions"""
    parser = argparse.ArgumentParser(
        prog=APP_NAME, description="Tray icon for borgmatic"
    )
    parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parser.add_argument("-c", "--config", help=f"{APP_NAME} configuration file")
    args = parser.parse_args()
    traycortex.log.DEBUG = args.debug
    try:
        if args.config:
            c = Config(args.config)
        else:
            c = Config.findConfig()
    except ConfigError:
        return 1
    runq: "queue.Queue[str]" = queue.Queue()
    icon = pystray.Icon(APP_NAME, get_image(), title, menu=create_menu(c, runq))
    checker = threading.Thread(target=borgmatic_checker(icon, c))
    checker.start()
    runner = threading.Thread(target=borgmatic_runner(icon, c, runq))
    runner.start()
    icon.run()
    return 0
