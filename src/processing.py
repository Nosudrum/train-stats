import pandas as pd
import requests
from utils import get_datasheet_id, DATASET_PATH, STATIONS_PATH
import pytz


def process_data():
    datasheet_id = get_datasheet_id()

    # Get dataset and save to file
    r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&output=csv')
    with open(DATASET_PATH, 'wb') as f:
        f.write(r.content)
    trips = pd.read_csv(DATASET_PATH, header=0, skiprows=[1])

    # Replace special things
    trips.replace('\xa0', ' ', regex=True, inplace=True)  # Remove non-breaking spaces
    trips.replace("Biel/Bienne", "BielBienne", regex=True, inplace=True)  # Get rid of slash

    # Rework dataframe
    trips = trips.rename(columns={"Alphabetical trip": "journey"})
    trips.dropna(inplace=True, subset=["Departure (Local)"])
    trips["Departure (Local)"] = pd.to_datetime(trips["Departure (Local)"], format="mixed")
    trips["Arrival (Local)"] = pd.to_datetime(trips["Arrival (Local)"], format="mixed")

    # Import stations CSV
    stations = pd.read_csv(STATIONS_PATH, sep=';', low_memory=False)
    for index, row in trips.iterrows():
        # Get origin/destination timezones
        origin = row["Origin"]
        destination = row["Destination"]

        origin_tz = stations.loc[stations["name"] == origin, "time_zone"]
        if not origin_tz.empty:
            trips.loc[index, "Departure (Local)"] = trips.loc[index, "Departure (Local)"].tz_localize(
                pytz.timezone(origin_tz.item()))
        else:
            print(f"[{origin}] from logbook not found in stations.csv")

        destination_tz = stations.loc[stations["name"] == destination, "time_zone"]
        if not destination_tz.empty:
            trips.loc[index, "Arrival (Local)"] = trips.loc[index, "Arrival (Local)"].tz_localize(
                pytz.timezone(destination_tz.item()))
        else:
            print(f"[{destination}] from logbook not found in stations.csv")

    return trips
