from plotsCodes import plot_graphs, plot_maps, plot_timelines, plot_trips
from utils import MapboxStyle, TrainStatsData

if __name__ == "__main__":
    # Setup Mapbox secrets
    mapbox_style = MapboxStyle()

    # Setup data
    data = TrainStatsData()

    # Generate plots
    print("Generating plots...")

    plot_graphs(data)
    plot_maps(data, mapbox_style)
    plot_timelines(data)
    plot_trips(data, mapbox_style)

    # Exit successfully
    print("All done!")
    exit(code=0)
