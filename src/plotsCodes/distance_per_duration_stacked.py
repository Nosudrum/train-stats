from utils import dark_figure, extract_trips_journeys, PARIS_TZ, COLORS, prepare_legend, finish_figure, compute_stats
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

import numpy as np

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
    trips, journeys = extract_trips_journeys(trips, filter_end=datetime.now(tz=PARIS_TZ))

    fig, ax = dark_figure()
    years = trips["Departure (Local)"].dt.year.unique().tolist()
    bottom = np.zeros(len(years))
    for ii, tier in enumerate(TIERS):
        min_duration = timedelta(hours=tier[0])
        max_duration = timedelta(hours=tier[1])
        distances = []
        tier_mask = trips["Duration"].between(min_duration, max_duration, inclusive="left")
        for year in years:
            distances.append(
                trips.loc[tier_mask & (trips["Departure (Local)"].dt.year == year), "Distance (km)"].sum()
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
    distance_str, duration_str = compute_stats(trips, timezone=PARIS_TZ)
    fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
    fig_axes.text(0, 0.12, distance_str, ha="right", va="bottom", color="white", fontsize=10)
    fig_axes.text(0, 0, duration_str, ha="right", va="bottom", color="white", fontsize=10)
    fig_axes.axis("off")
    finish_figure(fig, ax, "distance_per_duration_stacked", show=False)
