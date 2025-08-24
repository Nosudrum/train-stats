from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    COLORS,
    prepare_legend,
    DURATION_TIERS,
    finish_figure,
    GITHUB_DARK,
)
from utils.plotting import PlotParams


# Plot of km travelled by train journey duration
def plot_cost_per_distance(data: TrainStatsData, params: PlotParams):
    past_trips = data.get_past_trips()
    future_trips = data.get_future_trips(current_year_only=True)

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    plot_data = []
    for tier in DURATION_TIERS:
        min_duration = timedelta(hours=tier[0])
        max_duration = timedelta(hours=tier[1])
        plot_data.append(
            past_trips[
                past_trips["Duration"].between(
                    min_duration, max_duration, inclusive="left"
                )
            ]["Departure (Local)"].dt.year.values.tolist()
        )
    future_trips_mask = future_trips["Departure (Local)"].dt.year.isin(years)
    plot_data.append(
        future_trips[future_trips_mask]["Departure (Local)"].dt.year.values.tolist()
    )
    _, _, bar_containers = ax[0].hist(
        plot_data,
        bins=np.append(np.unique(years), max(years) + 1),
        histtype="bar",
        stacked=True,
        label=[tier[2] for tier in DURATION_TIERS],
        color=COLORS + [GITHUB_DARK],
    )
    if future_trips_mask.sum() > 0:
        for p in bar_containers[-1].patches:
            p.set_label(None)
            p.set_hatch("///")
            p.set_linewidth(0)
            p.set_edgecolor("white")
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Total trains taken",
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
