from datetime import datetime

import numpy as np
from cartopy.crs import PlateCarree, Robinson, Projection


class TripParams:
    def __init__(self, start: datetime, end: datetime):
        self.start: datetime = start
        self.end: datetime = end

    def get_trip_duration_days(self):
        return (self.end - self.start).days + 1


class PlotParams:
    def __init__(self, title: str, file_name: str, is_portrait: bool = False):
        self.title: str = title
        self.file_name: str = file_name
        self.is_portrait: bool = is_portrait

    def get_fig_size(self):
        if self.is_portrait:
            return 4, 7.1111
        else:
            return 7, 5.2

    def get_line_width(self):
        if self.is_portrait:
            return 1.7
        else:
            return 1.2

    def get_colorbar_axes(self):
        if self.is_portrait:
            return [0.08, 0.08, 0.8, 0.035]
        else:
            return [0.1, 0.08, 0.8, 0.035]

    def get_colorbar_ticks(self, count: int):
        if count <= 10 or (not self.is_portrait and count <= 26):
            return np.arange(0.5, count + 0.5)
        largest_divider = 1
        for i in range(2, count - 1):
            if (count - 1) % i == 0:
                largest_divider = i
        return np.linspace(0, count - 1, largest_divider + 1) + 0.5

    def get_stats_axes(self):
        if self.is_portrait:
            return [0.95, 0.027, 0.3, 0.3]
        else:
            return [0.97, 0.027, 0.3, 0.3]

    def get_split_stats_texts(self, distance_str: str, duration_str: str):
        index = duration_str.find(" out of")
        if self.is_portrait and index != -1:
            # Split the duration string if too long for portrait mode
            return distance_str, duration_str[:index], duration_str[index:]
        else:
            return distance_str, duration_str

    def get_split_stats_positions(self, distance_str: str, duration_str: str):
        if not self.is_portrait:
            return [0, 0.12], [0, 0]
        if len(self.get_split_stats_texts(distance_str, duration_str)) == 3:
            return [0, 0.08], [0, 0], [0, 0.19]
        else:
            return [0, 0.16], [0, 0.03]

    def get_stats_font_size(self):
        if self.is_portrait:
            return 9
        else:
            return 10

    def get_logo_position(self):
        if self.is_portrait:
            return [0.05, 0.656, 0.4, 0.3]
        else:
            return None


class MapParams(PlotParams):
    def __init__(
        self,
        title: str,
        file_name: str,
        lon_min: float,
        lon_max: float,
        lat_min: float,
        lat_max: float,
        zoom_level: int,
        map_projection: str,
        is_portrait: bool = False,
    ):
        super().__init__(title, file_name, is_portrait)
        self._lon_min: float = lon_min
        self._lon_max: float = lon_max
        self._lat_min: float = lat_min
        self._lat_max: float = lat_max
        self.zoom_level: int = zoom_level
        self.map_projection: Projection = self._match_map_projection(map_projection)

    def get_extent(self):
        return [self._lon_min, self._lon_max, self._lat_min, self._lat_max]

    def _match_map_projection(self, map_projection: str):
        if map_projection == "PlateCarree":
            return PlateCarree()
        elif map_projection == "Robinson":
            return Robinson()
        else:
            raise ValueError(f"Unknown map projection: {map_projection}.")
