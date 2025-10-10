#!/bin/python
# -*- coding: utf-8 -*-
from hashlib import sha256
from flask import Flask
from flask_cors import CORS
from datetime import datetime
from bs4 import BeautifulSoup
import json
import requests
import asyncio
import aiohttp

#NOTA Builds with command: pyinstaller --onefile --add-data "settings.json;json" extract-last-measurement.py

DEFAULT_SETTINGS_FILE_PATH = "settings.json"

auth_token = ""
user_id = ""
account_id = ""
version = "4.16.0"

data = {}
data_history = list()

app = Flask(__name__)
CORS(app)


def loads_settings(settings_file_path):
    print("Reading settings from file '{}'".format(settings_file_path))
    with open(settings_file_path, "r") as jfp:
        return json.load(jfp)


settings = loads_settings(DEFAULT_SETTINGS_FILE_PATH)


def login():
    global auth_token
    global user_id
    global account_id
    login_body = {}
    login_body["email"] = settings["email"]
    login_body["password"] = settings["password"]
    response = requests.post(
        "{}/llu/auth/login".format(settings["api_endpoint"]),
        headers={
            "accept-encoding": "gzip",
            "cache-control": "no-cache",
            "Connection": "Keep-Alive",
            "content-type": "application/json",
            "product": "llu.android",
            "version": version,
        },
        data=json.dumps(login_body),
    )
    response_json = response.json()
    print(response_json)
    auth_token = response_json["data"]["authTicket"]["token"]
    user_id = response_json["data"]["user"]["id"]
    account_id = response_json["data"]["user"]["id"]


#   TODO if you're not self-following your data:
# def get_connections(settings):
#    response = requests.get(
#        "{}/lli/connections".format(settings["api_endpoint"]),
#        headers={
#            "Authorization": "Bearer {}".format(settings["api_token"]),
#            "product": "llu.android",
#            "version": version
#        }
#    )


def get_user_graph():
    global user_id
    global account_id
    print(user_id)
    response = requests.get(
        "{}/llu/connections/{}/graph".format(settings["api_endpoint"], user_id),
        headers={
            "Authorization": "Bearer {}".format(auth_token),
            "accept-encoding": "gzip",
            "cache-control": "no-cache",
            "Connection": "Keep-Alive",
            "content-type": "application/json",
            "product": "llu.android",
            "version": version,
            "account-id": sha256(account_id.encode('utf-8')).hexdigest(),
        },
    )
    print(response.json())
    return response.json()

def update_data():
    global data
    print(get_user_graph()["data"])
    latest_glucose_measurement = get_user_graph()["data"]["connection"]["glucoseMeasurement"]
    latest_glucose_measurement["Timestamp"] = datetime.strptime(
        latest_glucose_measurement["Timestamp"], "%m/%d/%Y %I:%M:%S %p"
    )
    if len(data) == 0 or data["Timestamp"] < latest_glucose_measurement["Timestamp"]:
        data = latest_glucose_measurement
        data["MeasurementColor"] = get_color_by_value(data["MeasurementColor"])
        data["TrendArrow"] = get_angle_by_value(data["TrendArrow"])
        data["DataHistory"] = update_data_history(data["Value"])

def update_data_history(value):
    global data_history
    data_history.append(value)
    if len(data_history) > 60:
        data_history.pop(0)
    return data_history

def get_color_by_value(color):
    if color is None:
        return "silver"
    match color:
        case 1:
            return "#10b981"
        case 2:
            return "#f59e0b"
        case 3:
            return "#f5610b"
        case 4:
            return "#ef4444"
        case _:
            return "#64748b"

def get_angle_by_value(trend):
    if trend is None:
        return 0
    match trend:
        case 1:
            return 90
        case 2:
            return 45
        case 3:
            return 0
        case 4:
            return -45
        case 5:
            return -90
        case _:
            return 0

async def async_test():
    global user_id
    data_url = "{}/llu/connections/{}/graph".format(settings["api_endpoint"], user_id)
    headers={
            "Authorization": "Bearer {}".format(auth_token),
            "accept-encoding": "gzip",
            "cache-control": "no-cache",
            "Connection": "Keep-Alive",
            "content-type": "application/json",
            "product": "llu.android",
            "version": version,
            "account-id": sha256(account_id.encode('utf-8')).hexdigest(),
        }
    while True:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(data_url) as response:
                user_graph = await response.json()
        await asyncio.sleep(60)

async def update_data_loop():
    global data
    loop = asyncio.get_event_loop()
    while True:
        await loop.run_in_executor(None, update_data())
        await asyncio.sleep(60)


@app.route("/latestglucose")
def getLatestGlucose():
    if auth_token == "" or user_id == "":
        login()
    update_data()
    return data

#@app.route("/graph")
#def getLineGraph():
#    with open("./graph.html") as fp:
#        soup = BeautifulSoup(fp, 'html.parser')
#    if auth_token == "" or user_id == "":
#        login()
#    update_data()
#    return str(soup.prettify())

@app.route("/")
def start():
    with open("./index.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    if auth_token == "" or user_id == "":
        login()
    update_data()
    return str(soup.prettify())


# da rimuovere su vero server
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=1337, debug=True)
