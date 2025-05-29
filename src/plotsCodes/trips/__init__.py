from utils import TrainStatsData, TripParams, MapParams
from utils.mapbox import MapboxStyle

# from .trip_2019_china import plot_china_2019_portrait
# from .trip_2023_germany import plot_germany_2023
# from .trip_2023_uk_nye import plot_uk_nye_2023
# from .trip_2024_milano_iac import plot_milano_iac_2024
# from .trip_2024_october_alsace import plot_october_alsace_2024
# from .trip_2024_scandinavia import plot_scandinavia_2024, plot_scandinavia_2024_portrait
# from .trip_2025_netherlands_germany import (
#     plot_netherlands_germany_2025,
#     plot_nl_de_2025_portrait,
# )
from .trip_map import plot_trip_map
from datetime import datetime
from utils.plot_utils import PARIS_TZ


def plot_trips(data: TrainStatsData, mapbox_style: MapboxStyle):
    print("Plotting trips...")

    # plot_china_2019_portrait(data, mapbox_style)
    # plot_germany_2023(data, mapbox_style)
    # plot_uk_nye_2023(data, mapbox_style)
    # plot_scandinavia_2024(data, mapbox_style)
    # plot_scandinavia_2024_portrait(data, mapbox_style)
    # plot_milano_iac_2024(data, mapbox_style)
    # plot_october_alsace_2024(data, mapbox_style)
    # plot_netherlands_germany_2025(data, mapbox_style)
    # plot_nl_de_2025_portrait(data, mapbox_style)

    plot_trip_map(
        data,
        mapbox_style,
        TripParams(
            datetime(2024, 4, 26, 0, 0, 0, tzinfo=PARIS_TZ),
            datetime(2024, 5, 20, 23, 59, 59, tzinfo=PARIS_TZ),
        ),
        MapParams(
            "2024 Scandinavia Interrail Trip", "2024_scandinavia", -21, 29, 37, 66.5, 5
        ),
    )
    plot_trip_map(
        data,
        mapbox_style,
        TripParams(
            datetime(2024, 4, 26, 0, 0, 0, tzinfo=PARIS_TZ),
            datetime(2024, 5, 20, 23, 59, 59, tzinfo=PARIS_TZ),
        ),
        MapParams(
            "2024 Scandinavia Interrail Trip",
            "2024_scandinavia_portrait",
            -2.4,
            19.4,
            38.6,
            69,
            5,
            True,
        ),
    )
