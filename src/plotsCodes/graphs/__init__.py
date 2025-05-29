from utils import TrainStatsData
from .distance_per_duration import plot_distance_per_duration
from .distance_per_operator import plot_distance_per_operator
from .duration_per_operator import plot_duration_per_operator
from .number_per_duration import plot_number_per_duration
from .number_per_operator import plot_number_per_operator
from .spending_per_operator import plot_spending_per_operator


def plot_graphs(data: TrainStatsData):
    print("Plotting graphs...")

    plot_distance_per_operator(data)
    plot_distance_per_duration(data)
    plot_duration_per_operator(data)
    plot_number_per_operator(data)
    plot_number_per_duration(data)
    plot_spending_per_operator(data)
