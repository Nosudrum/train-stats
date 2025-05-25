import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from cartopy.crs import Robinson, PlateCarree

from utils import MapboxStyle, TrainStatsData
from utils.plot_utils import (
    dark_figure,
    finish_map,
)

# Setup map boundaries
LON_MIN = -4
LON_MAX = 19.4
LAT_MIN = 36
LAT_MAX = 69
ZOOM_LEVEL = 5


def plot_all_europe_heatmap_portrait(data: TrainStatsData, mapbox_style: MapboxStyle):
    # Setup figure
    fig, ax = dark_figure(grid=False, projection=Robinson(), figsize=(4, 7.1111))
    extent = [LON_MIN, LON_MAX, LAT_MIN, LAT_MAX]
    ax[0].set_extent(extent)
    ax[0].add_image(mapbox_style, ZOOM_LEVEL, regrid_shape=3000)

    # For all journeys in the dataset
    color_map = matplotlib.colormaps["rainbow"]

    coordinates = data.get_travel_coordinates(filter_end=data.NOW)

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
    print("Finalizing all Europe heatmap plot (portrait)...")

    # Setup colorbar
    sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=count_max))
    sm.set_array([])
    cax = ax[0].inset_axes([0.08, 0.08, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Travel count", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)
    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(end=data.NOW)
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
        "all_europe_heatmap_portrait",
        colorbar=cbar,
        show=False,
        logo_position=[0.05, 0.656, 0.4, 0.3],
    )
