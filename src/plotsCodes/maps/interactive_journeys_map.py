import folium
from tqdm import tqdm
from utils import MapboxStyle, TrainStatsData, MapParams
import geopandas
import matplotlib
from matplotlib.colors import rgb2hex


def plot_interactive_journeys_map(
    data: TrainStatsData, mapbox_style: MapboxStyle, params: MapParams
):
    # Compute journeys dataframe
    journeys = data.get_journeys()
    journeys.sort_values("count", ascending=True, inplace=True)

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

    # For all journeys in the dataset
    max_count = journeys["count"].max()
    color_map = matplotlib.colormaps["rainbow"]

    for journey in tqdm(
        journeys.index.to_list(),
        ncols=150,
        desc=f"{params.title} (Journeys)",
    ):
        count = journeys.loc[journey, "count"]

        geojson = data.get_geojson(journey)

        distance = journeys.loc[journey, "distance"]

        tmp = geopandas.GeoDataFrame.from_features(geojson, crs="epsg:4326")
        tmp["name"] = f"<b>{journey}</b>"
        tmp["count"] = count
        if journeys.loc[journey, "firstdate"] < data.NOW:
            tmp["label"] = (
                f"<center>Traveled {count} time{'s' if count > 1 else ''} ({round(distance)} km)</center>"
            )
            tmp["dashArray"] = "0, 0"
        else:
            tmp["label"] = "Travel planned in the future"
            tmp["dashArray"] = "2, 10"

        popup = folium.GeoJsonPopup(
            fields=["name", "label"],
            labels=False,
        )

        folium.GeoJson(
            tmp,
            name=journey,
            control=False,
            popup=popup,
            style_function=lambda x: {
                "color": rgb2hex(
                    color_map((x["properties"]["count"] - 1) / (max_count - 1))
                ),
                "dashArray": x["properties"]["dashArray"],
            },
        ).add_to(m)

    # Get all stations
    stations = data.get_past_stations()

    # For all stations in the dataset
    for station in tqdm(
        stations.index.to_list(),
        ncols=150,
        desc=f"{params.title} (Stations)",
    ):
        # Get the data
        row = stations.loc[station]

        # Add a dot (CircleMarker) to the map
        tooltip = folium.Tooltip(
            f"<b>{station}</b> (visited {int(row['Visit_Count'])} time{'s' if row['Visit_Count'] > 1 else ''})",
        )

        folium.CircleMarker(
            name=row.index,
            tooltip=tooltip,
            location=[row["latitude"], row["longitude"]],
            radius=4,
            color=rgb2hex(color_map((row["Visit_Count"] - 1) / (max_count - 1))),
            fill=True,
            fill_color=rgb2hex(color_map((row["Visit_Count"] - 1) / (max_count - 1))),
            fill_opacity=1.0,
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # Logging
    print("Finalizing plot...")

    m.save(f"../plots/{params.file_name}.html")
