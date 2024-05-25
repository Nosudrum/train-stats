from plotsCodes.all_europe import plot_all_europe
from plotsCodes.all_europe_portrait import plot_all_europe_portrait
from plotsCodes.germany_2023 import plot_germany_2023
from plotsCodes.scandinavia_2024 import plot_scandinavia_2024
from plotsCodes.scandinavia_2024_portrait import plot_scandinavia_2024_portrait
from plotsCodes.number_per_duration_stacked import plot_number_per_duration_stacked
from plotsCodes.distance_per_duration_stacked import plot_distance_per_duration_stacked
from processing import process_data
from utils import get_mapbox_secrets

if __name__ == "__main__":
    # Import Mapbox secrets
    MAPBOX_STYLE_TOKEN, MAPBOX_STYLE_ID = get_mapbox_secrets()

    # Import data
    trips = process_data()

    # Generate plots
    print("Generating plots...")
    plot_all_europe(trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN)
    plot_all_europe_portrait(trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN)
    plot_germany_2023(trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN)
    plot_scandinavia_2024(trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN)
    plot_scandinavia_2024_portrait(trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN)
    plot_number_per_duration_stacked(trips)
    plot_distance_per_duration_stacked(trips)

    # Exit successfully
    print("All done!")
    exit(code=0)
