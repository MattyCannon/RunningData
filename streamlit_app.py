import stravaConnect as sc
import streamlit as st
df_activities = sc.get_fromAPI(sc.get_auth(), "activities")

st.header('Test')
st.table(df_activities)
