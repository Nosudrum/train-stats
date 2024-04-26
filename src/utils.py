from datetime import datetime
from math import prod
import os
import matplotlib.pyplot as plt
from PIL import Image
import pandas as pd
import pytz

GITHUB_BADGE = Image.open("../assets/GitHub.png")

GITHUB_DARK = "#0D1117"

MAPBOX_STYLE_TOKEN_PATH = "../data/mapbox_style_token.txt"
MAPBOX_STYLE_ID_PATH = "../data/mapbox_style_id.txt"
DATASHEET_ID_PATH = "../data/datasheet_id.txt"
JOURNEYS_PATH = "../data/journeys_coords/"
DATASET_PATH = "../data/dataset.csv"

PARIS_TZ = pytz.timezone("Europe/Paris")
UTC_TZ = pytz.utc


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


def extract_trips_journeys(trips, filter_start=None, filter_end=None):
    if filter_start is not None:
        trips = trips[trips["Departure (Local)"] >= filter_start]
    if filter_end is not None:
        trips = trips[trips["Arrival (Local)"] <= filter_end]
    journey_counts = trips["journey"].value_counts().to_frame()
    journey_distances = trips[["journey", "Distance (km)"]].groupby("journey").mean()
    journey_firstdate = trips[["journey", "Arrival (Local)"]].groupby("journey").min()
    journeys = journey_counts.join(journey_distances).join(journey_firstdate)
    journeys.rename(columns={"Distance (km)": "distance", "Arrival (Local)": "firstdate"}, inplace=True)
    return trips, journeys


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
    return f"{round(km):_} km ({round(km_to_mi(km)):_} mi)".replace('_', ' ')


def compute_stats(trips, start=None, end=None, timezone=UTC_TZ):
    if not start:
        start = trips["Departure (Local)"].min()
    if not end:
        end = trips["Arrival (Local)"].max()
    trips_total_mask = (trips["Departure (Local)"] >= start) & (trips["Arrival (Local)"] <= end)
    trips_current_mask = (trips["Departure (Local)"] >= start) & (trips["Arrival (Local)"] < datetime.now(tzinfo=timezone))
    total_duration = pd.to_timedelta(trips[trips_total_mask]["Duration"].dropna() + ":00").sum()
    total_distance = trips[trips_total_mask]["Distance (km)"].dropna().sum()
    current_duration = pd.to_timedelta(trips[trips_current_mask]["Duration"].dropna() + ":00").sum()
    current_distance = trips[trips_current_mask]["Distance (km)"].dropna().sum()

    if end < datetime.now(tzinfo=timezone) or start > datetime.now(tzinfo=timezone):
        # Trip has ended or hasn't started
        distance_str = format_km(total_distance)
        duration_str = format_timedelta(total_duration)
    else:
        # Trip is ongoing
        distance_str = format_km(current_distance) + " out of " + format_km(total_distance)
        duration_str = format_timedelta(current_duration) + " out of " + format_timedelta(total_duration)
    
    return distance_str, duration_str
