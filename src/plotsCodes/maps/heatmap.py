import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from cartopy.crs import PlateCarree

from utils import MapboxStyle, TrainStatsData, MapParams
from utils.plot_utils import (
    dark_figure,
    finish_map,
)


def plot_heatmap(data: TrainStatsData, mapbox_style: MapboxStyle, params: MapParams):
    print("Plotting heatmap...")

    # Setup figure
    fig, ax = dark_figure(
        grid=False, projection=params.map_projection, figsize=params.get_fig_size()
    )
    ax[0].set_extent(params.get_extent())
    ax[0].add_image(mapbox_style, params.zoom_level, regrid_shape=3000)

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

    # Setup colorbar
    sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=count_max))
    sm.set_array([])
    cax = ax[0].inset_axes(params.get_colorbar_axes())
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    cbar.ax.set_title("Travel count", color="white", fontsize=8)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    if not params.is_portrait:
        ax[0].set(
            title=params.title,
        )

    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(end=data.NOW)
    fig_axes = fig.add_axes(params.get_stats_axes(), anchor="SE", zorder=1)

    stats_texts = params.get_split_stats_texts(distance_str, duration_str)
    stats_positions = params.get_split_stats_positions(distance_str, duration_str)

    for text, position in zip(stats_texts, stats_positions):
        fig_axes.text(
            position[0],
            position[1],
            text,
            ha="right",
            va="bottom",
            color="white",
            fontsize=params.get_stats_font_size(),
        )

    fig_axes.axis("off")

    finish_map(
        fig,
        ax,
        params.file_name,
        colorbar=cbar,
        logo_position=params.get_logo_position(),
    )
