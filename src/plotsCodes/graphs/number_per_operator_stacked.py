import matplotlib.pyplot as plt
import numpy as np

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    COLORS,
    prepare_legend,
    GITHUB_DARK,
    finish_figure,
)


# Plot of km travelled by train operator
def plot_number_per_operator_stacked(data: TrainStatsData):
    past_trips = data.get_past_trips()
    future_trips = data.get_future_trips(current_year_only=True)

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()

    operators = past_trips["Operator"].copy()
    operators_sorted = operators.value_counts().index.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    operators_selected.append("Others")
    plot_data = []
    for operator in operators_selected:
        plot_data.append(
            past_trips[operators == operator][
                "Departure (Local)"
            ].dt.year.values.tolist()
        )
    future_trips_mask = future_trips["Departure (Local)"].dt.year.isin(years)
    plot_data.append(
        future_trips[future_trips_mask]["Departure (Local)"].dt.year.values.tolist()
    )
    _, _, bar_containers = ax[0].hist(
        plot_data,
        bins=np.append(years, max(years) + 1),
        histtype="bar",
        stacked=True,
        label=operators_selected,
        color=COLORS + [GITHUB_DARK],
    )
    if future_trips_mask.sum() > 0:
        for p in bar_containers[-1].patches:
            p.set_label(None)
            p.set_hatch("///")
            p.set_linewidth(0)
            p.set_edgecolor("white")
    handles, labels = prepare_legend(reverse=False)

    ax[0].set(
        ylabel="Number of trains",
        xlim=[min(years), max(years) + 1],
        title="Number of trains taken per operator since " + str(min(years)),
    )
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
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
    finish_figure(fig, ax, "number_per_operator_stacked", show=False)
