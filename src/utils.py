from datetime import datetime, timezone
from math import prod
import os
import matplotlib.pyplot as plt
from PIL import Image

GITHUB_BADGE = Image.open("../assets/GitHub.png")

GITHUB_DARK = "#0D1117"

MAPBOX_STYLE_TOKEN_PATH = "../data/mapbox_style_token.txt"
MAPBOX_STYLE_ID_PATH = "../data/mapbox_style_id.txt"
DATASHEET_ID_PATH = "../data/datasheet_id.txt"
JOURNEYS_PATH = "../data/journeys_coords"
DATASET_PATH = "../data/dataset.csv"


def dark_figure(subplots=(1, 1), figsize=(7, 5.2), projection=None, grid=False):
    fig = plt.figure(facecolor=GITHUB_DARK, figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor=GITHUB_DARK, projection=projection)
        )
        axes[ii].tick_params(axis="x", colors="white", which="both")
        axes[ii].tick_params(axis="y", colors="white", which="both")
        axes[ii].yaxis.label.set_color("white")
        axes[ii].xaxis.label.set_color("white")
        axes[ii].title.set_color("white")
        if grid:
            axes[ii].set_axisbelow(True)
            axes[ii].grid(color="#161C22", linewidth=0.5)
        for i in axes[ii].spines:
            axes[ii].spines[i].set_color("white")
    return fig, axes


def finish_map(
        fig,
        axes,
        path,
        show,
        save_transparent=False,
        colorbar=None,
):
    axes[0].set_xlabel(
        datetime.now(timezone.utc).strftime(
            "Plot generated on %Y/%m/%d at %H:%M:%S UTC."
        ),
        color="dimgray",
        labelpad=10,
    )

    if colorbar is not None:
        colorbar.ax.xaxis.set_tick_params(color="white")
        colorbar.outline.set_edgecolor("white")
        plt.setp(plt.getp(colorbar.ax, "xticklabels"), color="white", fontsize=8)
    fig.subplots_adjust(bottom=0.12)
    fig_axes2 = fig.add_axes([0.014, 0.02, 0.3, 0.3], anchor="SW", zorder=1)
    fig_axes2.imshow(GITHUB_BADGE)
    fig_axes2.axis("off")
    if save_transparent:
        plt.savefig("../plots/" + path + "_transparent.png", transparent=True, dpi=500)
    plt.savefig("../plots/" + path + ".png", transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def get_mapbox_secrets():
    # Mapbox style token
    if os.path.exists(MAPBOX_STYLE_TOKEN_PATH):
        print("Using Mapbox style token from file")
        with open(MAPBOX_STYLE_TOKEN_PATH, 'r') as f:
            mapbox_style_token = f.read()
    elif "MAPBOX_STYLE_TOKEN" in os.environ:
        print("Using Mapbox style token from environment")
        mapbox_style_token = os.environ["MAPBOX_STYLE_TOKEN"]
    else:
        raise Exception("No Mapbox style token found")

    # Mapbox style ID
    if os.path.exists(MAPBOX_STYLE_ID_PATH):
        print("Using Mapbox style ID from file")
        with open(MAPBOX_STYLE_ID_PATH, 'r') as f:
            mapbox_style_id = f.read()
    elif "MAPBOX_STYLE_ID" in os.environ:
        print("Using Mapbox style ID from environment")
        mapbox_style_id = os.environ["MAPBOX_STYLE_ID"]
    else:
        raise Exception("No Mapbox style ID found")
    return mapbox_style_token, mapbox_style_id


def get_datasheet_id():
    if os.path.exists(DATASHEET_ID_PATH):
        print("Using Datasheet ID from file")
        with open(DATASHEET_ID_PATH, 'r') as f:
            datasheet_id = f.read()
    elif "DATASHEET_ID" in os.environ:
        print("Using Datasheet ID from environment")
        datasheet_id = os.environ["DATASHEET_ID"]
    else:
        raise Exception("No Datasheet ID found")
    return datasheet_id
