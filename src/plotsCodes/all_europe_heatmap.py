from datetime import datetime

import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from cartopy.crs import Robinson, PlateCarree
from cartopy.io.img_tiles import MapboxStyleTiles

from utils import (
    dark_figure,
    finish_map,
    extract_points_from_journeys,
    compute_stats,
    PARIS_TZ,
)

# Setup map boundaries
LON_MIN = -21
LON_MAX = 29
LAT_MIN = 37
LAT_MAX = 66.5
ZOOM_LEVEL = 5


def plot_all_europe_heatmap(trips, mapbox_style_token, mapbox_style_id):
    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson())
    request = MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(request, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    now = datetime.now(tz=PARIS_TZ)
    color_map = matplotlib.colormaps["rainbow"]

    coordinates = extract_points_from_journeys(
        trips.loc[trips["Arrival (Local)"] <= now, "journey"].tolist()
    )
    coordinates_stats = (
        coordinates.groupby(["lon", "lat"]).size().reset_index(name="count")
    )
    coordinates_stats.sort_values(["count"], ascending=True, inplace=True)

    count_max = coordinates_stats["count"].max()
    colors = color_map((coordinates_stats["count"].to_numpy() - 1) / (count_max - 1))

    ax[0].scatter(
        coordinates_stats["lon"].to_numpy(),
        coordinates_stats["lat"].to_numpy(),
        s=1,
        marker=".",
        color=colors,
        transform=PlateCarree(),
    )

    # Logging
    print("Finalizing all Europe heatmap plot...")

    # Setup colorbar
    sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=count_max))
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Travel count", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    ax[0].set(
        title="European train travel heatmap since 2013",
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

    finish_map(fig, ax, "all_europe_heatmap", colorbar=cbar, show=False)
