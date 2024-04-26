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
    stations = pd.read_csv(STATIONS_PATH, header=0)
    for index, row in trips.iterrows():
        # Get origin/destination timezones
        origin = row["Origin"]
        destination = row["Destination"]

        origin_data = stations[stations["name"] == origin]
        if origin_data:
            trips.iloc[index]["Departure (Local)"] = trips.iloc[index]["Departure (Local)"].dt.tz_localize(pytz.timezone(origin_data["time_zone"]))
        else:
            print(f"[{origin}] from logbook not found in stations.csv")

        destination_data = stations[stations["name"] == destination]
        if destination_data:
            trips.iloc[index]["Arrival (Local)"] = trips.iloc[index]["Arrival (Local)"].dt.tz_localize(pytz.timezone(destination_data["time_zone"]))
        else:
            print(f"[{destination}] from logbook not found in stations.csv")

    return trips
