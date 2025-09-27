import json
import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from pytz import timezone
from requests import get

load_dotenv()


class TrainStatsData:
    PARIS_TZ = timezone("Europe/Paris")
    NOW = datetime.now(PARIS_TZ)
    EOY = datetime(datetime.now(PARIS_TZ).year + 1, 1, 1, 0, 0, 0, tzinfo=PARIS_TZ)

    _TRIPS_PATH = "../data/trips.csv"
    _ADDITIONAL_SPENDING_PATH = "../data/additional_spending.csv"
    _STATIONS_PATH = "../data/stations.csv"
    _CUSTOM_STATIONS_PATH = "../data/custom_stations_tz.csv"
    _JOURNEYS_PATH = "../data/journeys_coords/"
    _PLOTS_CONFIG_PATH = "../data/plots_config.csv"

    def __init__(self):
        self._stations: pd.DataFrame = pd.read_csv(
            self._STATIONS_PATH, sep=";", low_memory=False
        )
        self._custom_stations: pd.DataFrame = pd.read_csv(
            self._CUSTOM_STATIONS_PATH, sep=","
        )
        self._trips: pd.DataFrame = self._import_trips(os.environ["DATASHEET_ID"])
        self._additional_spending: pd.DataFrame = self._import_additional_spending(
            os.environ["DATASHEET_ID"], os.environ["ADDITIONAL_SPENDING_ID"]
        )
        self._plots_config: pd.DataFrame = self._import_plots_config(
            os.environ["DATASHEET_ID"], os.environ["PLOTS_CONFIG_ID"]
        )

    def get_past_trips(self, filter_start: datetime = None) -> pd.DataFrame:
        return self.get_trips(filter_start=filter_start, filter_end=self.NOW)

    def get_future_trips(self, current_year_only: bool = False) -> pd.DataFrame:
        filter_end = self.EOY if current_year_only else None
        return self.get_trips(filter_start=self.NOW, filter_end=filter_end)

    def get_trips(
        self, filter_start: datetime = None, filter_end: datetime = None
    ) -> pd.DataFrame:
        trips = self._trips.copy(deep=True)
        if filter_start is not None:
            trips = trips[trips["Departure"] >= filter_start]
        if filter_end is not None:
            trips = trips[trips["Arrival"] <= filter_end]
        return trips

    def get_additional_spending(self) -> pd.DataFrame:
        return self._additional_spending.copy(deep=True)

    def get_plots_config(self) -> pd.DataFrame:
        return self._plots_config.copy(deep=True)

    def get_journeys(
        self, filter_start: datetime = None, filter_end: datetime = None
    ) -> pd.DataFrame:
        trips = self.get_trips(filter_start, filter_end)

        journey_counts = trips["journey"].value_counts().to_frame()
        journey_distances = (
            trips[["journey", "Distance (km)"]].groupby("journey").mean()
        )
        journey_firstdate = trips[["journey", "Arrival"]].groupby("journey").min()
        journeys = journey_counts.join(journey_distances).join(journey_firstdate)
        journeys.rename(
            columns={"Distance (km)": "distance", "Arrival": "firstdate"},
            inplace=True,
        )
        return journeys

    def get_past_journeys(self) -> pd.DataFrame:
        return self.get_journeys(filter_end=self.NOW)

    def get_stats(
        self, start: datetime = None, end: datetime = None
    ) -> tuple[str, str]:
        if not start:
            start = self._trips["Departure"].min()
        if not end:
            end = self._trips["Arrival"].max()
        trips_total_mask = (self._trips["Departure"] >= start) & (
            self._trips["Arrival"] <= end
        )
        trips_current_mask = (self._trips["Departure"] >= start) & (
            self._trips["Arrival"] < self.NOW
        )
        total_duration = self._trips[trips_total_mask]["Duration"].sum()
        total_distance = self._trips[trips_total_mask]["Distance (km)"].dropna().sum()
        current_duration = self._trips[trips_current_mask]["Duration"].dropna().sum()
        current_distance = (
            self._trips[trips_current_mask]["Distance (km)"].dropna().sum()
        )

        if end <= self.NOW or start > self.NOW:
            # Trip has ended or hasn't started
            distance_str = self._format_km(total_distance)
            duration_str = self._format_timedelta(total_duration)
        else:
            # Trip is ongoing
            distance_str = (
                self._format_km(current_distance)
                + " out of "
                + self._format_km(total_distance)
            )
            duration_str = (
                self._format_timedelta(current_duration)
                + " out of "
                + self._format_timedelta(total_duration)
            )

        return distance_str, duration_str

    def get_journey_coordinates(self, journey: str) -> np.ndarray:
        with open(
            self._JOURNEYS_PATH + journey + ".geojson", "r", encoding="utf8"
        ) as f:
            geojson = json.load(f)
            return np.array(geojson["features"][0]["geometry"]["coordinates"])

    def get_geojson(self, journey: str) -> dict:
        with open(
            self._JOURNEYS_PATH + journey + ".geojson", "r", encoding="utf8"
        ) as f:
            return json.load(f)

    def get_travel_coordinates(
        self, filter_start: datetime = None, filter_end: datetime = None
    ) -> pd.DataFrame:
        trips = self.get_trips(filter_start, filter_end)
        all_coordinates = np.empty((0, 2))

        for journey in trips["journey"].tolist():
            with open(
                self._JOURNEYS_PATH + journey + ".geojson",
                "r",
                encoding="utf8",
            ) as f:
                geojson = json.load(f)
                coordinates = np.array(
                    geojson["features"][0]["geometry"]["coordinates"]
                )
                # remove duplicates within a single journey
                unique_coordinates = np.unique(coordinates, axis=0)
                all_coordinates = np.append(all_coordinates, unique_coordinates, axis=0)

        return pd.DataFrame(
            {
                "lon": all_coordinates[:, 0],
                "lat": all_coordinates[:, 1],
            }
        )

    def _km_to_mi(self, km: float) -> float:
        return km * 0.621371

    def _format_km(self, km: float) -> str:
        return f"{round(km):_} km ({round(self._km_to_mi(km)):_} mi)".replace("_", " ")

    def _format_timedelta(self, dt: timedelta) -> str:
        days = dt.days
        hours = divmod(dt.seconds, 3600)[0]
        minutes = divmod(dt.seconds, 3600)[1] // 60

        string = ""
        if days > 0:
            string += f"{days} day{'s' if days > 1 else ''}"
        if hours > 0:
            string += f" {hours} hour{'s' if hours > 1 else ''}"
        if minutes > 0:
            string += f" {minutes} minute{'s' if minutes > 1 else ''}"

        return string

    def _get_station_timezone(self, station: str) -> timezone:
        custom_tz = self._custom_stations.loc[
            self._custom_stations["name"] == station, "time_zone"
        ].head(1)
        if not custom_tz.empty:
            return timezone(custom_tz.item())
        stations_tz = self._stations.loc[
            self._stations["name"] == station, "time_zone"
        ].head(1)
        if not stations_tz.empty:
            return timezone(stations_tz.item())
        else:
            raise ValueError(
                f"Could not find station name [{station}] in either standard or custom station CSVs."
            )

    def _import_trips(self, datasheet_id: str) -> pd.DataFrame:
        # Get trips dataset and save to file
        r = get(
            f"https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&output=csv"
        )
        with open(self._TRIPS_PATH, "wb") as f:
            f.write(r.content)
        trips = pd.read_csv(self._TRIPS_PATH, header=0, skiprows=[1])

        # Rework dataframe
        trips = trips.rename(columns={"Alphabetical trip": "journey"})
        trips.dropna(inplace=True, subset=["Departure (Local)"])
        trips["Departure (Local)"] = pd.to_datetime(
            trips["Departure (Local)"], format="mixed"
        )
        trips["Arrival (Local)"] = pd.to_datetime(
            trips["Arrival (Local)"], format="mixed"
        )

        trips["Arrival"] = trips["Arrival (Local)"]
        trips["Departure"] = trips["Departure (Local)"]

        # Localize departure and arrival times
        for index, row in trips.iterrows():
            origin = row["Origin"]
            trips.loc[index, "Departure"] = trips.loc[index, "Departure"].tz_localize(
                self._get_station_timezone(origin)
            )
            destination = row["Destination"]
            trips.loc[index, "Arrival"] = trips.loc[index, "Arrival"].tz_localize(
                self._get_station_timezone(destination)
            )
        trips["Departure"] = pd.to_datetime(trips["Departure"], utc=True)
        trips["Arrival"] = pd.to_datetime(trips["Arrival"], utc=True)

        # Format durations
        trips["Duration"] = pd.to_timedelta(
            (trips["Duration"].str.split(":", expand=True).astype(int) * (60, 1)).sum(
                axis=1
            ),
            unit="min",
        )

        # Format prices
        trips["Price"] = trips["Price"].str.replace("€", "").astype(float)
        trips["Reimb"] = trips["Reimb"].str.replace("€", "").astype(float)

        # Replace special things
        trips.replace(
            "\xa0", " ", regex=True, inplace=True
        )  # Remove non-breaking spaces
        trips.replace(
            "Sinsheim Museum/Arena", "Sinsheim MuseumArena", regex=True, inplace=True
        )
        trips.replace(
            "Biel/Bienne", "BielBienne", regex=True, inplace=True
        )  # Get rid of slash

        trips["Day of year"] = trips["Departure (Local)"].dt.dayofyear
        trips.loc[
            ~trips["Departure (Local)"].dt.is_leap_year
            & (trips["Departure (Local)"].dt.dayofyear >= 60),
            "Day of year",
        ] += 1

        return trips

    def _import_additional_spending(
        self, datasheet_id: str, additional_spending_id: str
    ) -> pd.DataFrame:
        # Get trips dataset and save to file
        r = get(
            f"https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&gid={additional_spending_id}&output=csv"
        )
        with open(self._ADDITIONAL_SPENDING_PATH, "wb") as f:
            f.write(r.content)
        additional_spending = pd.read_csv(
            self._ADDITIONAL_SPENDING_PATH, header=0, skiprows=[1]
        )

        # Rework dataframe
        additional_spending["Purchase date"] = pd.to_datetime(
            additional_spending["Purchase date"], format="%Y-%m-%d"
        )
        additional_spending["Valid date (start)"] = pd.to_datetime(
            additional_spending["Valid date (start)"], format="%Y-%m-%d"
        )
        additional_spending["Valid date (end)"] = pd.to_datetime(
            additional_spending["Valid date (end)"], format="%Y-%m-%d"
        )

        # Split each spending into one row per year
        ids = []
        years = []
        operators = []
        amounts = []

        for index, row in additional_spending.iterrows():
            start_date = row["Valid date (start)"]
            end_date = row["Valid date (end)"]
            price = float(row["Price"].replace("€", ""))
            if start_date.year == end_date.year:
                years.append(start_date.year)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price)
            elif end_date.year - start_date.year == 1:
                timedelta_first_year = datetime(start_date.year, 12, 31) - start_date
                timedelta_full = end_date - start_date
                price_on_first_year = (
                    price * timedelta_first_year.days / timedelta_full.days
                )
                price_on_second_year = price - price_on_first_year

                years.append(start_date.year)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price_on_first_year)

                years.append(end_date.year)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price_on_second_year)
            elif end_date.year - start_date.year == 2:
                timedelta_full = end_date - start_date
                timedelta_first_year = datetime(start_date.year, 12, 31) - start_date
                price_on_first_year = (
                    price * timedelta_first_year.days / timedelta_full.days
                )
                timedelta_third_year = end_date - datetime(end_date.year, 1, 1)
                price_on_third_year = (
                    price * timedelta_third_year.days / timedelta_full.days
                )
                price_on_second_year = price - price_on_first_year - price_on_third_year

                years.append(start_date.year)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price_on_first_year)

                years.append(start_date.year + 1)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price_on_second_year)

                years.append(end_date.year)
                operators.append(row["Operator"])
                ids.append(row["ID"])
                amounts.append(price_on_third_year)

            elif end_date.year - start_date.year > 2:
                raise ValueError(f"Spending {row['Ticket']} is over more than 3 years")

        return pd.DataFrame({"Year": years, "Operator": operators, "Amount": amounts, "ID": ids})

    def _import_plots_config(
        self, datasheet_id: str, plots_config_id: str
    ) -> pd.DataFrame:
        # Get trips dataset and save to file
        r = get(
            f"https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&gid={plots_config_id}&output=csv"
        )
        with open(self._PLOTS_CONFIG_PATH, "wb") as f:
            f.write(r.content)
        plots_config_df = pd.read_csv(self._PLOTS_CONFIG_PATH, header=0)
        plots_config_df.dropna(axis=0, how="all", inplace=True)
        plots_config_df["Zoom level"] = plots_config_df["Zoom level"].astype("Int64")
        plots_config_df.replace({np.nan: None}, inplace=True)
        return plots_config_df
