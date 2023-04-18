import stravaConnect as sc
import streamlit as st

#df_activities = sc.get_fromAPI(sc.get_auth(), "activities")
df_activities = pd.read_excel('data1.xlsx')

summary = df_activities.head
st.header('My Running Data')
st.header('Recent Runs: ')
st.table(summary)

print(df_activities.columns)
longest_run = max(df_activities['distance'])

st.write(f'longest run: {longest_run}')
