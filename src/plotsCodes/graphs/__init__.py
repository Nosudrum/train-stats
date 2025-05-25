from utils import TrainStatsData
from .distance_per_duration_stacked import plot_distance_per_duration_stacked
from .distance_per_operator_stacked import plot_distance_per_operator_stacked
from .duration_per_operator_stacked import plot_duration_per_operator_stacked
from .number_per_duration_stacked import plot_number_per_duration_stacked
from .number_per_operator_stacked import plot_number_per_operator_stacked
from .spending_per_operator_stacked import plot_spending_per_operator_stacked


def plot_graphs(data: TrainStatsData):
    print("Plotting graphs...")

    plot_distance_per_operator_stacked(data)
    plot_distance_per_duration_stacked(data)
    plot_duration_per_operator_stacked(data)
    plot_number_per_operator_stacked(data)
    plot_number_per_duration_stacked(data)
    plot_spending_per_operator_stacked(data)
