from utils import TrainStatsData
from utils.mapbox import MapboxStyle
from .europe_heatmap import plot_all_europe_heatmap
from .europe_heatmap_portrait import plot_all_europe_heatmap_portrait
from .europe_journeys import plot_all_europe
from .europe_journeys_portrait import plot_all_europe_portrait


def plot_maps(data: TrainStatsData, mapbox_style: MapboxStyle):
    print("Plotting maps...")

    plot_all_europe_heatmap(data, mapbox_style)
    plot_all_europe(data, mapbox_style)
    plot_all_europe_heatmap_portrait(data, mapbox_style)
    plot_all_europe_portrait(data, mapbox_style)
