import json
from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from cartopy.crs import Robinson, PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm

from utils import dark_figure, finish_map, JOURNEYS_PATH, extract_trips_journeys, compute_stats, PARIS_TZ

# Trip start/end dates
START = datetime(2024, 10, 12, 0, 0, 0, tzinfo=PARIS_TZ)
END = datetime(2024, 10, 20, 23, 59, 59, tzinfo=PARIS_TZ)

# Setup map boundaries
LON_MIN = 1
LON_MAX = 10
LAT_MIN = 42
LAT_MAX = 48
ZOOM_LEVEL = 7


def plot_milano_iac_2024(trips, mapbox_style_token, mapbox_style_id):
    # Compute journeys dataframe
    trips, journeys = extract_trips_journeys(trips, filter_start=START, filter_end=END)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson())
    request = MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    now = datetime.now(tz=PARIS_TZ)
    trip_duration_days = (END - START).days + 1
    color_map = matplotlib.colormaps["rainbow"]

    trip_list = trips.index.to_list()
    for trip in tqdm(trip_list, ncols=150, desc="Milano IAC 2024"):
        # Get the departure datetime
        trip_departure = trips.loc[trip, "Departure (Local)"]
        # Compute the trip day number
        trip_day = (trip_departure.date() - START.date()).days + 1
        # Color corresponding to the trip day
        trip_ratio = (trip_day - 1) / (trip_duration_days - 1)  # value must be between 0 and 1
        c = color_map(trip_ratio)

        # Dashes or not
        if trips.loc[trip, "Arrival (Local)"] < now:
            s = "-"
            dashes = [1, 0]
        else:
            s = ":"
            dashes = [1, 1 + trip_ratio]

        # Plot the trip
        with open(JOURNEYS_PATH + trips.loc[trip, "journey"] + ".geojson", 'r', encoding="utf8") as f:
            geojson = json.load(f)
            coords = np.array(geojson['features'][0]['geometry']['coordinates'])
            ax[0].plot(coords[:, 0], coords[:, 1], s, linewidth=1.2, color=c, transform=PlateCarree(),
                       zorder=(trip_duration_days - trip_day) + 1,
                       solid_capstyle="round",
                       dashes=dashes,
                       )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    color_map_list = np.array([color_map(i) for i in range(color_map.N)])
    custom_map = LinearSegmentedColormap.from_list(
        'Custom cmap', color_map_list.tolist(), color_map.N)
    bounds = np.linspace(0, trip_duration_days + 2, trip_duration_days + 1)
    sm = cm.ScalarMappable(cmap=custom_map, norm=plt.Normalize(vmin=0, vmax=trip_duration_days + 1))
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax, boundaries=bounds,
                        ticks=np.linspace(0.5, trip_duration_days + 1.5, trip_duration_days))
    cbar.ax.set_xticklabels(np.arange(1, trip_duration_days + 1))
    cbar.ax.set_title("Trip day", color="white", fontsize=8)
    cbar.outline.set_edgecolor('white')
    plt.setp(plt.getp(cbar.ax, 'xticklabels'), color='white', fontsize=12)

    ax[0].set(
        title="Milano IAC 2024 Interrail Trip",
    )
    plt.tight_layout()

    # Stats
    distance_str, duration_str = compute_stats(trips, start=START, end=END, timezone=PARIS_TZ)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10)
    fig_axes.text(0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10)
    fig_axes.axis("off")

    finish_map(fig, ax, "2024_milano_iac", colorbar=cbar, show=False)