import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    finish_figure,
)

MAX_DAYS_PER_YEAR = 366

MONTHS_TICKS = [1, 32, 61, 92, 122, 153, 183, 214, 245, 275, 306, 336]

MONTHS_LABELS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def plot_distance_per_day(data: TrainStatsData):
    past_trips = data.get_past_trips()

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    distance_matrix = np.empty((len(years) + 2, MAX_DAYS_PER_YEAR))
    distance_matrix[:2, :] = np.nan

    for ii, year in enumerate(years):
        for day in range(1, MAX_DAYS_PER_YEAR + 1):
            mask_past = (past_trips["Departure (Local)"].dt.year == year) & (
                past_trips["Day of year"] == day
            )
            distance_day = past_trips.loc[mask_past, "Distance (km)"].sum()
            distance_matrix[ii + 2, day - 1] = (
                distance_day if distance_day > 0 else np.nan
            )

    color_map = cm.get_cmap("viridis")
    color_map.set_bad("k", alpha=0)

    ax[0].matshow(
        distance_matrix,
        cmap=color_map,
        aspect="auto",
        extent=[0, MAX_DAYS_PER_YEAR, len(years) + 2, 0],
    )
    ax[0].xaxis.set_ticks_position("bottom")
    ax[0].set(
        title="Distance (km) travelled by train per day since " + str(min(years)),
        xticks=np.array(MONTHS_TICKS) - 1,
        xticklabels=MONTHS_LABELS,
        ylabel="Year",
        yticks=np.arange(2, len(years) + 2, 2) + 0.5,
        yticklabels=years[::2],
    )

    # Setup colorbar
    sm = cm.ScalarMappable(
        cmap=color_map, norm=plt.Normalize(vmin=0, vmax=np.nanmax(distance_matrix))
    )
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.935, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

    plt.tight_layout()

    # Stats
    distance_str, duration_str = data.get_stats(end=data.NOW)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(
        0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.text(
        0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.axis("off")
    finish_figure(
        fig,
        ax,
        "distance_per_day",
        show=False,
        override_ylim=False,
        override_yticks=False,
        colorbar=cbar,
    )
