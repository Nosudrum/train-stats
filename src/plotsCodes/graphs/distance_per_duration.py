from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    GITHUB_DARK,
    COLORS,
    prepare_legend,
    DURATION_TIERS,
    finish_figure,
)
from utils.plotting import PlotParams


# Plot of km travelled by train journey duration
def plot_distance_per_duration(data: TrainStatsData, params: PlotParams):
    past_trips = data.get_past_trips()
    future_trips = data.get_future_trips(current_year_only=True)

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))
    for ii, tier in tqdm(enumerate(DURATION_TIERS), ncols=150, desc=params.title):
        min_duration = timedelta(hours=tier[0])
        max_duration = timedelta(hours=tier[1])
        distances = []
        tier_mask = past_trips["Duration"].between(
            min_duration, max_duration, inclusive="left"
        )
        for year in years:
            distances.append(
                past_trips.loc[
                    tier_mask & (past_trips["Departure (Local)"].dt.year == year),
                    "Distance (km)",
                ].sum()
            )
        distances = np.array(distances)
        ax[0].bar(
            years,
            distances,
            bottom=bottom,
            color=COLORS[ii],
            label=tier[2],
            width=1,
            align="edge",
        )
        bottom += distances
    ax[0].bar(
        future_trips["Departure (Local)"].dt.year.unique().tolist(),
        future_trips["Distance (km)"].sum(),
        bottom=bottom[-1],
        color=GITHUB_DARK,
        label=None,
        width=1,
        align="edge",
        hatch="///",
        linewidth=0,
        edgecolor="white",
    )
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Distance travelled (km)",
        xlim=[min(years), max(years) + 1],
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

    finish_figure(fig, ax, params.file_name)
