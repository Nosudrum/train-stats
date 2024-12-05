from utils import (
    dark_figure,
    extract_trips_journeys,
    PARIS_TZ,
    COLORS,
    prepare_legend,
    finish_figure,
    compute_stats,
)
from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np


# Plot of km travelled by train operator
def plot_distance_per_operator_stacked(trips):
    past_trips, _ = extract_trips_journeys(trips, filter_end=datetime.now(tz=PARIS_TZ))

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))

    operators = past_trips["Operator"].copy()
    operators_sorted = operators.value_counts().index.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    operators_selected.append("Others")

    for ii, operator in enumerate(operators_selected):
        distances = []
        for year in years:
            distances.append(
                past_trips.loc[
                    (operators == operator)
                    & (past_trips["Departure (Local)"].dt.year == year),
                    "Distance (km)",
                ].sum()
            )
        distances = np.array(distances)
        ax[0].bar(
            years,
            distances,
            bottom=bottom,
            color=COLORS[ii],
            label=operator,
            width=1,
            align="edge",
        )
        bottom += distances
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Distance travelled (km)",
        xlim=[min(years), max(years) + 1],
        title="Distance travelled by train per operator since " + str(min(years)),
    )
    plt.tight_layout()

    # Stats
    distance_str, duration_str = compute_stats(past_trips, timezone=PARIS_TZ)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(
        0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.text(
        0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10
    )
    fig_axes.axis("off")
    finish_figure(fig, ax, "distance_per_operator_stacked", show=False)
