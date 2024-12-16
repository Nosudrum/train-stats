from datetime import datetime

import pandas as pd
import requests
from utils import (
    get_datasheet_id,
    TRIPS_PATH,
    STATIONS_PATH,
    CUSTOM_STATIONS_PATH,
    get_additional_spending_id,
    ADDITIONAL_SPENDING_PATH,
)
import pytz

# Import stations CSV
STATIONS = pd.read_csv(STATIONS_PATH, sep=";", low_memory=False)
CUSTOM_STATIONS = pd.read_csv(CUSTOM_STATIONS_PATH, sep=",")


def get_station_timezone(name):
    custom_tz = CUSTOM_STATIONS.loc[CUSTOM_STATIONS["name"] == name, "time_zone"].head(
        1
    )
    if not custom_tz.empty:
        return pytz.timezone(custom_tz.item())
    stations_tz = STATIONS.loc[STATIONS["name"] == name, "time_zone"].head(1)
    if not stations_tz.empty:
        return pytz.timezone(stations_tz.item())
    else:
        raise ValueError(
            f"Could not find station name [{name}] in either standard or custom station CSVs."
        )


def process_trips():
    datasheet_id = get_datasheet_id()

    # Get trips dataset and save to file
    r = requests.get(
        f"https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&output=csv"
    )
    with open(TRIPS_PATH, "wb") as f:
        f.write(r.content)
    trips = pd.read_csv(TRIPS_PATH, header=0, skiprows=[1])

    # Rework dataframe
    trips = trips.rename(columns={"Alphabetical trip": "journey"})
    trips.dropna(inplace=True, subset=["Departure (Local)"])
    trips["Departure (Local)"] = pd.to_datetime(
        trips["Departure (Local)"], format="mixed"
    )
    trips["Arrival (Local)"] = pd.to_datetime(trips["Arrival (Local)"], format="mixed")

    # Localize departure and arrival times
    for index, row in trips.iterrows():
        origin = row["Origin"]
        trips.loc[index, "Departure (Local)"] = trips.loc[
            index, "Departure (Local)"
        ].tz_localize(get_station_timezone(origin))
        destination = row["Destination"]
        trips.loc[index, "Arrival (Local)"] = trips.loc[
            index, "Arrival (Local)"
        ].tz_localize(get_station_timezone(destination))
    trips["Departure (Local)"] = pd.to_datetime(trips["Departure (Local)"], utc=True)
    trips["Arrival (Local)"] = pd.to_datetime(trips["Arrival (Local)"], utc=True)

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
    trips.replace("\xa0", " ", regex=True, inplace=True)  # Remove non-breaking spaces
    trips.replace(
        "Biel/Bienne", "BielBienne", regex=True, inplace=True
    )  # Get rid of slash

    trips["Day of year"] = trips["Departure (Local)"].dt.dayofyear
    trips.loc[
        ~trips["Departure (Local)"].dt.is_leap_year
        & (trips["Departure (Local)"].dt.dayofyear < 60),
        "Day of year",
    ] += 1

    return trips


def process_additional_spending():
    datasheet_id = get_datasheet_id()
    additional_spending_id = get_additional_spending_id()

    # Get trips dataset and save to file
    r = requests.get(
        f"https://docs.google.com/spreadsheet/ccc?key={datasheet_id}&gid={additional_spending_id}&output=csv"
    )
    with open(ADDITIONAL_SPENDING_PATH, "wb") as f:
        f.write(r.content)
    additional_spending = pd.read_csv(ADDITIONAL_SPENDING_PATH, header=0, skiprows=[1])

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
            amounts.append(price_on_first_year)

            years.append(end_date.year)
            operators.append(row["Operator"])
            amounts.append(price_on_second_year)
        elif end_date.year - start_date.year > 1:
            raise ValueError(f"Spending {row['Ticket']} is over more than 2 years")

    return pd.DataFrame({"Year": years, "Operator": operators, "Amount": amounts})
