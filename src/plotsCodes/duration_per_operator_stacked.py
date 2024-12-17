from utils import (
    dark_figure,
    extract_trips_journeys,
    PARIS_TZ,
    COLORS,
    prepare_legend,
    compute_stats,
    finish_figure,
)
from datetime import datetime
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd


# Plot of km travelled by train operator
def plot_duration_per_operator_stacked(trips):
    past_trips, _ = extract_trips_journeys(trips, filter_end=datetime.now(tz=PARIS_TZ))

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))

    operators = past_trips["Operator"].copy()
    all_operators = operators.unique().tolist()
    operators_duration = []
    for operator in all_operators:
        operators_duration.append(
            past_trips.loc[operators == operator]["Duration"].sum().total_seconds()
        )

    operators_distance = np.array(operators_duration)
    operators_distance_df = pd.DataFrame(
        {"Operator": all_operators, "Distance": operators_distance}
    )

    operators_sorted = operators_distance_df.sort_values(
        by="Distance", ascending=False
    ).Operator.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    operators_selected.append("Others")

    for ii, operator in enumerate(operators_selected):
        durations = []
        for year in years:
            durations.append(
                past_trips.loc[
                    (operators == operator)
                    & (past_trips["Departure (Local)"].dt.year == year),
                    "Duration",
                ]
                .sum()
                .total_seconds()
                / 3600
                / 24
            )
        durations = np.array(durations)
        ax[0].bar(
            years,
            durations,
            bottom=bottom,
            color=COLORS[ii],
            label=operator,
            width=1,
            align="edge",
        )
        bottom += durations
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Time spent in trains (days)",
        xlim=[min(years), max(years) + 1],
        title="Time spent in trains per operator since " + str(min(years)),
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
    # plt.savefig(
    #     "../plots/" + "duration_per_operator_stacked" + ".png",
    #     transparent=False,
    #     dpi=500,
    # )
    finish_figure(fig, ax, "duration_per_operator_stacked", show=False)
