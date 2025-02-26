import json
from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from cartopy.crs import Robinson, PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles
from tqdm import tqdm

from processing import process_trips, process_additional_spending
from utils import (
    dark_figure,
    finish_map,
    JOURNEYS_PATH,
    compute_stats,
    PARIS_TZ,
    extract_trips_journeys,
)
from utils import get_mapbox_secrets

# Setup map boundaries
LON_MIN = -21
LON_MAX = 29
LAT_MIN = 37
LAT_MAX = 66.5
ZOOM_LEVEL = 5


def extract_segments_from_geojson(geojson):
    coords = np.array(geojson["features"][0]["geometry"]["coordinates"])
    segments_lon1 = []
    segments_lon2 = []
    segments_lat1 = []
    segments_lat2 = []
    for i in range(len(coords) - 2):
        if coords[i, 0] == coords[i + 1, 0] and coords[i, 1] == coords[i + 1, 1]:
            # Skip duplicate points
            continue
        if coords[i, 0] <= coords[i + 1, 0]:
            # Longitude is increasing, append in current order
            segments_lon1.append(coords[i, 0])
            segments_lon2.append(coords[i + 1, 0])
            segments_lat1.append(coords[i, 1])
            segments_lat2.append(coords[i + 1, 1])
        else:
            # Longitude is decreasing, append in reverse order
            segments_lon1.append(coords[i + 1, 0])
            segments_lon2.append(coords[i, 0])
            segments_lat1.append(coords[i + 1, 1])
            segments_lat2.append(coords[i, 1])
    return segments_lon1, segments_lon2, segments_lat1, segments_lat2


def extract_segments_from_journeys(journeys_list):
    all_segments_lon1 = []
    all_segments_lon2 = []
    all_segments_lat1 = []
    all_segments_lat2 = []

    for journey in journeys_list:
        with open(
            JOURNEYS_PATH + journey + ".geojson",
            "r",
            encoding="utf8",
        ) as f:
            geojson = json.load(f)
            segments_coords = extract_segments_from_geojson(geojson)
            all_segments_lon1 += segments_coords[0]
            all_segments_lon2 += segments_coords[1]
            all_segments_lat1 += segments_coords[2]
            all_segments_lat2 += segments_coords[3]

    return pd.DataFrame(
        {
            "lon1": all_segments_lon1,
            "lon2": all_segments_lon2,
            "lat1": all_segments_lat1,
            "lat2": all_segments_lat2,
        }
    )


def testing(trips_, mapbox_style_token, mapbox_style_id):
    # Compute journeys dataframe
    trips, journeys = extract_trips_journeys(trips_)

    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson())
    request = MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    now = datetime.now(tz=PARIS_TZ)
    color_map = matplotlib.colormaps["rainbow"]

    segments = extract_segments_from_journeys(trips_["journey"].tolist())
    segments_stats = (
        segments.groupby(["lon1", "lon2", "lat1", "lat2"])
        .size()
        .reset_index(name="count")
    )

    segments_stats_list = segments_stats.index.to_list()
    count_max = segments_stats["count"].max()
    for segment in tqdm(segments_stats_list, ncols=150, desc="All Europe"):
        # if journeys.loc[journey, "firstdate"] < now:
        #     s = "-"
        # else:
        #     s = ":"

        count = segments_stats.loc[segment, "count"]
        c = color_map((count - 1) / (count_max - 1))
        # ax[0].plot(
        #     [segments_stats.loc[segment, "lon1"], segments_stats.loc[segment, "lon2"]],
        #     [segments_stats.loc[segment, "lat1"], segments_stats.loc[segment, "lat2"]],
        #     "-",
        #     linewidth=1.2,
        #     color=c,
        #     transform=PlateCarree(),
        #     zorder=count,
        #     solid_capstyle="round",
        # )
        ax[0].scatter(
            segments_stats.loc[segment, "lon1"].item(),
            segments_stats.loc[segment, "lat1"].item(),
            s=1.2,
            marker=".",
            color=c,
            transform=PlateCarree(),
            zorder=count,
        )
        ax[0].scatter(
            segments_stats.loc[segment, "lon2"].item(),
            segments_stats.loc[segment, "lat2"].item(),
            s=1.2,
            marker=".",
            color=c,
            transform=PlateCarree(),
            zorder=count,
        )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=count_max))
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Journey counts", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    ax[0].set(
        title="All European train journeys since 2013",
    )
    plt.tight_layout()

    # Stats
    distance_str, duration_str = compute_stats(trips, end=now, timezone=PARIS_TZ)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(
        0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.text(
        0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.axis("off")

    finish_map(fig, ax, "test", colorbar=cbar, show=False)


if __name__ == "__main__":
    # Import Mapbox secrets
    MAPBOX_STYLE_TOKEN, MAPBOX_STYLE_ID = get_mapbox_secrets()

    # Import data
    trips_processed = process_trips()
    additional_spending = process_additional_spending()
    # Generate plots
    print("Generating plots...")

    testing(
        trips_processed,
        mapbox_style_id=MAPBOX_STYLE_ID,
        mapbox_style_token=MAPBOX_STYLE_TOKEN,
    )
