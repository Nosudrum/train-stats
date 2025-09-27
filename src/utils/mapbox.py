import os

from cartopy.io.img_tiles import MapboxStyleTiles
from dotenv import load_dotenv

load_dotenv()


class MapboxStyle(MapboxStyleTiles):
    def __init__(self):
        self.style_token = os.environ["MAPBOX_STYLE_TOKEN"]
        self.username = os.environ["MAPBOX_USERNAME"]
        self.map_id = os.environ["MAPBOX_STYLE_ID"]

        super().__init__(
            os.environ["MAPBOX_STYLE_TOKEN"],
            os.environ["MAPBOX_USERNAME"],
            os.environ["MAPBOX_STYLE_ID"],
        )

    def get_tile_url(self) -> str:
        return f"https://api.mapbox.com/styles/v1/{self.username}/{self.map_id}/tiles/{{z}}/{{x}}/{{y}}?access_token={self.style_token}"
