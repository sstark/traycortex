import pystray
from PIL import Image
import threading
import time

run_checker = True
image = Image.open("borgmatic.png")
image_i = Image.open("borgmatic_i.png")

def after_click(icon, query):
    global run_checker
    if str(query) == "Run Borgmatic":
        print("Running borgmatic...")
    elif str(query) == "Exit":
        run_checker = False
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
        if icon.icon == image:
            icon.icon = image_i
            continue
        if icon.icon == image_i:
            icon.icon = image


icon = pystray.Icon("bmsystray", image_i, "Borgmatic", menu=pystray.Menu(
    pystray.MenuItem("Run Borgmatic", after_click),
    pystray.MenuItem("Notify", notif),
    pystray.MenuItem("Icon Black", ch_icon),
    pystray.MenuItem("Icon White", ch_icon),
    pystray.MenuItem("Exit", after_click)))

checker = threading.Thread(target=check_borgmatic)
checker.start()
icon.run()
