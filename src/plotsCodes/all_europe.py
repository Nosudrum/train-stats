import json
import os

import matplotlib
import matplotlib.cm as cm
import numpy as np
from cartopy.crs import Robinson, PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles
from tqdm import tqdm
from datetime import datetime
import pandas as pd

from src.utils import dark_figure, finish_map, get_mapbox_secrets, JOURNEYS_PATH
import matplotlib.pyplot as plt

# Import Mapbox secrets
MAPBOX_STYLE_TOKEN, MAPBOX_STYLE_ID = get_mapbox_secrets()

# Setup map boundaries
LON_MIN = -21
LON_MAX = 29
LAT_MIN = 37
LAT_MAX = 66.5


def plot_all_europe(trips, journeys):
    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson())
    request = MapboxStyleTiles(MAPBOX_STYLE_TOKEN, "nosu", MAPBOX_STYLE_ID, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, 5, regrid_shape=3000)
    
    # Compute total_time and total_distance
    total_time = pd.to_timedelta(trips[trips["Arrival (Local)"] < datetime.now()]["Duration"].dropna()+":00").sum()
    total_distance = trips[trips["Arrival (Local)"] < datetime.now()]["Distance (km)"].dropna().sum()

    # For all journeys in the dataset
    now = datetime.now()
    values = journeys["count"].values
    color_map = matplotlib.colormaps["viridis"]

    journeys_list = os.listdir(JOURNEYS_PATH)
    pbar = tqdm(journeys_list, ncols=150)

    for journey in pbar:
        pbar.set_description("Plotting " + journey)
        journey_name = journey.replace(".geojson", "")
        if journeys.loc[journey_name, "firstdate"] < now:
            s = "-"
        else:
            s = ":"

        count = journeys.loc[journey_name, "count"]
        c = color_map(count / (values.max()))

        with open('../data/journeys_coords/' + journey, 'r', encoding="utf8") as f:
            geojson = json.load(f)
            coords = np.array(geojson['features'][0]['geometry']['coordinates'])
            ax[0].plot(coords[:, 0], coords[:, 1], s, linewidth=1.2, color=c, transform=PlateCarree(), zorder=count,
                       solid_capstyle="round")

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=values.max()))
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Journey counts", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, 'xticklabels'), color='white', fontsize=12)

    ax[0].set(
        title="All European train journeys since 2013",
    )
    plt.tight_layout()
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(0, 0.12, f"{round(total_distance):_} km ({round(total_distance / 1.609344):_} mi)".replace('_', ' '),
                  ha="right", va="bottom", color="white", fontsize=10)
    fig_axes.text(0, 0,
                  f"> {total_time.days} days {divmod(total_time.seconds, 3600)[0]} hours {divmod(total_time.seconds, 3600)[1] // 60} minutes",
                  ha="right", va="bottom", color="white", fontsize=10)

    fig_axes.axis("off")

    finish_map(fig, ax, "all_europe", colorbar=cbar, show=False)
