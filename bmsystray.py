import pystray
from PIL import Image

image = Image.open("borgmatic_i.png")

def after_click(icon, query):
    if str(query) == "Run Borgmatic":
        print("Running borgmatic...")
    elif str(query) == "Exit":
        icon.stop()


icon = pystray.Icon("bmsystray", image, "Borgmatic", menu=pystray.Menu(
    pystray.MenuItem("Run Borgmatic", after_click),
    pystray.MenuItem("Exit", after_click)))
 
icon.run()

