import json
from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from cartopy.crs import Robinson, PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles
from tqdm import tqdm

from utils import (
    dark_figure,
    finish_map,
    JOURNEYS_PATH,
    extract_trips_journeys,
    compute_stats,
    PARIS_TZ,
)

# Setup map boundaries
LON_MIN = -4
LON_MAX = 19.4
LAT_MIN = 36
LAT_MAX = 69
ZOOM_LEVEL = 5


def plot_all_europe_portrait(trips, mapbox_style_token, mapbox_style_id):
    # Compute journeys dataframe
    trips, journeys = extract_trips_journeys(trips)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson(), figsize=(4, 7.1111))
    request = MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    now = datetime.now(tz=PARIS_TZ)
    values = journeys["count"].values
    color_map = matplotlib.colormaps["rainbow"]

    journeys_list = journeys.index.to_list()
    for journey in tqdm(journeys_list, ncols=150, desc="All Europe (portrait)"):
        if journeys.loc[journey, "firstdate"] < now:
            s = "-"
        else:
            s = ":"

        count = journeys.loc[journey, "count"]
        c = color_map((count - 1) / (values.max() - 1))

        with open(JOURNEYS_PATH + journey + ".geojson", "r", encoding="utf8") as f:
            geojson = json.load(f)
            coords = np.array(geojson["features"][0]["geometry"]["coordinates"])
            ax[0].plot(
                coords[:, 0],
                coords[:, 1],
                s,
                linewidth=1.2,
                color=c,
                transform=PlateCarree(),
                zorder=count,
                solid_capstyle="round",
            )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    sm = cm.ScalarMappable(
        cmap=color_map, norm=plt.Normalize(vmin=0, vmax=values.max())
    )
    sm.set_array([])
    cax = ax[0].inset_axes([0.08, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Journey counts", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)
    plt.tight_layout()

    # Stats
    distance_str, duration_str = compute_stats(trips, end=now, timezone=PARIS_TZ)
    fig_axes = fig.add_axes([0.95, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(
        0, 0.03, distance_str, ha="right", va="bottom", color="white", fontsize=9
    )
    fig_axes.text(
        0, 0.16, duration_str, ha="right", va="bottom", color="white", fontsize=9
    )
    fig_axes.axis("off")

    finish_map(
        fig,
        ax,
        "all_europe_portrait",
        colorbar=cbar,
        show=False,
        logo_position=[0.05, 0.656, 0.4, 0.3],
    )
