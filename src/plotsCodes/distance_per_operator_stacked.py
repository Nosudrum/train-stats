from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import (
    dark_figure,
    extract_trips_journeys,
    PARIS_TZ,
    GITHUB_DARK,
    COLORS,
    prepare_legend,
    finish_figure,
    compute_stats,
)


# Plot of km travelled by train operator
def plot_distance_per_operator_stacked(trips):
    past_trips, _ = extract_trips_journeys(trips, filter_end=datetime.now(tz=PARIS_TZ))
    future_trips, _ = extract_trips_journeys(
        trips,
        filter_start=datetime.now(tz=PARIS_TZ),
        filter_end=datetime(
            datetime.now(tz=PARIS_TZ).year + 1, 1, 1, 0, 0, 0, tzinfo=PARIS_TZ
        ),
    )

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))

    operators = past_trips["Operator"].copy()
    all_operators = operators.unique().tolist()
    operators_distance = []
    for operator in all_operators:
        operators_distance.append(
            past_trips.loc[operators == operator]["Distance (km)"].sum()
        )

    operators_distance = np.array(operators_distance)
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
