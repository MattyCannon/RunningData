import pandas as pd
import matplotlib.pyplot as plt
import stravaConnect as sc
import streamlit as st
import datetime
df_activities = sc.get_fromAPI(sc.get_auth(), "activities")

summary = df_activities.head()
summary['start_date'] = pd.to_datetime(summary['start_date'])  # Convert start_date to datetime
summary['distance'] = '%2f'.format(summary['distance']/1000)
today = datetime.datetime.now()
last_week_distance_col = df_activities[df_activities['start_date'] > str(pd.Timestamp(today + datetime.timedelta(days=-6)))]
last_week_dist = sum(last_week_distance_col['distance'])
weekly_goal = 10.0 * 1000
fig, ax = plt.subplots()
labels = 'distance', 'hi'
ax.pie([last_week_dist/weekly_goal, 1-last_week_dist/weekly_goal],
       colors=[(255/255, 84/255, 0), (255/255, 187/255, 153/255)],
       pctdistance=0.85,
       explode=(0.05, 0.05)
       )
# draw circle
centre_circle = plt.Circle((0, 0), 0.70, fc='white')
fig = plt.gcf()

# Adding Circle in Pie chart
fig.gca().add_artist(centre_circle)
plt.title('Pie', x=0.5, y=0.55)
#plt.show()

st.header('My Running Data')
st.header('Recent Runs: ')
st.table(summary)
st.pyplot(fig)
