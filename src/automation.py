from processing import process_data
from plotsCodes.all_europe import plot_all_europe

if __name__ == "__main__":
    
    trips, journeys = process_data()

    plot_all_europe(trips, journeys)
    exit(code=0)
