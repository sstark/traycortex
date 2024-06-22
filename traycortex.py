from pystray import Menu, MenuItem, Icon
from PIL import Image
import threading
import time
import queue

run_checker = True
run_runner = True
image = Image.open("borgmatic.png")
image_i = Image.open("borgmatic_i.png")
image_i_r = Image.open("borgmatic_i_r.png")

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


def check_borgmatic():
    while run_checker:
        time.sleep(1)


def run_borgmatic():
    while run_runner:
        if runq.get():
            icon.icon = image_i_r
            icon.notify("Commencing backup...")
            print("Running borgmatic...")
            time.sleep(5)
            print("Done.")
            icon.icon = image_i
            icon.notify("Finished backup")


def create_menu() -> Menu:
    return Menu(
        MenuItem("Engage", menu_click),
        MenuItem("Discard", menu_click)
    )


icon = Icon("traycortex", image_i, "Borgmatic", menu=create_menu())

checker = threading.Thread(target=check_borgmatic)
checker.start()

runq = queue.Queue()
runner = threading.Thread(target=run_borgmatic)
runner.start()
icon.run()