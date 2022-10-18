#!/bin/python
# -*- coding: utf-8 -*-
from asyncio.windows_events import NULL
import json
import pprint
import requests

DEFAULT_SETTINGS_FILE_PATH = "settings.json"


def loads_settings(settings_file_path):
    print("Reading settings from file '{}'".format(settings_file_path))
    with open(settings_file_path, "r") as jfp:
        return json.load(jfp)

# def login(settings):
    # TODO Returns 501: Invalid request
    # https://api-eu.libreview.io/auth/login
#    auth_request_body = {}
#    auth_request_body['email'] = settings["email"]
#    auth_request_body['fingerprint'] = settings["fingerprint"]
#    auth_request_body['password'] = settings["password"]
#    response = requests.post(
#        "{}/auth/login".format(settings["api_endpoint"]),
#        json=json.dumps(auth_request_body)
#    )
#    response_json = json.loads(response.text)
#    return response_json

def read_data_from_libreview_api(settings):
    # TODO Get user settings: for device listing.
    # https://api-eu.libreview.io/user
    # Get Glucose history.
    # https://api-eu.libreview.io/glucoseHistory?numPeriods=5&period=14
    response = requests.get(
        "{}/glucoseHistory?numPeriods=5&period=7".format(settings["api_endpoint"]),
        headers={"Authorization": "Bearer {}".format(settings["api_token"])},
    )
    return response.json()

def get_report_settings(settings):
    # Get report settings.
    # https://api-eu.libreview.io/reportSettings
    response = requests.get(
        "{}/reportSettings".format(settings["api_endpoint"]),
        headers={"Authorization": "Bearer {}".format(settings["api_token"])},
    )
    return response

def set_report_settings(settings):
    # Set report settings.
    # https://api-eu.libreview.io/reports
    report_settings_response = get_report_settings(settings)
    report_settings = json.loads(report_settings_response.text)

    new_report_settings = {}
    new_report_settings['Country'] = 'IT'
    new_report_settings['CultureCode'] = 'it-IT'
    new_report_settings['CultureCodeCommunication'] = 'it-IT'
    new_report_settings['DateFormat'] = 2
    new_report_settings['EndDate'] = report_settings['data']['endDate']
    new_report_settings['GlucoseUnits'] = 1
    new_report_settings['HighGlucoseThreshold'] = report_settings['data']['settings']['highThreshold']
    new_report_settings['LowGlucoseThreshold'] = report_settings['data']['settings']['lowThreshold']
    data_sources = report_settings['data']['dataSources']
    for data_source in data_sources:
        primaryDevice = data_source
    new_report_settings['PrimaryDeviceId'] = report_settings['data']['dataSources'][primaryDevice]['id']
    new_report_settings['PrimaryDeviceTypeId'] = report_settings['data']['dataSources'][primaryDevice]['type']
    new_report_settings['PrintReportsWithPatientInformation'] = report_settings['data']['settings']['includePatientInfo']
    new_report_settings['ReportIds'] = list({
        500000 + report_settings['data']['dataSources'][primaryDevice]['type']
        })
    new_report_settings['SecondaryDeviceIds'] = list({})
    new_report_settings['TertiaryDeviceIds'] = list({})
    new_report_settings['ConnectedInsulinDeviceIds'] = list({})
    new_report_settings['StartDates'] = list({
        report_settings['data']['endDate'] - 86400
        })
    new_report_settings['TargetRangeHigh'] = report_settings['data']['settings']['targetRange']['max']
    new_report_settings['TargetRangeLow'] = report_settings['data']['settings']['targetRange']['min']
    new_report_settings['TimeFormat'] = 2
    new_report_settings['TodayDate'] = report_settings['data']['endDate']
    new_report_settings['PatientDateOfBirth'] = settings["PatientDateOfBirth"]
    new_report_settings['PatientFirstName'] = settings["PatientFirstName"]
    new_report_settings['PatientId'] = settings["PatientId"]
    new_report_settings['PatientLastName'] = settings["PatientLastName"]
    new_report_settings['ClientReportIDs'] = list({
        5
        })
    report_settings_body = json.dumps(new_report_settings)
    print(report_settings_body)

    response = requests.post(
        "{}/reports".format(settings["api_endpoint"]),
        headers={"Authorization": "Bearer {}".format(settings["api_token"])},
        json=json.dumps(new_report_settings)
    )
    return response.json()

def read_data_from_report(settings):
    # Get data from settings.
    # url: [response url, esempio https://hub-eu.libreview.io/channel/4da136f4-9801-4cfd-b57a-c82269ce5e1d]
    return NULL


if __name__ == "__main__":
    settings = loads_settings(DEFAULT_SETTINGS_FILE_PATH)
#    pprint.pprint(login(settings))
    report_settings = get_report_settings(settings).json()
    pprint.pprint(report_settings)
    data = set_report_settings(settings)
#    data = read_data_from_libreview_api(settings)
    pprint.pprint(data)
    output_json_file_path = "export-output.json"
    with open(output_json_file_path, "w") as ef:
        json.dump(data, ef)
        print("Written LibreView data to {}".format(output_json_file_path))


# CSV export.
# https://api-fr.libreview.io/export
# {"captchaResponse":"XXX","type":"glucose"}
# {"status":0,"data":{"url":"https://hub-fr.libreview.io/channel/XXX"},"ticket":{"token":"XXX","expires":1586543766}}