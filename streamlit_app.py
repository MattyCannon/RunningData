import pandas as pd
import matplotlib.pyplot as plt
import stravaConnect as sc
import streamlit as st
import math
import datetime
import numpy as np

df_activities = sc.get_fromAPI(sc.get_auth(), "activities")


def convert(seconds):
       seconds = seconds % (24 * 3600)
       hour = seconds // 3600
       seconds %= 3600
       minutes = seconds // 60
       seconds %= 60
       if hour != 0: return "%d:%02d:%02d" % (hour, minutes, seconds)
       else: return "%02d:%02d" % (minutes, seconds)
n=5
summary = df_activities.head(n)
summary['start_date'] = pd.to_datetime(summary['start_date']).dt.strftime('%d/%m/%Y')  # Convert start_date to datetime
summary['distance'] = summary['distance'].apply(lambda x: round((x/1000), 2)).astype(str)
pd.options.display.float_format = '${:,.2f}'.format
#summary['moving_time'] = np.floor(summary['moving_time']/60) #str(math.floor(summary['moving_time']/60)) #+ ':' + round(60*(summary['moving_time']/60 - math.floor(summary['moving_time']/60)), 2)
summary['moving_time'] = summary['moving_time'].apply(convert)
summary = summary.filter(items=['name', 'distance', 'moving_time', 'total_elevation_gain', 'start_date'])

today = datetime.datetime.now()
this_week_distance_col = df_activities[df_activities['start_date'] > str(pd.Timestamp(today + datetime.timedelta(days=-6)))]
this_week_dist = sum(this_week_distance_col['distance'])
weekly_goal = 10.0 * 1000
last_week_distance_col = df_activities[
       (df_activities['start_date'] > str(pd.Timestamp(today + datetime.timedelta(days=-13))))
       &
       (df_activities['start_date'] < str(pd.Timestamp(today + datetime.timedelta(days=-6))))
]
last_week_dist = sum(last_week_distance_col['distance'])
dist_difference = this_week_dist - last_week_dist

### CHART ###
fig, ax = plt.subplots()
labels = 'distance', 'hi'
proportion = last_week_dist/weekly_goal
if proportion > 1: proportion = 1
ax.pie([proportion, 1-proportion],
       colors=[(255/255, 84/255, 0), (255/255, 187/255, 153/255)],
       pctdistance=0.85,
       explode=(0.05, 0.05)
       )
# draw circle
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()

# Adding Circle in Pie chart
fig.gca().add_artist(centre_circle)
plt.title(f'This Week\'s distance:\n {last_week_dist}', x=0.5, y=0.45)
#plt.show()
#pd.options.display.max_columns = 10
#print(summary.dtypes)
#print(summary)

### DISPLAY ###
st.header('My Running Data')
st.header('Recent Runs: ')
st.table(summary)
st.pyplot(fig)

