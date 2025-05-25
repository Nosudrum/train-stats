from utils import TrainStatsData
from .distance_per_day import plot_distance_per_day


def plot_timelines(data: TrainStatsData):
    print("Plotting timelines...")

    plot_distance_per_day(data)
