from datetime import timedelta
from math import prod, ceil, floor

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

GITHUB_BADGE = Image.open("../assets/GitHub.png")

GITHUB_DARK = "#0D1117"
COLORS_DICT = {
    "red": "#e41a1c",
    "orange": "#ff7f00",
    "blue": "#377eb8",
    "pink": "#f781bf",
    "yellow": "#dede00",
    "green": "#4daf4a",
    "grey": "#999999",
    "purple": "#984ea3",
}
COLORS = ["blue", "orange", "red", "green", "pink", "yellow", "purple", "grey"]
COLORS = [COLORS_DICT[i] for i in COLORS]

MAX_DAYS_PER_YEAR = 366

MONTHS_TICKS = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]

MONTHS_LABELS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

DURATION_TIERS = [
    (0, 2, "up to 2h"),
    (2, 4, "2h to 4h"),
    (4, 6, "4h to 6h"),
    (6, 8, "6h to 8h"),
    (8, 10, "8h to 10h"),
    (10, 12, "10h to 12h"),
    (12, 14, "12h to 14h"),
    (14, 999, "over 14h"),
]


def dark_figure(subplots=(1, 1), figsize=(7, 5.2), projection=None, grid=False):
    fig = plt.figure(facecolor=GITHUB_DARK, figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(
                subplots[0],
                subplots[1],
                ii + 1,
                facecolor=GITHUB_DARK,
                projection=projection,
            )
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
    _axes,
    path,
    show=False,
    save_transparent=False,
    colorbar=None,
    logo_position=None,
):
    if colorbar is not None:
        colorbar.ax.xaxis.set_tick_params(color="white")
        colorbar.outline.set_edgecolor("white")
        plt.setp(plt.getp(colorbar.ax, "xticklabels"), color="white", fontsize=8)
    fig.subplots_adjust(bottom=0.12)
    if logo_position:
        fig_axes2 = fig.add_axes(logo_position, anchor="NW", zorder=1)
    else:
        fig_axes2 = fig.add_axes([0.014, 0.02, 0.3, 0.3], anchor="SW", zorder=1)
    fig_axes2.imshow(GITHUB_BADGE)
    fig_axes2.axis("off")
    if save_transparent:
        plt.savefig("../plots/" + path + "_transparent.png", transparent=True, dpi=500)
    plt.savefig("../plots/" + path + ".png", transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def finish_figure(
    fig,
    axes,
    path,
    show=False,
    save_transparent=False,
    override_ylim=None,
    override_yticks=None,
    colorbar=None,
):
    ticks = None
    if override_yticks is None:
        ticks = axes_ticks(axes[0].get_ylim()[1])
        axes[0].set_yticks(ticks)
    elif override_yticks:
        ticks = override_yticks
        axes[0].set_yticks(ticks)
    if override_ylim is None:
        axes[0].set_ylim([0, ticks[-1] * 1.25])
    elif override_ylim:
        axes[0].set_ylim(override_ylim)
    if colorbar is not None:
        colorbar.ax.xaxis.set_tick_params(color="white")
        colorbar.outline.set_edgecolor("white")
        plt.setp(plt.getp(colorbar.ax, "xticklabels"), color="white", fontsize=8)
    fig.subplots_adjust(bottom=0.20)
    fig_axes2 = fig.add_axes([0.014, 0.02, 0.3, 0.3], anchor="SW", zorder=1)
    fig_axes2.imshow(GITHUB_BADGE)
    fig_axes2.axis("off")
    if save_transparent:
        plt.savefig("../plots/" + path + "_transparent.png", transparent=True, dpi=500)
    plt.savefig("../plots/" + path + ".png", transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def axes_ticks(value):
    value = floor(value)
    if value < 5:
        interval = 1
    elif value < 14:
        interval = 2
    elif value < 30:
        interval = 5
    elif value < 100:
        interval = 10
    elif value < 200:
        interval = 25
    elif value < 500:
        interval = 50
    elif value < 1000:
        interval = 100
    elif value < 2000:
        interval = 250
    elif value < 5000:
        interval = 500
    elif value < 10000:
        interval = 1000
    elif value < 20000:
        interval = 2500
    elif value < 50000:
        interval = 5000
    else:
        interval = 1
    upper_bound = interval * (ceil(value / interval) + 1)
    return np.arange(0, upper_bound, interval)


def prepare_legend(reverse):
    handles_, labels_ = plt.gca().get_legend_handles_labels()
    handles_ = [k for j in [handles_[i::4] for i in range(4)] for k in j]
    labels_ = [k for j in [labels_[i::4] for i in range(4)] for k in j]
    if reverse:
        return handles_[::-1], labels_[::-1]
    else:
        return handles_, labels_


def get_trip_labels(start_day, end_day, fixed_number=None):
    if start_day.month == end_day.month and start_day.year == end_day.year:
        header = start_day.strftime("%B %Y")
    elif start_day.year == end_day.year:
        header = f"{start_day.strftime('%B')} - {end_day.strftime('%B %Y')}"
    else:
        header = f"{start_day.strftime('%B %Y')} - {end_day.strftime('%B %Y')}"

    labels = []
    for ii in range((end_day - start_day).days + 1):
        labels.append((start_day + timedelta(days=ii)).day)

    if fixed_number is not None:
        step = (len(labels) - 1) // (fixed_number - 1)  # Ste
        labels = [labels[i * step] for i in range(fixed_number)]
    return header, labels
