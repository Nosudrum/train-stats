import pandas as pd
import requests
from datetime import datetime

YOUR_SHEET_ID = "1_D1kQjm1KoyVXcmUTxerClQrp661OozyZrYYs5QUjbs"

r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={YOUR_SHEET_ID}&output=csv')
with open('../data/dataset.csv', 'wb') as f:
    f.write(r.content)
df = pd.read_csv('../data/dataset.csv', header=0, skiprows=[1])
df.replace('\xa0', ' ', regex=True, inplace=True)
df.replace("Biel/Bienne", "BielBienne", regex=True, inplace=True)
df = df.rename(columns={"Alphabetical trip": "journey"})
df.dropna(inplace=True, subset=["Departure (Local)"])
df["Departure (Local)"] = pd.to_datetime(df["Departure (Local)"], format="mixed")
df["Arrival (Local)"] = pd.to_datetime(df["Arrival (Local)"], format="mixed")

journey_counts = df["journey"].value_counts().to_frame()

journey_distances = df[["journey", "Distance (km)"]].groupby("journey").mean()

journey_firstdate = df[["journey", "Departure (Local)"]].groupby("journey").min()

journeys = journey_counts.join(journey_distances).join(journey_firstdate)

journeys.rename(columns={"Distance (km)": "distance", "Departure (Local)": "firstdate"}, inplace=True)
total_time = pd.to_timedelta(df[df["Arrival (Local)"] < datetime.now()]["Duration"].dropna()+":00").sum()
total_distance = df[df["Arrival (Local)"] < datetime.now()]["Distance (km)"].dropna().sum()
