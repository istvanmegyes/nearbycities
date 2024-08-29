import math
from flask import Flask, render_template
import pandas as pd
import config

def get_cites_data_frame():
    df = pd.read_csv(config.file_to_read, usecols=['city', 'state_id', 'lat', 'lng'], nrows=config.limit_rows)
    df['city_name'] = df['city'] + ', ' + df['state_id']
    df = df[['city_name', 'lat', 'lng']]
    
    return df

# Haversine formula
def get_cities_haversine_distance(latitude1, longitude1, latitude2, longitude2): 
    return config.earth_radius * math.acos(
        math.sin(latitude1) * 
        math.sin(latitude2) +
        math.cos(latitude1) * 
        math.cos(latitude2) * 
        math.cos(longitude2 - longitude1)
    );

def find_nearby_cities(df):
    cities = {}

    for i, row in df.iterrows():
        city_lat = math.radians(row['lat'])
        city_lon = math.radians(row['lng'])
        cities_nearby = []
    
        for j in range(i + 1, len(df)):
            compared_city_row = df.iloc[j]
            compared_city_lat = math.radians(compared_city_row['lat'])
            compared_city_lon = math.radians(compared_city_row['lng'])
            
            distance = get_cities_haversine_distance(
                city_lat,
                city_lon,
                compared_city_lat,
                compared_city_lon
            )
            
            if distance <= config.city_radius:
                cities_nearby.append(compared_city_row['city_name'])
                
                if compared_city_row['city_name'] in cities:
                    cities[compared_city_row['city_name']].append(row['city_name'])
                else:
                    cities[compared_city_row['city_name']] = [row['city_name']]
                    
        cities[row['city_name']] = cities_nearby

    return cities

app = Flask(__name__)

@app.route("/")
def main():
    df = get_cites_data_frame()
    result = find_nearby_cities(df)
    
    return render_template('index.html', result=result)