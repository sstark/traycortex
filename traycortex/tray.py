from collections.abc import Callable
import pystray
from PIL import Image
import threading
import time
import queue
from importlib import resources
import traycortex.images
from multiprocessing.connection import Listener
from multiprocessing.connection import Client

DEFAULT_PORT = 35234
MSG_JOB_STARTED = "job started"
MSG_JOB_FINISHED = "job finished"
MSG_CLOSE = "close"
p_name = __package__ or __name__
title = "Borgmatic"
run_runner = True
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
        pystray.MenuItem("Discard", menu_click(runq))
    )


def menu_click(runq: queue.Queue) -> Callable:

    def _menu_click(icon: pystray.Icon, query: pystray.MenuItem):
        global run_checker
        global run_runner
        if str(query) == "Engage":
            print("runq put")
            runq.put(True)
        elif str(query) == "Discard":
            run_runner = False
            close_checker()
            runq.put(False)
            icon.stop()
    return _menu_click


def close_checker(port: int = DEFAULT_PORT):
    conn = Client(("localhost", port))
    conn.send(MSG_CLOSE)
    conn.close()


def borgmatic_checker(icon: pystray.Icon, port: int = DEFAULT_PORT):

    def _borgmatic_checker():
        listener = Listener(("localhost", port))
        print("accepting connections")
        while True:
            conn = listener.accept()
            msg = conn.recv()
            print(f"msg: {msg}")
            if msg == MSG_JOB_STARTED:
                icon.icon = get_image(running=True)
                conn.close()
            if msg == MSG_JOB_FINISHED:
                icon.icon = get_image()
                conn.close()
            if msg == MSG_CLOSE:
                print("closing")
                conn.close()
                break
        listener.close()
        print("stop listening")
    return _borgmatic_checker


def borgmatic_runner(icon: pystray.Icon, runq: queue.Queue) -> Callable:

    def _borgmatic_runner():
        while run_runner:
            if runq.get():
                icon.icon = get_image(running=True)
                icon.notify("Commencing backup...")
                print("Running borgmatic...")
                time.sleep(5)
                print("Done.")
                icon.icon = get_image()
                icon.notify("Finished backup")
    return _borgmatic_runner


def app():
    runq = queue.Queue()
    icon = pystray.Icon(p_name, get_image(), title, menu=create_menu(runq))
    checker = threading.Thread(target=borgmatic_checker(icon))
    checker.start()
    runner = threading.Thread(target=borgmatic_runner(icon, runq))
    runner.start()
    icon.run()
