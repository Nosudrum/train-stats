from utils import MapboxStyle, TrainStatsData
from utils.config import PlotConfig

if __name__ == "__main__":
    # Setup Mapbox secrets
    mapbox_style = MapboxStyle()

    # Setup data
    data = TrainStatsData()

    # Generate plots
    print("Generating plots...")
    config = data.get_plots_config()

    for index, plot in config.iterrows():
        PlotConfig(**plot).run(data, mapbox_style)

    # Exit successfully
    print("All done!")
    exit(code=0)
