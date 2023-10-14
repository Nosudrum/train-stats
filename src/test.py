import json
import os
from matplotlib.image import imread
import cartopy.io.img_tiles as cimgt

from PlotFunctions import *

# read Mapbox token
with open('../data/mapbox_token.txt', 'r') as f:
    mapbox_token = f.read()

with open('../data/mapbox_style_token.txt', 'r') as f:
    mapbox_style_token = f.read()

with open('../data/mapbox_style_id.txt', 'r') as f:
    mapbox_style_id = f.read()

# isolate coordinates


fig, ax = dark_figure(grid=False, projection=ccrs.Robinson())

request = cimgt.MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
# fig = plt.figure(figsize=(10, 5), facecolor="#0D1117")
# ax[0] = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
extent = [-6, 18, 40, 55]  # (xmin, xmax, ymin, ymax)
ax[0].set_extent(extent)
ax[0].imshow(imread("../plots/test2.png"), origin='upper', transform=ccrs.PlateCarree(),
              extent = [-6, 18, 40, 55], interpolation='spline36', regrid_shape=2000)

# for all journeys in the dataset
for journey in os.listdir('../data/journeys_coords'):
    with open('../data/journeys_coords/' + journey, 'r', encoding="utf8") as f:
        geojson = json.load(f)
        coords = np.array(geojson['features'][0]['geometry']['coordinates'])
        ax[0].plot(coords[:, 0], coords[:, 1], '.', color="cyan", transform=ccrs.PlateCarree(), markersize=0.5)

ax[0].set(
    title="All my train journeys since 2013",
)

finish_map(fig, ax, "test", show=False)
