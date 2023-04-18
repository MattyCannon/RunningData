import stravaConnect as sc
import streamlit as st

df_activities = sc.get_fromAPI(sc.get_auth(), "activities")

print(df_activities.head)
st.header('My Running Data')
st.header('Recent Runs: ')
st.table(df_activities.head)

print(df_activities.columns)
longest_run = max(df_activities['distance'])

st.write(f'longest run: {longest_run}')
