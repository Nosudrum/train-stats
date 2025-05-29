import matplotlib
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from cartopy.crs import PlateCarree
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from tqdm import tqdm

from utils import MapboxStyle, TrainStatsData, TripParams, MapParams
from utils.plot_utils import (
    dark_figure,
    finish_map,
    get_trip_labels,
)


def plot_trip_map(
    data: TrainStatsData, mapbox_style: MapboxStyle, trip: TripParams, params: MapParams
):
    # Compute trips and journeys dataframe
    trips = data.get_trips(filter_start=trip.start, filter_end=trip.end)

    # Setup figure
    fig, ax = dark_figure(
        grid=False, projection=params.map_projection, figsize=params.get_fig_size()
    )
    ax[0].set_extent(params.get_extent())
    ax[0].add_image(mapbox_style, params.zoom_level, regrid_shape=3000)

    # Setup colormap
    color_map = matplotlib.colormaps["rainbow"]
    color_map_list = np.array([color_map(i) for i in range(color_map.N)])
    custom_map = LinearSegmentedColormap.from_list(
        "Custom cmap", color_map_list.tolist(), trip.get_trip_duration_days()
    )

    bounds = np.linspace(
        0, trip.get_trip_duration_days(), trip.get_trip_duration_days() + 1
    )
    norm = BoundaryNorm(boundaries=bounds, ncolors=trip.get_trip_duration_days())

    sm = cm.ScalarMappable(cmap=custom_map, norm=norm)

    # For all journeys in the dataset
    trip_list = trips.index.to_list()
    for trip_item in tqdm(
        trip_list,
        ncols=150,
        desc=f"{params.title} (Portrait)" if params.is_portrait else params.title,
    ):
        # Get the departure datetime
        trip_departure = trips.loc[trip_item, "Departure (Local)"]
        # Compute the trip day number (1-indexed)
        trip_day = (trip_departure - trip.start).days + 1
        # Color corresponding to the trip day
        trip_ratio = (trip_day - 1) / (
            trip.get_trip_duration_days() - 1
        )  # value must be between 0 and 1
        c = sm.to_rgba(trip_day - 1)

        # Dashes or not
        if trips.loc[trip_item, "Arrival (Local)"] < data.NOW:
            s = "-"
            dashes = [1, 0]
        else:
            s = ":"
            dashes = [1, 1 + trip_ratio]

        # Plot the trip
        coordinates = data.get_journey_coordinates(trips.loc[trip_item, "journey"])
        ax[0].plot(
            coordinates[:, 0],
            coordinates[:, 1],
            s,
            linewidth=params.get_line_width(),
            color=c,
            transform=PlateCarree(),
            zorder=(trip.get_trip_duration_days() - trip_day) + 2,
            solid_capstyle="round",
            dashes=dashes,
        )

    # Logging
    print("Finalizing plot...")

    # Setup colorbar
    cax = ax[0].inset_axes(params.get_colorbar_axes())
    cbar_ticks = params.get_colorbar_ticks(trip.get_trip_duration_days())
    cbar = fig.colorbar(
        sm,
        orientation="horizontal",
        cax=cax,
        ticks=cbar_ticks,
    )
    cbar_title, cbar_ticks = get_trip_labels(trip.start, trip.end, len(cbar_ticks))
    cbar.ax.set_title(cbar_title, color="white", fontsize=8)
    cbar.ax.set_xticklabels(cbar_ticks)
    cbar.outline.set_edgecolor("white")
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    if not params.is_portrait:
        ax[0].set(
            title=params.title,
        )

    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(start=trip.start, end=trip.end)
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
