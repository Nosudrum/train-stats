import os

from cartopy.io.img_tiles import MapboxStyleTiles
from dotenv import load_dotenv

load_dotenv()


class MapboxStyle(MapboxStyleTiles):
    def __init__(self):
        super().__init__(
            os.environ["MAPBOX_STYLE_TOKEN"],
            os.environ["MAPBOX_USERNAME"],
            os.environ["MAPBOX_STYLE_ID"],
        )
