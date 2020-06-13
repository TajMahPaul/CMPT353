import pandas as pd
import sys
import numpy as np
import matplotlib.pyplot as plt

def distance(city, stations):
 
    station_lats = np.deg2rad(stations['latitude'])
    station_lons = np.deg2rad(stations['longitude'])

    city_lat = np.deg2rad(city.latitude)
    city_lon = np.deg2rad(city.longitude)

    # haversine formula 
    dlon = station_lons - city_lon 
    dlat = station_lats - city_lat

    a = np.sin(dlat/2)**2 + np.cos(city_lat) * np.cos(station_lats) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371000 # Radius of earth in meters. Use 3956 for miles
    return c * r 
    
def best_tmax(city, stations):
    return stations.iloc[np.argmin(distance(city, stations))].avg_tmax

def main():
    assert len(sys.argv) == 4, "Wrong number of cli arguments. Usage: python3 average_ratings.py <movie_list_file> <rating_csv_file> <output_file_name>"

    stations_file_name = sys.argv[1]
    city_data_csv_file_name = sys.argv[2]
    output_svg_file_name = sys.argv[3]

    stations = pd.read_json(stations_file_name, lines=True)
    cities = pd.read_csv(city_data_csv_file_name)

    stations['avg_tmax'] = stations['avg_tmax'].map (lambda x: x/10)

    cities = cities[cities.area.notnull()]
    cities = cities[cities.population.notnull()]
    cities['area'] = cities['area'].map (lambda x: x/1000000)
    cities = cities[cities['area'] <= 10000]
    cities['pop_density'] =  cities.population / cities.area
    cities['best_tmax'] = cities.apply(best_tmax, stations=stations, axis=1)
    
    plt.scatter(cities['best_tmax'], cities['pop_density'])
    plt.title("Temperature vs. Population Density")
    plt.ylabel("Population Density (people/km\u00b2)")
    plt.xlabel("Avg Max Temperature (\u00b0C)")
    plt.savefig(output_svg_file_name)
if __name__ == '__main__':
    main()