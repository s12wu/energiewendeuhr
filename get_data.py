#!/usr/bin/env python

import requests, json, os

import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import date, timedelta

from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

def get_stromgedacht_data():
    today = date.today()
    tomorrow = today + timedelta(days=1)
    url = "https://api.stromgedacht.de/v1/forecast?zip=71332&from=" + today.strftime("%Y-%m-%d") + "&to=" + tomorrow.strftime("%Y-%m-%d")
    print(url)
    
    response = requests.get(url)
    content = json.loads(response.text)

    # timestamps are encoded like 2023-09-17T06:30:00Z (ISO 8601), InfluxDB understands that as well
    timestamp = [entry["dateTime"] for entry in content["load"]] # should be the same for all categories

    load = [entry["value"] for entry in content["load"]]
    renewableEnergy = [entry["value"] for entry in content["renewableEnergy"]]

    renewableFraction = [ren/l for ren, l in zip(renewableEnergy, load)]
    
    return timestamp, renewableFraction

def get_record_points():
    points = []
    
    timestamp, renewableFraction = get_stromgedacht_data()

    for t, r in zip(timestamp, renewableFraction):
        points.append(Point("renewableFraction").field("fraction", r).time(t))
    
    return points
    

token = os.getenv("DB_TOKEN")
org = "energiewendeuhr"
url = "http://127.0.0.1:8086"
bucket="energiewendeuhr"

write_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = write_client.write_api(write_options=SYNCHRONOUS)

write_api.write(bucket=bucket, org=org, record=get_record_points())

