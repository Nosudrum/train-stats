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
    additional_spending = data.get_additional_spending()

    past_trips = past_trips[past_trips['Price'] != 0]  # Remove rows where Price is zero
    past_trips = past_trips.reset_index(drop=True)

    while past_trips["Price"].isna().any():
        # Find the index of the first row with null in 'Price'
        null_index = past_trips[past_trips['Price'].isna()].index[0]

        # Raise an exception if the first row has a null 'Price'
        if null_index == 0:
            raise ValueError("The first row of the dataset needs a non-null 'Price' value.")

        # Keep the operator value with the biggest distance
        if past_trips.loc[null_index, "Distance (km)"] > past_trips.loc[null_index - 1,"Distance (km)"]:
                past_trips.loc[null_index - 1, "Operator"] = past_trips.loc[null_index, "Operator"]


        # Add the 'Distance (km)' value to the previous row
        past_trips.loc[null_index - 1, "Distance (km)"] += past_trips.loc[null_index, "Distance (km)"]

        # Drop the row with null 'Price'
        past_trips = past_trips.drop(index=null_index).reset_index(drop=True)

    operators = past_trips["Operator"].copy()
    all_operators = operators.unique().tolist()
    operators_spending = []
    for operator in all_operators:
        operators_spending.append(
            past_trips.loc[operators == operator]["Price"].sum()
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

    # Class filters
    first_class = past_trips["Class"] == 1
    second_class = past_trips["Class"] == 2

    # Partial refund
    rf = past_trips["Reimb"] > 0

    # Interrail
    interrail_card_IDs = additional_spending.loc[additional_spending["Operator"]=="Eurail"]["ID"].unique().tolist()
    ir = past_trips["Card"].isin(interrail_card_IDs)

    # No card
    nc = past_trips["Card"].isna()

    fig, ax = dark_figure()
    for ii, operator in enumerate(operators_selected):
        op = operators==operator

        ax[0].scatter(
            [],
            [],
            color=COLORS[ii],
            label=operator,
            marker="o",
            s=20,
        )
        
        ax[0].scatter(
            past_trips.loc[(op) & first_class]["Distance (km)"].tolist(),
            past_trips.loc[(op) & first_class]["Price"].tolist(), 
            color=COLORS[ii],
            marker="*",
            s=15,
            linewidth=0,
        )

        ax[0].scatter(
            past_trips.loc[(op) & second_class]["Distance (km)"].tolist(),
            past_trips.loc[(op) & second_class]["Price"].tolist(), 
            color=COLORS[ii],
            marker=".",
            s=15,
            linewidth=0,
        )

        ax[0].scatter(
            past_trips.loc[(op) & rf]["Distance (km)"].tolist(),
            past_trips.loc[(op) & rf]["Price"].tolist(), 
            facecolor=(0,0,0,0),
            edgecolors=COLORS[ii],
            marker="o",
            s=20,
            linewidth=0.5,
        )

        ax[0].scatter(
            past_trips.loc[(op) & ir]["Distance (km)"].tolist(),
            past_trips.loc[(op) & ir]["Price"].tolist(), 
            facecolor=(0,0,0,0),
            edgecolors=COLORS[ii],
            marker="D",
            s=20,
            linewidth=0.5,
        )

        ax[0].scatter(
            past_trips.loc[(op) & nc]["Distance (km)"].tolist(),
            past_trips.loc[(op) & nc]["Price"].tolist(), 
            facecolor=(0,0,0,0),
            edgecolors=COLORS[ii],
            marker="s",
            s=20,
            linewidth=0.5,
        )
    

    ax[0].scatter(
        [],
        [],
        marker="*",
        label="1st class",
        facecolor="white",
        s=20,
        linewidth=0,
    )
    ax[0].scatter(
        [],
        [],
        marker="o",
        label="Partial refund",
        facecolor=(0,0,0,0),
        edgecolors="white",
        s=20,
        linewidth=0.5,
    )
    ax[0].scatter(
        [],
        [],
        marker="D",
        label="Interrail",
        facecolor=(0,0,0,0),
        edgecolors="white",
        s=20,
        linewidth=0.5,
    )
    ax[0].scatter(
        [],
        [],
        marker="s",
        label="No card",
        facecolor=(0,0,0,0),
        edgecolors="white",
        s=20,
        linewidth=0.5,
    )

    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        xlim=[0, past_trips["Distance (km)"].max()*1.05],
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