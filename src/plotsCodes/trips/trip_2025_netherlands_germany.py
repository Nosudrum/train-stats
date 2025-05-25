from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from cartopy.crs import Robinson, PlateCarree
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from tqdm import tqdm

from utils import MapboxStyle, TrainStatsData
from utils.plot_utils import (
    dark_figure,
    finish_map,
    PARIS_TZ,
    get_trip_labels,
)

# Trip start/end dates
START = datetime(2025, 6, 10, 0, 0, 0, tzinfo=PARIS_TZ)
END = datetime(2025, 6, 21, 23, 59, 59, tzinfo=PARIS_TZ)


def plot_netherlands_germany_2025(data: TrainStatsData, mapbox_style: MapboxStyle):
    # Setup map boundaries
    lon_min = -9
    lon_max = 14
    lat_min = 40.5
    lat_max = 54
    zoom_level = 6

    # Compute trips and journeys dataframe
    trips = data.get_trips(filter_start=START, filter_end=END)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson())
    extent = [lon_min, lon_max, lat_min, lat_max]
    ax[0].set_extent(extent)
    ax[0].add_image(mapbox_style, zoom_level, regrid_shape=3000)

    # Setup colormap
    trip_duration_days = (END - START).days + 1
    color_map = matplotlib.colormaps["rainbow"]
    color_map_list = np.array([color_map(i) for i in range(color_map.N)])
    custom_map = LinearSegmentedColormap.from_list(
        "Custom cmap", color_map_list.tolist(), trip_duration_days
    )

    bounds = np.linspace(0, trip_duration_days, trip_duration_days + 1)
    norm = BoundaryNorm(boundaries=bounds, ncolors=trip_duration_days)

    sm = cm.ScalarMappable(cmap=custom_map, norm=norm)

    # For all journeys in the dataset
    trip_list = trips.index.to_list()
    for trip in tqdm(trip_list, ncols=150, desc="Netherlands Germany 2025"):
        # Get the departure datetime
        trip_departure = trips.loc[trip, "Departure (Local)"]
        # Compute the trip day number (1-indexed)
        trip_day = (trip_departure - START).days + 1
        # Color corresponding to the trip day
        trip_ratio = (trip_day - 1) / (
            trip_duration_days - 1
        )  # value must be between 0 and 1
        c = sm.to_rgba(trip_day - 1)

        # Dashes or not
        if trips.loc[trip, "Arrival (Local)"] < data.NOW:
            s = "-"
            dashes = [1, 0]
        else:
            s = ":"
            dashes = [1, 1 + trip_ratio]

        # Plot the trip
        coordinates = data.get_journey_coordinates(trips.loc[trip, "journey"])
        ax[0].plot(
            coordinates[:, 0],
            coordinates[:, 1],
            s,
            linewidth=1.2,
            color=c,
            transform=PlateCarree(),
            zorder=(trip_duration_days - trip_day) + 2,
            solid_capstyle="round",
            dashes=dashes,
        )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(
        sm,
        orientation="horizontal",
        cax=cax,
        ticks=np.arange(0.5, trip_duration_days + 0.5),
    )
    cbar_title, cbar_ticks = get_trip_labels(START, END)
    cbar.ax.set_title(cbar_title, color="white", fontsize=8)
    cbar.ax.set_xticklabels(cbar_ticks)
    cbar.outline.set_edgecolor("white")
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    ax[0].set(
        title="2025 Netherlands & Germany Interrail Trip",
    )
    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(start=START, end=END)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(
        0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.text(
        0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.axis("off")

    finish_map(fig, ax, "2025_netherlands_germany", colorbar=cbar, show=False)


def plot_nl_de_2025_portrait(data: TrainStatsData, mapbox_style: MapboxStyle):
    # Setup map boundaries
    lon_min = -2.5
    lon_max = 9.5
    lat_min = 40
    lat_max = 54
    zoom_level = 6

    # Compute trips and journeys dataframe
    trips = data.get_trips(filter_start=START, filter_end=END)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson(), figsize=(4, 7.1111))
    extent = [lon_min, lon_max, lat_min, lat_max]
    ax[0].set_extent(extent)
    ax[0].add_image(mapbox_style, zoom_level, regrid_shape=3000)

    # Setup colormap
    trip_duration_days = (END - START).days + 1
    color_map = matplotlib.colormaps["rainbow"]
    color_map_list = np.array([color_map(i) for i in range(color_map.N)])
    custom_map = LinearSegmentedColormap.from_list(
        "Custom cmap", color_map_list.tolist(), trip_duration_days
    )

    bounds = np.linspace(0, trip_duration_days, trip_duration_days + 1)
    norm = BoundaryNorm(boundaries=bounds, ncolors=trip_duration_days)

    sm = cm.ScalarMappable(cmap=custom_map, norm=norm)

    # For all journeys in the dataset
    trip_list = trips.index.to_list()
    for trip in tqdm(trip_list, ncols=150, desc="Netherlands Germany 2025 (portrait)"):
        # Get the departure datetime
        trip_departure = trips.loc[trip, "Departure (Local)"]
        # Compute the trip day number (1-indexed)
        trip_day = (trip_departure - START).days + 1
        # Color corresponding to the trip day
        trip_ratio = (trip_day - 1) / (
            trip_duration_days - 1
        )  # value must be between 0 and 1
        c = sm.to_rgba(trip_day - 1)

        # Dashes or not
        if trips.loc[trip, "Arrival (Local)"] < data.NOW:
            s = "-"
            dashes = [1, 0]
        else:
            s = ":"
            dashes = [1, 1 + trip_ratio]

            # Plot the trip
        coordinates = data.get_journey_coordinates(trips.loc[trip, "journey"])
        ax[0].plot(
            coordinates[:, 0],
            coordinates[:, 1],
            s,
            linewidth=1.7,
            color=c,
            transform=PlateCarree(),
            zorder=(trip_duration_days - trip_day) + 2,
            solid_capstyle="round",
            dashes=dashes,
        )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    cax = ax[0].inset_axes([0.08, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(
        sm,
        orientation="horizontal",
        cax=cax,
        ticks=np.linspace(0, trip_duration_days - 1, 5) + 0.5,
    )
    cbar_title, cbar_ticks = get_trip_labels(START, END, 5)
    cbar.ax.set_title(cbar_title, color="white", fontsize=8)
    cbar.ax.set_xticklabels(cbar_ticks)
    cbar.outline.set_edgecolor("white")
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)
    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(start=START, end=END)
    fig_axes = fig.add_axes([0.95, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    index = duration_str.find(" out of")
    if index != -1:
        # Split the duration in two lines
        fig_axes.text(
            0,
            0.08,
            duration_str[:index],
            ha="right",
            va="bottom",
            color="white",
            fontsize=9,
        )
        fig_axes.text(
            0,
            0,
            duration_str[index:],
            ha="right",
            va="bottom",
            color="white",
            fontsize=9,
        )
        fig_axes.text(
            0, 0.19, distance_str, ha="right", va="bottom", color="white", fontsize=9
        )
    else:
        fig_axes.text(
            0, 0.03, duration_str, ha="right", va="bottom", color="white", fontsize=9
        )
        fig_axes.text(
            0, 0.16, distance_str, ha="right", va="bottom", color="white", fontsize=9
        )
    fig_axes.axis("off")

    finish_map(
        fig,
        ax,
        "2025_netherlands_germany_portrait",
        colorbar=cbar,
        show=False,
        logo_position=[0.05, 0.656, 0.4, 0.3],
    )
