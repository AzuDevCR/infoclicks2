__version__ = '2.3.0'
__author__ = 'AzuDevCR'


import os, sys
import json
import time
import threading

from pynput import mouse
from pynput import keyboard
from pynput.keyboard import Listener as KeyListener
from pynput.keyboard import Key
from collections import defaultdict
from rich.console import Console
from rich.table import Table
from rich.table import box

from pygame.mixer import init, Sound

from visualizer import startVisualizer

def getPath(relPath):
    if getattr(sys, 'frozen', False):
        basePath = sys._MEIPASS
    else:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relPath)

keyCount = defaultdict(int)
pressedKeys = set()
enterText = False

#keys for internal functionalities, not to be logged
utilityKeys = [Key.home, Key.pause, Key.insert]

#Audio
init(frequency=44100, size=-16, channels=2, buffer=512)
resetClip = Sound(getPath("reset.wav"))
textModeOffClip = Sound(getPath("textModeOff.wav"))
textModeOnClip = Sound(getPath("textModeOn.wav"))

clickCount = {
    'left': 0,
    'right': 0,
    'middle': 0,
    'side_4': 0, #back
    'side_5': 0, #Forward
}

def resetData():
    keyCount.clear()
    for key in clickCount:
        clickCount[key] = 0
    
    with open("infoClicks.json", "w") as f:
        json.dump({"keys": {}, "clicks": {}}, f)

    Sound.play(resetClip)

def cleanKeyName(k):
    if isinstance(k, Key):
        return str(k).replace('Key.', '').replace('_l', '').replace('_r', '').capitalize()
    try:
        return k.char.upper()
    except AttributeError:
        return str(k)

def startMouse():
    with mouse.Listener(on_click=onClick) as ml:
        ml.join()

def startKeyboard():
    with keyboard.Listener(on_press=onKeyPress, on_release=onKeyRelease) as kl:
        kl.join()

def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')

def onKeyPress(key):

    global enterText

    #Enter text mode
    if key == Key.insert:
        if enterText == False:
            enterText = True
            Sound.play(textModeOnClip)
        else:
            enterText = False
            Sound.play(textModeOffClip)

    if key == Key.home:
        resetData()
    
    if key == Key.pause:
        print("<3")
        os._exit(0)

    keyStr = cleanKeyName(key)

    if keyStr in pressedKeys:
        return

    if not enterText and key not in utilityKeys:
        pressedKeys.add(keyStr)
        keyCount[keyStr] += 1

    # clearScreen()
    # showInfo()
    saveCountsToJson()

def onKeyRelease(key):
    keyStr = cleanKeyName(key)
    pressedKeys.discard(keyStr)

def onClick(x, y, button, pressed):
    if pressed:
        if button == mouse.Button.left:
            clickCount['left'] += 1
        elif button == mouse.Button.right:
            clickCount['right'] += 1
        elif button == mouse.Button.middle:
            clickCount['middle'] += 1
        elif button == mouse.Button.button8:
            clickCount['side_4'] +=1
        elif button == mouse.Button.button9:
            clickCount['side_5'] += 1

        # clearScreen()
        # showInfo()
        saveCountsToJson()

def setCountColor(button):
    '''button is any clickCount[button] or keyCount[key]'''
    if button <= 0 and button <= 300:
        return "bright_white"
    elif button > 300 and button <= 700:
        return "green3"
    elif button > 700 and button <= 1800:
        return "yellow2"
    elif button > 1800 and button <= 2500:
        return "orange_red1"
    elif button > 2500 and button <= 4444:
        return "red1"
    elif button > 4444:
        return "light_goldenrod1"

def showInfo():
    console = Console()
    table = Table(title=f"InfoClicks {__version__}", box=box.HEAVY)

    table.add_column("Button/Key", style="aquamarine1", no_wrap=True)
    table.add_column("Count", style="aquamarine1", justify="right")

    table.add_row("Left", str(clickCount['left']), style=setCountColor(clickCount['left']))
    table.add_row("Right", str(clickCount['right']), style=setCountColor(clickCount['right']))
    table.add_row("Middle", str(clickCount['middle']), style=setCountColor(clickCount['middle']))
    table.add_row("LBack", str(clickCount['side_4']), style=setCountColor(clickCount['side_4']))
    table.add_row("LForward", str(clickCount['side_5']), style=setCountColor(clickCount['side_5']))

    for key, count in keyCount.items():
        table.add_row(f"{key}", str(count), style=setCountColor(count))

    console.print(table)

def saveCountsToJson():
    data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "clicks": clickCount,
        "keys": dict(keyCount)
    }

    with open ("infoClicks.json", "w") as f:
        json.dump(data, f, indent=4)


def main():
    print(f"InfoClicks {__version__} Pause/Break para terminar")

    mouseThread = threading.Thread(target=startMouse)
    keyboardThread = threading.Thread(target=startKeyboard)

    mouseThread.start()
    keyboardThread.start()

    mouseThread.join()
    keyboardThread.join()

if __name__ == "__main__":
    from threading import Thread

    mainThread = Thread(target=main, daemon=True)
    mainThread.start()

    startVisualizer()
