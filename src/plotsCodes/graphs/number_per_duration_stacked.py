from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    COLORS,
    prepare_legend,
    finish_figure,
    GITHUB_DARK,
)

# Setup train duration tiers
TIERS = [
    (0, 2, "up to 2h"),
    (2, 4, "2h to 4h"),
    (4, 6, "4h to 6h"),
    (6, 8, "6h to 8h"),
    (8, 10, "8h to 10h"),
    (10, 12, "10h to 12h"),
    (12, 14, "12h to 14h"),
    (14, 999, "over 14h"),
]


# Plot of km travelled by train journey duration
def plot_number_per_duration_stacked(data: TrainStatsData):
    past_trips = data.get_past_trips()
    future_trips = data.get_future_trips(current_year_only=True)

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    plot_data = []
    for tier in TIERS:
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
        label=[tier[2] for tier in TIERS],
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
        title="Train trips per duration since " + str(min(years)),
    )
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
    finish_figure(fig, ax, "number_per_duration_stacked", show=False)
