#!/usr/bin/env python

import requests, json, os

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime

from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

"""
# Solar and wind symbols - using data from SMARD here.
// The SMARD data is for the whole of Germany, not just the local area, but we use it to roughly calculate whether the renewable share is wind or solar.
// We're using data points 125 - "Stromerzeugung - Prognostizierte Erzeugung Day-Ahead / Photovoltaik"
// and 5097 - "Stromerzeugung - Prognostizierte Erzeugung Day-Ahead / Photovoltaik und Wind"
// Biomass is ignored here.
// By substracting "Sun" from "Sun and Wind", we get the wind value.
// The proportion of sun and wind in the total is calculated ($sun/wind_fraction_of_renewable). For example 0.6 solar and 0.4 wind.

"""

response = requests.get("https://www.smard.de/app/chart_data/125/DE/index_quarterhour.json")
content = json.loads(response.text)
timestamp = content["timestamps"][-1]

response = requests.get(f"https://www.smard.de/app/chart_data/125/DE/125_DE_quarterhour_{timestamp}.json")
content = json.loads(response.text)
sun = content["series"]

# sun looks like this:
#[
#    [1745997300000,7027.5],
#    [1745998200000,7635.25],
#    [1745999100000,8192.25]
#]

response = requests.get(f"https://www.smard.de/app/chart_data/5097/DE/5097_DE_quarterhour_{timestamp}.json")
content = json.loads(response.text)
sun_and_wind = content["series"]

points = []

for sun_entry, sun_and_wind_entry in zip(sun, sun_and_wind):
    unixtime = sun_entry[0] // 1000 # millisecods to seconds
    
    ts = datetime.fromtimestamp(unixtime)
    print(ts.isoformat())
    
    sun_pwr = sun_entry[1]
    sun_and_wind_pwr = sun_and_wind_entry[1]
    
    if sun_pwr == None or sun_and_wind_pwr == None:
        #print("skipping bad point", unixtime)
        continue
    
    wind_pwr = sun_and_wind_pwr - sun_pwr;
    sun_fraction_of_renewable = sun_pwr / sun_and_wind_pwr;
    wind_fraction_of_renewable = wind_pwr / sun_and_wind_pwr;
    
    points.append(
        Point("sun_wind").field("sun_fraction_of_renewable", sun_fraction_of_renewable)
            .field("wind_fraction_of_renewable", wind_fraction_of_renewable)
            .time(ts.isoformat())
    )
    


token = os.getenv("DB_TOKEN")
org = "energiewendeuhr"
url = "http://127.0.0.1:8086"
bucket="energiewendeuhr"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

write_api.write(bucket=bucket, org=org, record=points)

