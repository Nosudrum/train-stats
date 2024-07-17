import pandas as pd
import requests
from utils import get_datasheet_id, DATASET_PATH, STATIONS_PATH, CUSTOM_STATIONS_PATH
import pytz

# Import stations CSV
STATIONS = pd.read_csv(STATIONS_PATH, sep=';', low_memory=False)
CUSTOM_STATIONS = pd.read_csv(CUSTOM_STATIONS_PATH, sep=',')


def get_station_timezone(name):
    custom_tz = CUSTOM_STATIONS.loc[CUSTOM_STATIONS["name"] == name, "time_zone"].head(1)
    if not custom_tz.empty:
        return pytz.timezone(custom_tz.item())
    stations_tz = STATIONS.loc[STATIONS["name"] == name, "time_zone"].head(1)
    if not stations_tz.empty:
        return pytz.timezone(stations_tz.item())
    else:
        raise ValueError(f"Could not find station name [{name}] in either standard or custom station CSVs.")


def process_data():
    datasheet_id = get_datasheet_id()

    # Get dataset and save to file
    r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&output=csv')
    with open(DATASET_PATH, 'wb') as f:
        f.write(r.content)
    trips = pd.read_csv(DATASET_PATH, header=0, skiprows=[1])

    # Rework dataframe
    trips = trips.rename(columns={"Alphabetical trip": "journey"})
    trips.dropna(inplace=True, subset=["Departure (Local)"])
    trips["Departure (Local)"] = pd.to_datetime(trips["Departure (Local)"], format="mixed")
    trips["Arrival (Local)"] = pd.to_datetime(trips["Arrival (Local)"], format="mixed")

    # Localize departure and arrival times
    for index, row in trips.iterrows():
        origin = row["Origin"]
        trips.loc[index, "Departure (Local)"] = trips.loc[index, "Departure (Local)"].tz_localize(
            get_station_timezone(origin))
        destination = row["Destination"]
        trips.loc[index, "Arrival (Local)"] = trips.loc[index, "Arrival (Local)"].tz_localize(
            get_station_timezone(destination))
    trips["Departure (Local)"] = pd.to_datetime(trips["Departure (Local)"], utc=True)
    trips["Arrival (Local)"] = pd.to_datetime(trips["Arrival (Local)"], utc=True)
    
    # Format durations
    trips["Duration"] = pd.to_timedelta((trips["Duration"].str.split(':', expand=True).astype(int) * (60, 1)).sum(axis=1), unit='min')

    # Replace special things
    trips.replace('\xa0', ' ', regex=True, inplace=True)  # Remove non-breaking spaces
    trips.replace("Biel/Bienne", "BielBienne", regex=True, inplace=True)  # Get rid of slash

    return trips
