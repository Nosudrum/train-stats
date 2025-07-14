from datetime import timedelta

import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    finish_figure,
    MONTHS_TICKS,
    MAX_DAYS_PER_YEAR,
    MONTHS_LABELS,
)
from utils.plotting import PlotParams


def plot_duration_timeline(data: TrainStatsData, params: PlotParams):
    past_trips = data.get_past_trips()

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    duration_matrix = np.empty((len(years) + 2, MAX_DAYS_PER_YEAR))
    duration_matrix[:2, :] = np.nan

    for ii, year in enumerate(years):
        for day in range(1, MAX_DAYS_PER_YEAR + 1):
            mask_past = (past_trips["Departure (Local)"].dt.year == year) & (
                past_trips["Day of year"] == day
            )
            duration_day = past_trips.loc[mask_past, "Duration"].sum()
            duration_matrix[ii + 2, day - 1] = (
                duration_day.total_seconds() / 3600
                if duration_day > timedelta(0)
                else np.nan
            )

    color_map = cm.get_cmap("viridis")
    color_map.set_bad("k", alpha=0)

    ax[0].matshow(
        duration_matrix,
        cmap=color_map,
        aspect="auto",
        extent=[0, MAX_DAYS_PER_YEAR, len(years) + 2, 0],
    )
    ax[0].xaxis.set_ticks_position("bottom")
    ax[0].set(
        title=params.title,
        xticks=np.array(MONTHS_TICKS) - 1,
        xticklabels=MONTHS_LABELS,
        ylabel="Year",
        yticks=np.arange(2, len(years) + 2, 2) + 0.5,
        yticklabels=years[::2],
    )

    # Setup colorbar
    sm = cm.ScalarMappable(
        cmap=color_map, norm=plt.Normalize(vmin=0, vmax=np.nanmax(duration_matrix))
    )
    sm.set_array([])
    cax = ax[0].inset_axes([0.1, 0.935, 0.8, 0.035])
    cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
    plt.setp(plt.getp(cbar.ax, "xticklabels"), color="white", fontsize=12)

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
    finish_figure(
        fig,
        ax,
        params.file_name,
        override_ylim=False,
        override_yticks=False,
        colorbar=cbar,
    )
