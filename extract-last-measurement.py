#!/bin/python
# -*- coding: utf-8 -*-
from asyncio.windows_events import NULL
from datetime import datetime
import json
import pprint
import requests

DEFAULT_SETTINGS_FILE_PATH = "settings.json"

auth_token = ""
user_id = ""


def loads_settings(settings_file_path):
    print("Reading settings from file '{}'".format(settings_file_path))
    with open(settings_file_path, "r") as jfp:
        return json.load(jfp)

def login():
    global auth_token
    global user_id
    login_body = {}
    login_body['email'] = settings["email"]
    login_body['password'] = settings["password"]
    response = requests.post(
        "{}/llu/auth/login".format(settings["api_endpoint"]),
        headers={
            "content-type": "application/json",
            "product": "llu.android",
            "version": "4.2.1"
            },
        data=json.dumps(login_body)
    )
    response_json = response.json()
    auth_token = response_json['data']['authTicket']['token']
    user_id = response_json['data']['user']['id']

#   TODO if you're not self-following your data:
# def get_connections(settings):
#    response = requests.get(
#        "{}/lli/connections".format(settings["api_endpoint"]),
#        headers={
#            "Authorization": "Bearer {}".format(settings["api_token"]),
#            "product": "llu.android",
#            "version": "4.2.1"
#        }
#    )

def get_user_graph():
    response = requests.get(
        "{}/llu/connections/{}/graph".format(settings["api_endpoint"], user_id),
        headers={
            "Authorization": "Bearer {}".format(auth_token),
            "product": "llu.android",
            "version": "4.2.1"
        }
    )
    return response.json()

def get_latest_data():
    user_graph_data = get_user_graph()['data']
    latest_glucose_measurement = user_graph_data['connection']['glucoseMeasurement']
    latest_graph_data = user_graph_data['graphData'][-1]
    measurement_timestamp = datetime.strptime(latest_glucose_measurement['Timestamp'], "%m/%d/%Y %I:%M:%S %p")
    graph_timestamp = datetime.strptime(latest_graph_data['Timestamp'], "%m/%d/%Y %I:%M:%S %p")
    if measurement_timestamp > graph_timestamp :
        return latest_glucose_measurement
    else:
        return latest_graph_data


if __name__ == "__main__":
    global settings
    settings = loads_settings(DEFAULT_SETTINGS_FILE_PATH)
    output_json_file_path = "export-output.json"

    if auth_token == "" or user_id == "":
        login()
    
    data = get_latest_data()
    with open(output_json_file_path, "w") as ef:
        json.dump(data, ef)
        print("Written LibreLink data to {}".format(output_json_file_path))