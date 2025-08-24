from datetime import timedelta

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

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
    bottom = np.zeros(len(years))

    operators = past_trips["Operator"].copy()
    all_operators = operators.unique().tolist()
    operators_spending = []
    for operator in all_operators:
        operators_spending.append(
            (past_trips.loc[operators == operator]["Price"]-past_trips.loc[operators == operator]["Reimb"]).sum()
        )

    operators_spending = np.array(operators_spending)
    operators_spending_df = pd.DataFrame(
        {"Operator": all_operators, "Spending": operators_spending}
    )

    operators_sorted = operators_spending_df.sort_values(
        by="Spending", ascending=False
    ).Operator.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    operators_selected.append("Others")

    for ii, operator in enumerate(operators_selected):
        #TODO: show trips partially refunded separately
        #TODO: split 1st and second class
        #TODO: use the cards and passes links somehow
        
        ax[0].scatter(
            past_trips.loc[operators==operator]["Distance (km)"].tolist(),
            past_trips.loc[operators==operator]["Price"].tolist(), 
            color=COLORS[ii],
            label=operator,
        )
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        xlabel="Distance (km)",
        ylabel="Cost (€)",
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