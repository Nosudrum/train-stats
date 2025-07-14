import matplotlib.pyplot as plt
import pandas as pd
from utils import TrainStatsData
from utils.plot_utils import (
    dark_figure,
    COLORS,
    prepare_legend,
    finish_figure,
)
from utils.plotting import PlotParams
import numpy as np
import matplotlib.dates as mdates


# Plot of km travelled by train journey duration
def plot_timed_number_per_operator(data: TrainStatsData, params: PlotParams):
    past_trips = data.get_past_trips()

    operators = past_trips["Operator"].copy()
    operators_sorted = operators.value_counts().index.tolist()
    operators_selected = operators_sorted[0:7]
    operators.loc[~operators.isin(operators_selected)] = "Others"
    operators_selected.append("Others")

    # Initialize an array for each minute of the day
    minute_counts = np.zeros((8, 1440), dtype=int)

    for index, operator in enumerate(operators_selected):
        operator_trips = past_trips[operators == operator]

        # Convert depart/arrival to minutes from midnight
        departure_dates = operator_trips["Departure (Local)"].dt.date
        departure_minutes = (
            operator_trips["Departure (Local)"].dt.hour
        ) * 60 + operator_trips["Departure (Local)"].dt.minute
        arrival_dates = operator_trips["Arrival (Local)"].dt.date
        arrival_minutes = (
            operator_trips["Arrival (Local)"].dt.hour * 60
            + operator_trips["Arrival (Local)"].dt.minute
        )

        for departure_date, departure_minute, arrival_date, arrival_minute in zip(
            departure_dates, departure_minutes, arrival_dates, arrival_minutes
        ):
            date_delta = arrival_date - departure_date
            match date_delta.days:
                case 0:
                    # Trip entirely within the same day
                    minute_counts[index, departure_minute:arrival_minute] += 1
                case 1:
                    # Trip over two days (e.g. night train)
                    minute_counts[index, departure_minute:] += 1
                    minute_counts[index, :arrival_minute] += 1
                case _:
                    # Trip over multiple days (e.g. long distance train)
                    minute_counts[index, departure_minute:] += 1
                    minute_counts[index, :arrival_minute] += 1
                    minute_counts[index, :] += date_delta.days - 1

    datetimes = pd.date_range(
        start="00:00",
        end="23:59",
        freq="min",
    )

    fig, ax = dark_figure()
    ax[0].stackplot(
        datetimes,
        minute_counts,
        labels=operators_selected,
        step="post",
        colors=COLORS,
    )

    handles, labels = prepare_legend(reverse=False)
    ax[0].legend(
        handles, labels, loc="upper center", ncol=4, frameon=False, labelcolor="white"
    )
    ax[0].set(
        ylabel="Total trains taken",
        xlim=[min(datetimes), max(datetimes)],
        title=params.title,
    )
    ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
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
