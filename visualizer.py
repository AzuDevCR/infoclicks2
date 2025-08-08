__version__ = '2.3.0'

import os, sys
import json
from json.decoder import JSONDecodeError
import matplotlib
matplotlib.use('TkAgg')

matplotlib.rcParams['keymap.quit'] = []
matplotlib.rcParams['keymap.zoom'] = []
matplotlib.rcParams['keymap.save'] = []
matplotlib.rcParams['keymap.fullscreen'] = []
matplotlib.rcParams['keymap.grid'] = []
matplotlib.rcParams['keymap.pan'] = []

import matplotlib.pyplot as plt
plt.rcParams['keymap.xscale'].remove('k')
plt.rcParams['keymap.yscale'].remove('l')

import matplotlib.image as mpimg


from matplotlib.animation import FuncAnimation
#from mpl_toolkits.mplot3d import Axes3D

from matplotlib import cm
from matplotlib.colors import Normalize
from matplotlib.image import imread

def getPath(relPath):
    if getattr(sys, 'frozen', False):
        basePath = sys._MEIPASS
    else:
        basePath = os.path.abspath(".")
    return os.path.join(basePath, relPath)
# bgImg = mpimg.imread(getPath("bck.jpg"))
# img_extent = [0, 100, 0, 100]  # Eje X de 0 a 100, eje Y de 0 a 100
# img_artist = ax.imshow(bgImg, extent=img_extent, aspect='auto', zorder=0)

def startVisualizer():
    fig, ax = plt.subplots(figsize=(10, 6))
    imgBCK = imread(getPath("bck.jpg"))

    fig.canvas.manager.set_window_title(f"InfoClicks {__version__}")
    fig.figimage(imgBCK, xo=0, yo=0, alpha=0.3, zorder=0)
    
    bars = ax.bar([], [], alpha=0.8, edgecolor="white", linewidth=1.2, width=0.5)

    def update(frame):
        ax.clear()

        # ax.set_title("InfoClicks Live Stats", fontsize=16, color='cyan')
        #ax.set_ylabel("Pulsaciones", fontsize=12, color='white')
        ax.tick_params(axis='x', labelrotation=45, colors='white')
        ax.tick_params(axis='y', colors='white')
        ax.set_facecolor('#292929')
        fig.patch.set_facecolor('#292929')

        try:
            with open("infoClicks.json", "r") as f:
                data = json.load(f)
        except (FileNotFoundError, JSONDecodeError):
            return

        all_counts = {**data.get('clicks', {}), **data.get('keys', {})}
        if not all_counts:
            return

        keys = list(all_counts.keys())
        values = list(all_counts.values())

        norm = Normalize(vmin=0, vmax=max(values))
        cmap = cm.get_cmap('inferno')

        colors = [cmap(norm(v)) for v in values]
        bars = ax.bar(keys, values, color=colors, edgecolor='white', linewidth=1.2)

        for bar, key, val in zip(bars, keys, values):
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.5,
                f'{val}',
                ha='center', va='bottom',
                fontsize=12,
                color='white',
                rotation=30 if len(keys) > 15 else 0
            )

        # Este paso sincroniza los ticks con las etiquetas
        ax.set_xticks(range(len(keys)))
        ax.set_xticklabels(keys, rotation=45, ha='right', color='white')

        ax.set_ylim(0, max(values) + 5)

        return bars

    global ani
    ani = FuncAnimation(fig, update, interval=500, cache_frame_data=False)
    plt.tight_layout()

    fig.subplots_adjust(
        left=0.1,
        right=0.95,
        top=0.92,
        bottom=0.2
    )

    plt.show()
