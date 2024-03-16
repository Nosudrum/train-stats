import json
import os
from tqdm import tqdm

import cartopy.io.img_tiles as cimgt
import matplotlib
import matplotlib.cm as cm

from PlotFunctions import *
from test3 import journeys, total_distance, total_time

# read Mapbox token
with open('../data/mapbox_token.txt', 'r') as f:
    mapbox_token = f.read()

with open('../data/mapbox_style_token.txt', 'r') as f:
    mapbox_style_token = f.read()

with open('../data/mapbox_style_id.txt', 'r') as f:
    mapbox_style_id = f.read()

longitude_min = -21
longitude_max = 29
latitude_min = 37
latitude_max = 66.5

# Projections
# ccrs.Robinson()
# ccrs.Orthographic(
#     central_longitude=(longitude_min + longitude_max) / 2,
#     central_latitude=(latitude_min + latitude_max) / 2)
#                       )

fig, ax = dark_figure(grid=False, projection=ccrs.Robinson())
request = cimgt.MapboxStyleTiles(mapbox_style_token, "nosu", mapbox_style_id, cache=False)
extent = [longitude_min, longitude_max, latitude_min, latitude_max]
ax[0].set_extent(extent)
ax[0].add_image(request, 5, regrid_shape=3000)

# for all journeys in the dataset
now = datetime.now()
values = journeys["count"].values
color_map = matplotlib.colormaps["viridis"]

journeys_list = os.listdir('../data/journeys_coords')
pbar = tqdm(journeys_list, ncols=150)

for journey in pbar:
    pbar.set_description("Plotting " + journey)
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
        ax[0].plot(coords[:, 0], coords[:, 1], s, linewidth=1.2, color=c, transform=ccrs.PlateCarree(), zorder=count,
                   solid_capstyle="round")

# Logging
print("Finalizing plot...")

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
plt.tight_layout()
fig_axes = fig.add_axes([0.97, 0.027, 0.3, 0.3], anchor="SE", zorder=1)
fig_axes.text(0, 0.12, f"{round(total_distance):_} km ({round(total_distance / 1.609344):_} mi)".replace('_', ' '),
              ha="right", va="bottom", color="white", fontsize=10)
fig_axes.text(0, 0,
              f"> {total_time.days} days {divmod(total_time.seconds, 3600)[0]} hours {divmod(total_time.seconds, 3600)[1] // 60} minutes",
              ha="right", va="bottom", color="white", fontsize=10)

fig_axes.axis("off")

finish_map(fig, ax, "test", colorbar=cbar, show=False)
