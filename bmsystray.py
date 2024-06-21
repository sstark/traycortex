import pystray
from PIL import Image

image = Image.open("borgmatic.png")

def after_click(icon, query):
    if str(query) == "GeeksforGeeks Website":
        print("The Best Place to learn anything Tech \
        Related -> https://www.geeksforgeeks.org/")
        # icon.stop()
    elif str(query) == "GeeksforGeeks Youtube":
        print("Youtube Channel of GeeksforGeeks \
        is -> https://www.youtube.com/@GeeksforGeeksVideos")
        # icon.stop()
    elif str(query) == "GeeksforGeeks LinkedIn":
        print("LinkedIn of GeeksforGeeks \
        is -> https://www.linkedin.com/company/geeksforgeeks/")
    elif str(query) == "Exit":
        icon.stop()


icon = pystray.Icon("GFG", image, "GeeksforGeeks", menu=pystray.Menu(
    pystray.MenuItem("GeeksforGeeks Website", after_click),
    pystray.MenuItem("GeeksforGeeks Youtube", after_click),
    pystray.MenuItem("GeeksforGeeks LinkedIn", after_click),
    pystray.MenuItem("Exit", after_click)))
 
icon.run()

