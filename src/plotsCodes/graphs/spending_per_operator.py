import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    COLORS,
    GITHUB_DARK,
    prepare_legend,
    finish_figure,
)
from utils.plotting import PlotParams


# Plot of km travelled by train operator
def plot_spending_per_operator(data: TrainStatsData, params: PlotParams):
    past_trips = data.get_past_trips()
    future_trips = data.get_future_trips(current_year_only=True)
    additional_spending = data.get_additional_spending()

    fig, ax = dark_figure()
    years = past_trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))

    operators = past_trips["Operator"].copy()
    additional_spending_operators = additional_spending["Operator"].copy()

    all_operators = list(set(operators).union(additional_spending_operators))
    all_operators_spending = []
    for operator in all_operators:
        all_operators_spending.append(
            additional_spending.loc[additional_spending_operators == operator][
                "Amount"
            ].sum()
            + past_trips.loc[operators == operator]["Price"].sum()
            - past_trips.loc[operators == operator]["Reimb"].sum()
        )

    all_operators_spending = np.array(all_operators_spending)
    all_operators_spending_df = pd.DataFrame(
        {"Operator": all_operators, "Amount": all_operators_spending}
    )

    operators_sorted = all_operators_spending_df.sort_values(
        by="Amount", ascending=False
    ).Operator.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    additional_spending_operators.loc[
        ~additional_spending_operators.isin(operators_selected)
    ] = "Others"
    operators_selected.append("Others")

    for ii, operator in enumerate(operators_selected):
        amounts = []
        for year in years:
            amounts.append(
                past_trips.loc[
                    (operators == operator)
                    & (past_trips["Departure (Local)"].dt.year == year),
                    "Price",
                ].sum()
                - past_trips.loc[
                    (operators == operator)
                    & (past_trips["Departure (Local)"].dt.year == year),
                    "Reimb",
                ].sum()
                + additional_spending.loc[
                    (additional_spending_operators == operator)
                    & (additional_spending["Year"] == year),
                    "Amount",
                ].sum()
            )
        amounts = np.array(amounts)
        ax[0].bar(
            years,
            amounts,
            bottom=bottom,
            color=COLORS[ii],
            label=operator,
            width=1,
            align="edge",
        )
        bottom += amounts
    ax[0].bar(
        future_trips["Departure (Local)"].dt.year.unique().tolist(),
        future_trips["Price"].sum() - future_trips["Reimb"].sum(),
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
        ylabel="Spending (€)",
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
