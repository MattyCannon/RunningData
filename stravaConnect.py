
import requests
#import logging
import urllib3
import os
#from dotenv import dotenv
import pandas as pd
import openpyxl
import streamlit as st

#dotenv.read_dotenv("C:\\Users\\MatthewCannon\\PycharmProjects\\strava\\.env.txt")
api_call_count = 0

def get_auth():
    global api_call_count
    #print("Requesting Token...\n")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    auth_url = "https://www.strava.com/oauth/token"
    keyList = ["client_id", "client_secret", "refresh_token", "grant_type", "f"]
    #valList = [os.environ.get("client_id"), os.environ.get("client_secret"), os.environ.get("refresh_token_read"),
    #           "refresh_token", "json"]
    valList = [st.secrets["client_id"], st.secrets["client_secret"], st.secrets["refresh_token_read"],
    "refresh_token", "json"]
    payload = dict(list(zip(keyList, valList)))
    res = requests.post(auth_url, data=payload, verify=False)
    api_call_count += 1
    print('call count: ' + str(api_call_count))
    #print(res.json())
    access_token_read = res.json()['access_token']
    #print("Access Token = {}\n".format(access_token_read))
    return access_token_read

def get_fromAPI(access_token, api):
    global api_call_count
    activities_url = f"https://www.strava.com/api/v3/{api}"
    header_read = {'Authorization': 'Bearer ' + access_token}
    param = {'per_page': 200, 'page': 1}
    my_dataset = requests.get(activities_url, headers=header_read, params=param).json()
    api_call_count += 1
    print('call count: ' + str(api_call_count))
    df = pd.json_normalize(my_dataset)
    # nonStrava = df[df["manual"]]    # needed for altering the nonStrava heartrate / elevation data. Don't need to run.
    # nonStrava.to_excel("Non_Strava.xlsx")
    return df


df_activities = get_fromAPI(get_auth(), "activities")
#df_athlete = get_fromAPI(get_auth(), "athlete")  # needs to be normalised
#df_shoes = df_athlete.filter(items=["id", "shoes"]).rename(columns={"id": "athleteId"})
#df_bikes = df_athlete.filter(items=["id", "bikes"]).rename(columns={"id": "athleteId"})
#df_clubs = df_athlete.filter(items=["id", "clubs"]).rename(columns={"id": "athleteId"})

# df_shoesNormal = (pd.concat({i: pd.json_normalize(x) for i, x in df_shoes.pop('shoes').items()})
#          .reset_index(level=1, drop=True)
#          .join(df_shoes)
#          .reset_index(drop=True))
# df_bikesNormal = (pd.concat({i: pd.json_normalize(x) for i, x in df_bikes.pop('bikes').items()})
#          .reset_index(level=1, drop=True)
#          .join(df_bikes)
#          .reset_index(drop=True))
# df_clubsNormal = (pd.concat({i: pd.json_normalize(x) for i, x in df_clubs.pop('clubs').items()})
#          .reset_index(level=1, drop=True)
#          .join(df_clubs)
#          .reset_index(drop=True))

## segments -- extracts all segment data for Strava recorded activities. ##
## To do: extract achievements from the final df_segmentNormal data frame. ##

def singleActivities(load_type = 0):
    '''
    load_type: 0 = incremental, 1 = full.
    '''
    global api_call_count
    manual_filter = df_activities[df_activities["manual"] == False]
    df_existing = pd.read_excel('single_out.xlsx')
    if load_type == 0:
        print(df_existing[df_existing['start_date_local'].notnull()])
        last_date = max(df_existing[df_existing['start_date_local'].notnull()])
        print(last_date)
        activities = [i for i in manual_filter[manual_filter["start_date_local"] > last_date]["id"]]
    else:
        activities = [i for i in manual_filter["id"]]
    if activities:
        for count, activity_id in enumerate(activities):
            api_call_count += 1
            print('call count: ' + str(api_call_count))
            df_activity_single = get_fromAPI(get_auth(), f'activities/{activity_id}')
            if count == 0:
                df_singleNormal = df_activity_single
            else:
                df_singleNormal = pd.concat([df_singleNormal, df_activity_single])
    else:
        return df_existing

    if load_type == 0:
        return pd.concat([df_singleNormal, df_existing])
    else:
        return df_singleNormal

def splitsOrSegments(strata, load_type = 0):
    '''
    strata: segment_efforts, splits_metric, splits_standard
    load_type: 0 = incremental, 1 = full.
    '''
    global api_call_count
    manual_filter = df_activities[df_activities["manual"] == False]
    activities = [i for i in manual_filter["id"]]
    df_existing = pd.read_excel('splits_out.xlsx')
    if load_type == 0:
        existing_activities = [i for i in df_existing["id"]]
        activities = list(set(existing_activities) - set(activities))
    if activities:
        for count, activity_id in enumerate(activities):
            api_call_count += 1
            print('call count: ' + str(api_call_count))
            df_activity_single = get_fromAPI(get_auth(), f'activities/{activity_id}')
            df_activity_single_strata = df_activity_single.filter(items=["name", "id", strata]) \
               .rename({"id": "activityId"})
            #try:
            df_single_strataNormal = \
                pd.concat({i: pd.json_normalize(x) for i, x in df_activity_single_strata.pop(strata).items()})\
                .reset_index(level=1, drop=True).join(df_activity_single_strata, lsuffix=('_'+strata)).reset_index(drop=True)
            if count == 0:
                df_strataNormal = df_single_strataNormal
            else:
                df_strataNormal = pd.concat([df_strataNormal, df_single_strataNormal])
            # except KeyError as e:
            #     print(e)
        if load_type == 0:
            return pd.concat([df_existing, df_strataNormal])
        return df_strataNormal
    else:
        return df_existing

#df_splits = splitsOrSegments('splits_metric', load_type=1)
#df_singles = singleActivities(load_type=0)

#df_singles.to_excel('single_out.xlsx')
#df_splits.to_excel('splits_out.xlsx')

## Map polyline stuff ##

def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates

#df_activities["map_polyline_coords"] = df_activities["map.summary_polyline"].apply(decode_polyline)
#df_activities.to_excel('LatLong.xlsx')
#df = df.set_index(['id', "map.summary_polyline"]).explode("map_polyline_coords").reset_index()
#print(df["map_polyline_coords"])
#df2 = df[df['map_polyline_coords'].notnull()]
#df2['latitude'], df2['longitude'] = zip(*(df2["map_polyline_coords"]))
#print(df2)

st.header('Test')
st.table(df_activities)
