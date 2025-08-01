from datetime import datetime

from pytz import timezone

from plotsCodes.graphs import (
    plot_distance_per_duration,
    plot_distance_per_operator,
    plot_duration_per_operator,
    plot_number_per_duration,
    plot_number_per_operator,
    plot_spending_per_operator,
    plot_timed_distance_per_operator,
    plot_timed_number_per_operator,
)
from plotsCodes.maps import plot_heatmap, plot_journeys_map
from plotsCodes.timelines import (
    plot_distance_timeline,
    plot_duration_timeline,
    plot_number_timeline,
)
from plotsCodes.trips import plot_trip_map
from utils import TrainStatsData, MapboxStyle, TripParams, MapParams
from utils.plotting import PlotParams

GOOGLE_SHEET_DT_FORMAT = "%d/%m/%Y %H:%M:%S"


class PlotConfig:
    def __init__(self, **kwargs):
        self._skip = kwargs["Skip"]
        self._plot_type = kwargs["Type"]

        # Set the plot parameters
        if kwargs["Title"] and kwargs["Filename"]:
            self._plot_params = PlotParams(
                kwargs["Title"],
                kwargs["Filename"],
                is_portrait=kwargs["Portrait"],
            )
        else:
            raise Exception("Title is required")

        # Set the trip parameters (start and end) if they exist
        if kwargs["Start"] and kwargs["End"]:
            self._trip_params = TripParams(
                datetime.strptime(kwargs["Start"], GOOGLE_SHEET_DT_FORMAT).replace(
                    tzinfo=timezone(kwargs["Start TZ"])
                ),
                datetime.strptime(kwargs["End"], GOOGLE_SHEET_DT_FORMAT).replace(
                    tzinfo=timezone(kwargs["End TZ"])
                ),
            )
        else:
            self._trip_params = None

        # Set the map parameters if they exist
        if kwargs["Lon min"]:
            self._map_params = MapParams(
                kwargs["Title"],
                kwargs["Filename"],
                kwargs["Lon min"],
                kwargs["Lon max"],
                kwargs["Lat min"],
                kwargs["Lat max"],
                kwargs["Zoom level"],
                kwargs["Projection"],
                is_portrait=kwargs["Portrait"],
            )
        else:
            self._map_params = None

    def run(self, data: TrainStatsData, mapbox_style: MapboxStyle):
        if self._skip:
            print(f"Skipping [{self._plot_type}] {self._plot_params.file_name}")
            return
        else:
            print(f"Generating [{self._plot_type}] {self._plot_params.file_name} ...")
        match self._plot_type:
            case "Distance per duration":
                return plot_distance_per_duration(data, self._plot_params)
            case "Distance per operator":
                return plot_distance_per_operator(data, self._plot_params)
            case "Duration per operator":
                return plot_duration_per_operator(data, self._plot_params)
            case "Number per duration":
                return plot_number_per_duration(data, self._plot_params)
            case "Number per operator":
                return plot_number_per_operator(data, self._plot_params)
            case "Spending per operator":
                return plot_spending_per_operator(data, self._plot_params)
            case "Timed distance per operator":
                return plot_timed_distance_per_operator(data, self._plot_params)
            case "Timed number per operator":
                return plot_timed_number_per_operator(data, self._plot_params)
            case "Heatmap":
                return plot_heatmap(data, mapbox_style, self._map_params)
            case "Journeys map":
                return plot_journeys_map(data, mapbox_style, self._map_params)
            case "Distance timeline":
                return plot_distance_timeline(data, self._plot_params)
            case "Duration timeline":
                return plot_duration_timeline(data, self._plot_params)
            case "Number timeline":
                return plot_number_timeline(data, self._plot_params)
            case "Trip map":
                return plot_trip_map(
                    data, mapbox_style, self._trip_params, self._map_params
                )
            case _:
                raise Exception("Unknown plot type")
