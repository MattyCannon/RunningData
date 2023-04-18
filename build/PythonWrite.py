import requests
import logging
import urllib3
import os
from py_dotenv import dotenv
import pandas as pd

def writeToApi(w_param):
    dotenv.read_dotenv("C:\\Users\\MatthewCannon\\PycharmProjects\\strava\\.env.txt")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    auth_url = "https://www.strava.com/oauth/token"
    activities_url = "https://www.strava.com/api/v3/athlete/activities"

    #w_param = {"name": "PyRun2", "sport_type": "Run", "start_date_local": '2023-02-17T10:02:13Z', "elapsed_time": 9999, "distance": 100}
    #                 {"name": "PyRun", "sport_type": "Run", "start_date_local": '2023-02-16T18:02:13Z', "elapsed_time": 9999,
    #                  "distance": 100, "private": True}]

    ## DEBUG ##
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

    keyList = ["client_id", "client_secret", "refresh_token", "grant_type", "f"]
    valList = [os.environ.get("client_id"), os.environ.get("client_secret"), os.environ.get("refresh_token_write"),
               "refresh_token", "json"]
    payload = dict(list(zip(keyList, valList)))
    res = requests.post(auth_url, data=payload, verify=False)
    access_token = res.json()['access_token']
    header_write = {'Authorization': 'Bearer ' + access_token}
    print(header_write)
    print(w_param)
    #requests.post("https://www.strava.com/api/v3/activities", headers=header_write, params=w_param)
writeToApi(1)
