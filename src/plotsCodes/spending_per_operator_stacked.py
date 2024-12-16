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
import pandas as pd
import numpy as np


# Plot of km travelled by train operator
def plot_spending_per_operator_stacked(trips, additional_spending):
    past_trips, _ = extract_trips_journeys(trips, filter_end=datetime.now(tz=PARIS_TZ))

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
    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Spending (€)",
        xlim=[min(years), max(years) + 1],
        title="Money spent on train tickets & passes per operator since "
        + str(min(years)),
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
    finish_figure(fig, ax, "spending_per_operator_stacked", show=False)
