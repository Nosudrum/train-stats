from datetime import datetime, timedelta
from math import prod, ceil, floor
import os

import matplotlib.pyplot as plt
from PIL import Image
import pytz
import numpy as np

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

MAPBOX_STYLE_TOKEN_PATH = "../data/mapbox_style_token.txt"
MAPBOX_STYLE_ID_PATH = "../data/mapbox_style_id.txt"
DATASHEET_ID_PATH = "../data/datasheet_id.txt"
ADDITIONAL_SPENDING_ID_PATH = "../data/additional_spending_id.txt"
JOURNEYS_PATH = "../data/journeys_coords/"
TRIPS_PATH = "../data/dataset.csv"
ADDITIONAL_SPENDING_PATH = "../data/additional_spending.csv"
STATIONS_PATH = "../data/stations.csv"
CUSTOM_STATIONS_PATH = "../data/custom_stations_tz.csv"

PARIS_TZ = pytz.timezone("Europe/Paris")
UTC_TZ = pytz.utc


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
    show,
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
    show,
    save_transparent=False,
    override_ylim=None,
    override_yticks=None,
    colorbar=None,
):
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


def get_mapbox_secrets():
    # Mapbox style token
    if os.path.exists(MAPBOX_STYLE_TOKEN_PATH):
        print("Using Mapbox style token from file")
        with open(MAPBOX_STYLE_TOKEN_PATH, "r") as f:
            mapbox_style_token = f.read()
    elif "MAPBOX_STYLE_TOKEN" in os.environ:
        print("Using Mapbox style token from environment")
        mapbox_style_token = os.environ["MAPBOX_STYLE_TOKEN"]
    else:
        raise Exception("No Mapbox style token found")

    # Mapbox style ID
    if os.path.exists(MAPBOX_STYLE_ID_PATH):
        print("Using Mapbox style ID from file")
        with open(MAPBOX_STYLE_ID_PATH, "r") as f:
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
        with open(DATASHEET_ID_PATH, "r") as f:
            datasheet_id = f.read()
    elif "DATASHEET_ID" in os.environ:
        print("Using Datasheet ID from environment")
        datasheet_id = os.environ["DATASHEET_ID"]
    else:
        raise Exception("No Datasheet ID found")
    return datasheet_id


def get_additional_spending_id():
    if os.path.exists(ADDITIONAL_SPENDING_ID_PATH):
        print("Using Additional Spending ID from file")
        with open(ADDITIONAL_SPENDING_ID_PATH, "r") as f:
            additional_spending_id = f.read()
    elif "ADDITIONAL_SPENDING_ID" in os.environ:
        print("Using Additional Spending ID from environment")
        additional_spending_id = os.environ["ADDITIONAL_SPENDING_ID"]
    else:
        raise Exception("No Additional Spending ID found")
    return additional_spending_id


def extract_trips_journeys(trips, filter_start=None, filter_end=None):
    trips_copy = trips.copy()
    if filter_start is not None:
        trips_copy = trips_copy[trips_copy["Departure (Local)"] >= filter_start]
    if filter_end is not None:
        trips_copy = trips_copy[trips_copy["Arrival (Local)"] <= filter_end]
    journey_counts = trips_copy["journey"].value_counts().to_frame()
    journey_distances = (
        trips_copy[["journey", "Distance (km)"]].groupby("journey").mean()
    )
    journey_firstdate = (
        trips_copy[["journey", "Arrival (Local)"]].groupby("journey").min()
    )
    journeys = journey_counts.join(journey_distances).join(journey_firstdate)
    journeys.rename(
        columns={"Distance (km)": "distance", "Arrival (Local)": "firstdate"},
        inplace=True,
    )
    return trips_copy, journeys


def km_to_mi(km):
    return km * 0.621371


def format_timedelta(dt):
    days = dt.days
    hours = divmod(dt.seconds, 3600)[0]
    minutes = divmod(dt.seconds, 3600)[1] // 60

    string = ""
    if days > 0:
        string += f"{days} day{'s' if days > 1 else ''}"
    if hours > 0:
        string += f" {hours} hour{'s' if hours > 1 else ''}"
    if minutes > 0:
        string += f" {minutes} minute{'s' if minutes > 1 else ''}"

    return string


def format_km(km):
    return f"{round(km):_} km ({round(km_to_mi(km)):_} mi)".replace("_", " ")


def compute_stats(trips, start=None, end=None, timezone=UTC_TZ):
    if not start:
        start = trips["Departure (Local)"].min()
    if not end:
        end = trips["Arrival (Local)"].max()
    trips_total_mask = (trips["Departure (Local)"] >= start) & (
        trips["Arrival (Local)"] <= end
    )
    trips_current_mask = (trips["Departure (Local)"] >= start) & (
        trips["Arrival (Local)"] < datetime.now(tz=timezone)
    )
    total_duration = trips[trips_total_mask]["Duration"].sum()
    total_distance = trips[trips_total_mask]["Distance (km)"].dropna().sum()
    current_duration = trips[trips_current_mask]["Duration"].dropna().sum()
    current_distance = trips[trips_current_mask]["Distance (km)"].dropna().sum()

    if end < datetime.now(tz=timezone) or start > datetime.now(tz=timezone):
        # Trip has ended or hasn't started
        distance_str = format_km(total_distance)
        duration_str = format_timedelta(total_duration)
    else:
        # Trip is ongoing
        distance_str = (
            format_km(current_distance) + " out of " + format_km(total_distance)
        )
        duration_str = (
            format_timedelta(current_duration)
            + " out of "
            + format_timedelta(total_duration)
        )

    return distance_str, duration_str


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
