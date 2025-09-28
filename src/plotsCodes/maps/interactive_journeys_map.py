import folium
from tqdm import tqdm
from utils import MapboxStyle, TrainStatsData, MapParams
import geopandas
import matplotlib
from matplotlib.colors import rgb2hex
# import branca.colormap as cm


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
    values = journeys["count"].values
    color_map = matplotlib.colormaps["rainbow"]

    journeys_list = journeys.index.to_list()
    for journey in tqdm(
        journeys_list,
        ncols=150,
        desc=f"{params.title} (Portrait)" if params.is_portrait else params.title,
    ):
        count = journeys.loc[journey, "count"]

        geojson = data.get_geojson(journey)

        tmp = geopandas.GeoDataFrame.from_features(geojson, crs="epsg:4326")
        tmp["name"] = f"<b>{journey}</b>"
        tmp["count"] = count
        if journeys.loc[journey, "firstdate"] < data.NOW:
            tmp["label"] = (
                f"<center>Traveled {count} time{'s' if count > 1 else ''}</center>"
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
                    color_map((x["properties"]["count"] - 1) / (values.max() - 1))
                ),
                "dashArray": x["properties"]["dashArray"],
            },
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # Logging
    print("Finalizing plot...")

    m.save(f"../plots/{params.file_name}.html")
