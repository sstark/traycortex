import pystray
from PIL import Image
import threading
import time
import queue

run_checker = True
run_runner = True
image = Image.open("borgmatic.png")
image_i = Image.open("borgmatic_i.png")
image_i_r = Image.open("borgmatic_i_r.png")

def after_click(icon, query):
    global run_checker
    global run_runner
    if str(query) == "Engage":
        runq.put("True")
    elif str(query) == "Discard":
        run_checker = False
        run_runner = False
        icon.stop()


def notif(icon, _):
    icon.notify("bla")


def ch_icon(icon, query):
    if str(query) == "Icon Black":
        icon.icon = image
    if str(query) == "Icon White":
        icon.icon = image_i


def check_borgmatic():
    while run_checker:
        time.sleep(1)

def run_borgmatic():
    while run_runner:
        runq.get()
        icon.icon = image_i_r
        icon.title = "Running"
        print("Running borgmatic...")
        time.sleep(5)
        print("Done.")
        icon.icon = image_i
        icon.title = "Idle"


icon = pystray.Icon("bmsystray", image_i, "Borgmatic", menu=pystray.Menu(
    pystray.MenuItem("Engage", after_click),
    pystray.MenuItem("Notify", notif),
    pystray.MenuItem("Icon Black", ch_icon),
    pystray.MenuItem("Icon White", ch_icon),
    pystray.MenuItem("Discard", after_click)))

checker = threading.Thread(target=check_borgmatic)
checker.start()

runq = queue.Queue()
runner = threading.Thread(target=run_borgmatic)
runner.start()
icon.run()
