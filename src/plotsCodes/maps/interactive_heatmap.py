import folium
from utils import MapboxStyle, TrainStatsData, MapParams
import matplotlib
from matplotlib.colors import rgb2hex
from tqdm import tqdm


def plot_interactive_heatmap(
    data: TrainStatsData, mapbox_style: MapboxStyle, params: MapParams
):
    # Compute coords dataframe
    coords = data.get_travel_coordinate_couples(filter_end=data.NOW)

    coords_counts = (
        coords.groupby(["lon1", "lat1", "lon2", "lat2"], sort=False)
        .agg(
            {
                "count": "sum",  # Sum the counts for each group
            }
        )
        .reset_index()
    ).reset_index(drop=True)

    max_count = coords_counts["count"].max()
    color_map = matplotlib.colormaps["rainbow"]

    m = folium.Map(
        tiles=None,
        location=[params.get_center_lat(), params.get_center_lon()],
        zoom_start=params.zoom_level,
        max_bounds=True,
    )
    folium.TileLayer(
        tiles=mapbox_style.get_tile_url(),
        attr="Mapbox",
        name="Custom train-stats.com style",
        overlay=False,
    ).add_to(m)
    folium.TileLayer(
        "OpenStreetMap",
        attr="OpenStreetMap",
        name="OpenStreetMap",
        show=False,
        overlay=False,
    ).add_to(m)

    pbar = tqdm(total=coords_counts.shape[0])
    row_index = coords_counts.index[0]

    number_of_polylines = 0

    # Initialize the coordinates list
    coordinates = [
        [coords_counts.loc[row_index]["lat1"], coords_counts.loc[row_index]["lon1"]],
    ]

    # For all sets of coordinates
    while row_index <= coords_counts.index[-1]:
        if row_index < coords_counts.index[-1] and _next_row_is_contiguous(
            coords_counts, row_index
        ):
            # Next row is contiguous, add the coordinates to the list
            coordinates.append(
                [
                    coords_counts.loc[row_index + 1]["lat1"],
                    coords_counts.loc[row_index + 1]["lon1"],
                ]
            )
        else:
            # Next row is not contiguous or does not exist, complete the current coordinates list
            coordinates.append(
                [
                    coords_counts.loc[row_index]["lat2"],
                    coords_counts.loc[row_index]["lon2"],
                ]
            )

            # Create a PolyLine and add it to the map
            count = coords_counts.loc[row_index]["count"]
            folium.PolyLine(
                locations=coordinates,
                color=rgb2hex(color_map((count - 1) / (max_count - 1))),
            ).add_to(m)
            number_of_polylines += 1

            if row_index < coords_counts.index[-1]:
                # Reset the coordinates list and count
                coordinates = [
                    [
                        coords_counts.loc[row_index + 1]["lat1"],
                        coords_counts.loc[row_index + 1]["lon1"],
                    ]
                ]

        row_index += 1
        pbar.update(1)

    pbar.close()
    folium.LayerControl().add_to(m)

    print(f"Number of polylines: {number_of_polylines}")

    # Logging
    print("Finalizing plot...")

    m.save(f"../plots/{params.file_name}.html")


def _next_row_is_contiguous(df, row_index):
    count_remains_same = df.loc[row_index + 1]["count"] == df.loc[row_index]["count"]
    longitudes_are_contiguous = (
        df.loc[row_index + 1]["lon1"] == df.loc[row_index]["lon2"]
    )
    latitudes_are_contiguous = (
        df.loc[row_index + 1]["lat1"] == df.loc[row_index]["lat2"]
    )
    coordinates_are_contiguous = longitudes_are_contiguous and latitudes_are_contiguous
    return count_remains_same and coordinates_are_contiguous
