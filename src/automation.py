from plotsCodes.all_europe import plot_all_europe
from plotsCodes.all_europe_portrait import plot_all_europe_portrait
from plotsCodes.china_2019_portrait import plot_china_2019_portrait
from plotsCodes.distance_per_day import plot_distance_per_day
from plotsCodes.distance_per_duration_stacked import plot_distance_per_duration_stacked
from plotsCodes.distance_per_operator_stacked import plot_distance_per_operator_stacked
from plotsCodes.duration_per_operator_stacked import plot_duration_per_operator_stacked
from plotsCodes.germany_2023 import plot_germany_2023
from plotsCodes.milano_iac_2024 import plot_milano_iac_2024
from plotsCodes.number_per_duration_stacked import plot_number_per_duration_stacked
from plotsCodes.number_per_operator_stacked import plot_number_per_operator_stacked
from plotsCodes.october_alsace_2024 import plot_october_alsace_2024
from plotsCodes.scandinavia_2024 import plot_scandinavia_2024
from plotsCodes.scandinavia_2024_portrait import plot_scandinavia_2024_portrait
from plotsCodes.spending_per_operator_stacked import plot_spending_per_operator_stacked
from plotsCodes.uk_nye_2023 import plot_uk_nye_2023
from processing import process_trips, process_additional_spending
from utils import get_mapbox_secrets

if __name__ == "__main__":
    # Import Mapbox secrets
    MAPBOX_STYLE_TOKEN, MAPBOX_STYLE_ID = get_mapbox_secrets()

    # Import data
    trips = process_trips()
    additional_spending = process_additional_spending()

    # Generate plots
    print("Generating plots...")

    plot_all_europe(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_all_europe_portrait(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_china_2019_portrait(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_germany_2023(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_scandinavia_2024(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_scandinavia_2024_portrait(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_milano_iac_2024(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_october_alsace_2024(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )
    plot_uk_nye_2023(
        trips, mapbox_style_id=MAPBOX_STYLE_ID, mapbox_style_token=MAPBOX_STYLE_TOKEN
    )

    plot_number_per_duration_stacked(trips)
    plot_number_per_operator_stacked(trips)
    plot_distance_per_day(trips)
    plot_distance_per_duration_stacked(trips)
    plot_distance_per_operator_stacked(trips)
    plot_duration_per_operator_stacked(trips)
    plot_spending_per_operator_stacked(trips, additional_spending)

    # Exit successfully
    print("All done!")
    exit(code=0)
