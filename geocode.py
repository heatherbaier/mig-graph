from shapely.geometry import Point, LineString
from geopy.geocoders import Nominatim
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely import wkt
import pandas as pd
import numpy as np
import shapely
import random
import folium 
import os


def get_coordinates(city_list, country):
    """Takes a list of cities and returns a dictionary of the cities and their corresponding coordinates."""
    geolocator = Nominatim(user_agent="location script")
    dicto = {}
    
    for city in city_list:
        try:
            location = geolocator.geocode(city + ", " + country)
            coordinate_values = (location.longitude, location.latitude)
        except Exception as e:
            dicto[city] = "Fail"
            
    return dicto
    
    
    
country_names = {"MEX": "Mexico", "NIC": "Nicaragua", "GTM": "Guatemala", "SLV": "El Salvador"}
    
for file in os.listdir("flows"):
    
    print(file)
    
    if ".ipynb" not in file:

        origin_country_iso3c = file[0:3]
        origin_country_name = country_names[file[0:3]]
        
        flows = pd.read_csv("./flows/" + file)

        cross_coords = get_coordinates(flows['cross_loc'].unique(), "Mexico")
        print("cross done")
        origin_coords = get_coordinates(flows['origin_loc'].unique(), origin_country_name)
        print("origin done")
        us_coords = get_coordinates(flows['us_loc'].unique(), "United States")
        print("us done")    
        
        print(cross_coords)

        flows['origin_coords'] = flows['origin_loc'].map(origin_coords)
        flows['cross_coords'] = flows['cross_loc'].map(cross_coords)
        flows['us_coords'] = flows['us_loc'].str.replace("PMSA", "").str.replace("MSA", "").map(us_coords)

        flows.to_csv("./geocoded_flows/" + origin_country_iso3c + "_flows.csv", index = False)
        
        flow_lines = []
        for col, row in flows.iterrows():

            try:

                origin_coords = str(row.origin_coords)
                cross_coords = str(row.cross_coords)
                us_coords = str(row.us_coords)
                
                origin_lat = float(origin_coords.split(", ")[0].replace("(", ""))
                origin_lon = float(origin_coords.split(", ")[1].replace(")", ""))

                cross_lat = float(cross_coords.split(", ")[0].replace("(", ""))
                cross_lon = float(cross_coords.split(", ")[1].replace(")", ""))

                us_lat = float(us_coords.split(", ")[0].replace("(", ""))
                us_lon = float(us_coords.split(", ")[1].replace(")", ""))    

                flow_lines.append(shapely.geometry.LineString([(origin_lat, origin_lon), (cross_lat, cross_lon), (us_lat, us_lon)]))

            except Exception as e:

                flow_lines.append(np.nan)

        flows['flow'] = flow_lines
        flows = flows[flows["crsyr"] != 9999]
        flows = flows.dropna(subset = ['flow'])
        flows.to_csv("./geocoded_flows/" + origin_country_iso3c + "_flows.csv", index = False)
