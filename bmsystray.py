import pystray
from PIL import Image

image = Image.open("borgmatic.png")
image_i = Image.open("borgmatic_i.png")

def after_click(icon, query):
    if str(query) == "Run Borgmatic":
        print("Running borgmatic...")
    elif str(query) == "Exit":
        icon.stop()


def notif(icon, query):
    icon.notify("bla")


def ch_icon(icon, query):
    if str(query) == "Icon Black":
        icon.icon = image
    if str(query) == "Icon White":
        icon.icon = image_i


icon = pystray.Icon("bmsystray", image_i, "Borgmatic", menu=pystray.Menu(
    pystray.MenuItem("Run Borgmatic", after_click),
    pystray.MenuItem("Notify", notif),
    pystray.MenuItem("Icon Black", ch_icon),
    pystray.MenuItem("Icon White", ch_icon),
    pystray.MenuItem("Exit", after_click)))
 
icon.run()
