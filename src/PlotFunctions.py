from datetime import datetime, timezone
from math import prod, ceil, floor

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Badge_DataLL2 = Image.open("assets/DataByLL2.png")
Badge_GitHub = Image.open("../assets/GitHub.png")

# Colors & Labels
github_dark = "#0D1117"
colors_dict = {
    "red": "#e41a1c",
    "orange": "#ff7f00",
    "blue": "#377eb8",
    "pink": "#f781bf",
    "yellow": "#dede00",
    "green": "#4daf4a",
    "grey": "#999999",
    "purple": "#984ea3",
}
colors = ["blue", "orange", "red", "green", "pink", "yellow", "purple", "grey"]
colors = [colors_dict[i] for i in colors]
SPF_colors = ["#4daf4a", "#ff7f00", "#e41a1c"]
SPF_labels = ["Success", "Partial Failure", "Failure"]
reusability_labels = [
    "New & Not recovered",
    "New & Recovered",
    "Reused & Not recovered",
    "Reused & Recovered",
]
reusability_colors = [colors_dict[i] for i in ["blue", "yellow", "orange", "green"]]


monthsLabels = [
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

monthsTicks = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]


# Functions for figures
def dark_figure(subplots=(1, 1), figsize=(7, 5.2), projection=None, grid=False):
    fig = plt.figure(facecolor=github_dark, figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor=github_dark, projection=projection)
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


def dark_map(subplots=(1, 1), figsize=(7, 5.2), projection=ccrs.Robinson()):
    fig = plt.figure(facecolor=github_dark, figsize=figsize)
    axes = []
    for ii in range(0, prod(subplots)):
        axes.append(
            fig.add_subplot(subplots[0], subplots[1], ii + 1, facecolor=github_dark, projection=projection)
        )
        # axes[ii].tick_params(axis="x", colors="white", which="both")
        # axes[ii].tick_params(axis="y", colors="white", which="both")
        # axes[ii].yaxis.label.set_color("white")
        # axes[ii].xaxis.label.set_color("white")
        # axes[ii].title.set_color("white")
        # for i in axes[ii].spines:
        #     axes[ii].spines[i].set_color("white")
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
    plt.tight_layout()
    if colorbar is not None:
        colorbar.ax.xaxis.set_tick_params(color="white")
        colorbar.outline.set_edgecolor("white")
        plt.setp(plt.getp(colorbar.ax, "xticklabels"), color="white", fontsize=8)
    fig.subplots_adjust(bottom=0.12)
    # fig_axes1 = fig.add_axes([0.678, 0.02, 0.3, 0.3], anchor="SE", zorder=1)
    # fig_axes1.imshow(Badge_DataLL2)
    # fig_axes1.axis("off")
    fig_axes2 = fig.add_axes([0.014, 0.02, 0.3, 0.3], anchor="SW", zorder=1)
    fig_axes2.imshow(Badge_GitHub)
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
        show,
        save_transparent=False,
        override_ylim=None,
        override_yticks=None,
        colorbar=None,
):
    axes[0].set_xlabel(
        datetime.now(timezone.utc).strftime(
            "Plot generated on %Y/%m/%d at %H:%M:%S UTC."
        ),
        color="dimgray",
        labelpad=10,
    )
    plt.tight_layout()
    if override_yticks is None:
        ticks = axes_ticks(axes[0].get_ylim()[1])
        axes[0].set_yticks(ticks)
    else:
        ticks = override_yticks
        axes[0].set_yticks(ticks)
    if override_ylim is None:
        axes[0].set_ylim([0, ticks[-1] * 1.25])
    else:
        axes[0].set_ylim(override_ylim)
    if colorbar is not None:
        colorbar.ax.xaxis.set_tick_params(color="white")
        colorbar.outline.set_edgecolor("white")
        plt.setp(plt.getp(colorbar.ax, "xticklabels"), color="white", fontsize=8)
    fig.subplots_adjust(bottom=0.20)
    # fig_axes1 = fig.add_axes([0.678, 0.02, 0.3, 0.3], anchor="SE", zorder=1)
    # fig_axes1.imshow(Badge_DataLL2)
    # fig_axes1.axis("off")
    fig_axes2 = fig.add_axes([0.014, 0.02, 0.3, 0.3], anchor="SW", zorder=1)
    fig_axes2.imshow(Badge_GitHub)
    fig_axes2.axis("off")
    if save_transparent:
        plt.savefig("../plots/" + path + "_transparent.png", transparent=True, dpi=500)
    plt.savefig("../plots/" + path + ".png", transparent=False, dpi=500)
    if show:
        plt.show()
    plt.close()


def prepare_legend(reverse):
    handles_, labels_ = plt.gca().get_legend_handles_labels()
    handles_ = [k for j in [handles_[i::4] for i in range(4)] for k in j]
    labels_ = [k for j in [labels_[i::4] for i in range(4)] for k in j]
    if reverse:
        return handles_[::-1], labels_[::-1]
    else:
        return handles_, labels_


def flatten(list_of_lists):
    flattened_list = []
    for i in list_of_lists:
        if isinstance(i, list):
            flattened_list += i
        else:
            flattened_list.append(i)
    return flattened_list


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
    else:
        interval = 1
    upper_bound = interval * (ceil(value / interval) + 1)
    return np.arange(0, upper_bound, interval)


def remove_html_margins(path):
    with open(path, "r") as f:
        lines = f.readlines()
    with open(path, "w") as f:
        for line in lines:
            if "<head>" in line:
                f.write(
                    line.replace("<head>", "<head><style>body { margin: 0; }</style>")
                )
            else:
                f.write(line)


def finish_plotly_figure(fig, path):
    fig.update_layout(
        xaxis=dict(
            title=datetime.now(timezone.utc).strftime(
                "Plot generated on %Y/%m/%d at %H:%M:%S UTC."
            ),
            titlefont=dict(color="dimgray"),
        ),
        legend=dict(font=dict(size=17)),
        title=dict(font=dict(size=17)),
    )
    # fig.add_layout_image(
    #     dict(
    #         source=Badge_DataLL2,
    #         xanchor="right",
    #         yanchor="top",
    #         xref="x domain",
    #         yref="y domain",
    #         x=1,
    #         y=0.99,
    #         sizex=0.2,
    #         sizey=0.2,
    #     )
    # )
    fig.add_layout_image(
        dict(
            source=Badge_GitHub,
            xanchor="left",
            yanchor="top",
            xref="x domain",
            yref="y domain",
            x=0,
            y=0.99,
            sizex=0.2,
            sizey=0.2,
        )
    )
    fig.update_annotations()
    fig.write_html("plots/" + path)
    remove_html_margins("plots/" + path)
