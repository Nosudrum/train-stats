from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np

from utils import (
    dark_figure,
    GITHUB_DARK,
    extract_trips_journeys,
    PARIS_TZ,
    COLORS,
    prepare_legend,
    finish_figure,
    compute_stats,
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
def plot_distance_per_duration_stacked(trips):
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
    for ii, tier in enumerate(TIERS):
        min_duration = timedelta(hours=tier[0])
        max_duration = timedelta(hours=tier[1])
        distances = []
        tier_mask = past_trips["Duration"].between(
            min_duration, max_duration, inclusive="left"
        )
        for year in years:
            distances.append(
                past_trips.loc[
                    tier_mask & (past_trips["Departure (Local)"].dt.year == year),
                    "Distance (km)",
                ].sum()
            )
        distances = np.array(distances)
        ax[0].bar(
            years,
            distances,
            bottom=bottom,
            color=COLORS[ii],
            label=tier[2],
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
        title="Distance travelled by train per duration since " + str(min(years)),
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
    finish_figure(fig, ax, "distance_per_duration_stacked", show=False)
