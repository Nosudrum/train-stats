import json
import os

import cartopy.io.img_tiles as cimgt
import matplotlib
import matplotlib.cm as cm

from PlotFunctions import *
from test3 import journeys

# read Mapbox token
with open('../data/mapbox_token.txt', 'r') as f:
    mapbox_token = f.read()

with open('../data/mapbox_style_token.txt', 'r') as f:
    mapbox_style_token = f.read()

with open('../data/mapbox_style_id.txt', 'r') as f:
    mapbox_style_id = f.read()

# isolate coordinates

# fig, ax = plt.subplots(facecolor=github_dark, figsize=(7, 5.2))

fig, ax = dark_figure(grid=False, projection=ccrs.Robinson())

request = cimgt.MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
# fig = plt.figure(figsize=(10, 5), facecolor="#0D1117")
# ax[0] = fig.add_subplot(1, 1, 1, projection=ccrs.Robinson())
extent = [-6, 18, 40, 55]  # (xmin, xmax, ymin, ymax) #
ax[0].set_extent(extent)
ax[0].add_image(request, 5, regrid_shape=3000)
# ax[0].imshow(plt.imread("../plots/test2.png"), extent=extent)
# , origin='upper',
# transform=ccrs.PlateCarree()

# , interpolation='spline36', regrid_shape=2000
#

# for all journeys in the dataset
now = datetime.now()
values = journeys["count"].values
color_map = matplotlib.colormaps["viridis"]

for journey in os.listdir('../data/journeys_coords'):
    journey_name = journey.replace(".geojson", "")
    if journeys.loc[journey_name, "firstdate"] < now:
        s = "-"
    else:
        s = ":"

    count = journeys.loc[journey_name, "count"]
    c = color_map(count / (values.max()))

    with open('../data/journeys_coords/' + journey, 'r', encoding="utf8") as f:
        geojson = json.load(f)
        coords = np.array(geojson['features'][0]['geometry']['coordinates'])
        ax[0].plot(coords[:, 0], coords[:, 1], s, color=c, markersize=0.5, transform=ccrs.PlateCarree(), zorder=count)

# Setup colorbar
sm = cm.ScalarMappable(cmap=color_map, norm=plt.Normalize(vmin=0, vmax=values.max()))
sm.set_array([])
cax = ax[0].inset_axes([0.1, 0.08, 0.8, 0.035])
cbar = fig.colorbar(sm, orientation="horizontal", cax=cax)
cbar.ax.set_title("Journey counts", color="white", fontsize=8)
plt.setp(plt.getp(cbar.ax, 'xticklabels'), color='white', fontsize=12)

ax[0].set(
    title="All European train journeys since 2013",
)

finish_map(fig, ax, "test", colorbar=cbar, show=False)
