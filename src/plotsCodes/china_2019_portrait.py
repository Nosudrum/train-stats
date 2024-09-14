import json
from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from cartopy.crs import PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles
from matplotlib.colors import LinearSegmentedColormap
from tqdm import tqdm
import pytz

from utils import dark_figure, finish_map, JOURNEYS_PATH, extract_trips_journeys, compute_stats

CHINA_TZ = pytz.timezone("Asia/Shanghai")

# Trip start/end dates
START = datetime(2019, 8, 3, 0, 0, 0, tzinfo=CHINA_TZ)
END = datetime(2019, 8, 10, 23, 59, 59, tzinfo=CHINA_TZ)

# Setup map boundaries
LON_MIN = 114.5
LON_MAX = 123.5
LAT_MIN = 28.5
LAT_MAX = 40.5
ZOOM_LEVEL = 6


def plot_china_2019_portrait(trips, mapbox_style_token, mapbox_style_id):
    # Compute trips and journeys dataframe
    trips, journeys = extract_trips_journeys(trips, filter_start=START, filter_end=END)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=PlateCarree(), figsize=(4, 7.1111))
    request = MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    now = datetime.now(tz=CHINA_TZ)
    trip_duration_days = (END - START).days + 1
    color_map = matplotlib.colormaps["rainbow"]

    trip_list = trips.index.to_list()
    for trip in tqdm(trip_list, ncols=150, desc="China 2019 (portrait)"):
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
            ax[0].plot(coords[:, 0], coords[:, 1], s, linewidth=1.7, color=c, transform=PlateCarree(),
                       zorder=(trip_duration_days - trip_day) + 2,
                       solid_capstyle="round",
                       dashes=dashes
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
    cax = ax[0].inset_axes([0.08, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax, boundaries=bounds,
                        ticks=np.linspace(0.5, trip_duration_days + 1.5, trip_duration_days))
    cbar.ax.set_xticklabels(np.arange(1, trip_duration_days + 1))
    cbar.ax.set_title("Trip day", color="white", fontsize=8)
    cbar.outline.set_edgecolor('white')
    plt.setp(plt.getp(cbar.ax, 'xticklabels'), color='white', fontsize=12)
    plt.tight_layout()

    # Stats
    distance_str, duration_str = compute_stats(trips, start=START, end=END, timezone=CHINA_TZ)
    fig_axes = fig.add_axes([0.95, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    index = duration_str.find(" out of")
    if index != -1:
        # Split the duration in two lines
        fig_axes.text(0, 0.08, duration_str[:index], ha="right", va="bottom", color="white", fontsize=9)
        fig_axes.text(0, 0, duration_str[index:], ha="right", va="bottom", color="white", fontsize=9)
        fig_axes.text(0, 0.19, distance_str, ha="right", va="bottom", color="white", fontsize=9)
    else:
        fig_axes.text(0, 0.03, duration_str, ha="right", va="bottom", color="white", fontsize=9)
        fig_axes.text(0, 0.16, distance_str, ha="right", va="bottom", color="white", fontsize=9)
    fig_axes.axis("off")

    finish_map(fig, ax, "2019_china_portrait", colorbar=cbar, show=False, logo_position=[0.05, 0.656, 0.4, 0.3])
