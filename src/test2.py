from PIL import Image
import requests
from io import BytesIO

# read Mapbox token
with open('../data/mapbox_token.txt', 'r') as f:
    mapbox_token = f.read()

with open('../data/mapbox_style_token.txt', 'r') as f:
    mapbox_style_token = f.read()

with open('../data/mapbox_style_id.txt', 'r') as f:
    mapbox_style_id = f.read()

username = "nosu"

overlay= ""

lon_min = -6
lat_min = 40
lon_max = 18
lat_max = 55


bbox = f"[{lon_min},{lat_min},{lon_max},{lat_max}]"

zoom = 5

width = 1280
height = int(1280 * (lat_max - lat_min) / (lon_max - lon_min))

lon = (lon_min + lon_max) / 2
lat = (lat_min + lat_max) / 2

url = f"https://api.mapbox.com/styles/v1/{username}/{mapbox_style_id}/static/{bbox}/{width}x{height}@2x?access_token={mapbox_token}&logo=false&attribution=false"

# url = f"https://api.mapbox.com/styles/v1/{username}/{mapbox_style_id}/static/{lon},{lat},{zoom}/{width}x{height}@2x?access_token={mapbox_token}&logo=false&attribution=false"


response = requests.get(url)
img = Image.open(BytesIO(response.content))
img.save("../plots/test2.png")

