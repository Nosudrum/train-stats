from utils import TrainStatsData
from utils.mapbox import MapboxStyle
from .trip_2019_china import plot_china_2019_portrait
from .trip_2023_germany import plot_germany_2023
from .trip_2023_uk_nye import plot_uk_nye_2023
from .trip_2024_milano_iac import plot_milano_iac_2024
from .trip_2024_october_alsace import plot_october_alsace_2024
from .trip_2024_scandinavia import plot_scandinavia_2024, plot_scandinavia_2024_portrait
from .trip_2025_netherlands_germany import (
    plot_netherlands_germany_2025,
    plot_nl_de_2025_portrait,
)


def plot_trips(data: TrainStatsData, mapbox_style: MapboxStyle):
    print("Plotting trips...")

    plot_china_2019_portrait(data, mapbox_style)
    plot_germany_2023(data, mapbox_style)
    plot_uk_nye_2023(data, mapbox_style)
    plot_scandinavia_2024(data, mapbox_style)
    plot_scandinavia_2024_portrait(data, mapbox_style)
    plot_milano_iac_2024(data, mapbox_style)
    plot_october_alsace_2024(data, mapbox_style)
    plot_netherlands_germany_2025(data, mapbox_style)
    plot_nl_de_2025_portrait(data, mapbox_style)
