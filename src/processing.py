import pandas as pd
import requests
from utils import get_datasheet_id, DATASET_PATH


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
    
    return trips
