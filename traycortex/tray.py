from collections.abc import Callable
import pystray
from PIL import Image
import threading
import time
import queue


p_name = __package__ or __name__
title = "Borgmatic"
run_checker = True
run_runner = True
darkmode = True

# standard image and image while running
image = Image.open("borgmatic.png")
image_r = Image.open("borgmatic.png")
# same for darkmode (inverted)
image_i = Image.open("borgmatic_i.png")
image_i_r = Image.open("borgmatic_i_r.png")


def get_image(running: bool = False, darkmode: bool = darkmode) -> Image.Image:
    if running:
        return image_i_r if darkmode else image_r
    else:
        return image_i if darkmode else image
        


def create_menu() -> pystray.Menu:
    return pystray.Menu(
        pystray.MenuItem("Engage", menu_click),
        pystray.MenuItem("Discard", menu_click)
    )


def menu_click(icon, query):
    global run_checker
    global run_runner
    if str(query) == "Engage":
        runq.put(True)
    elif str(query) == "Discard":
        run_checker = False
        run_runner = False
        runq.put(False)
        icon.stop()


def borgmatic_checker():
    while run_checker:
        time.sleep(0.5)


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
    icon = pystray.Icon(p_name, get_image(), title, menu=create_menu())
    checker = threading.Thread(target=borgmatic_checker)
    checker.start()
    runq = queue.Queue()
    runner = threading.Thread(target=borgmatic_runner(icon, runq))
    runner.start()
    icon.run()
