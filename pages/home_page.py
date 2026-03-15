import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("users.db", check_same_thread=False)

userID = st.session_state.get("user_id")

username_query = """
SELECT username
FROM users
WHERE id = ?
"""

name_df = pd.read_sql_query(username_query, conn, params=(userID,))

st.Page("pages/home_page.py")

st.set_page_config(
    page_title="Assignment Tracker",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Assignment Tracker. Made by Aparna, Tabitha, Tristan."
    }
)

#st.markdown("<h2 style='text-align: right;'>👤</h2>", unsafe_allow_html=True)

col1, col2 = st.columns([6, 1])
with col2:
    if st.button("👤"):
        st.switch_page(st.Page("pages/my_profile.py"))

st.divider()
if not name_df.empty:
    username = name_df.iloc[0]

    st.markdown(f"<h1 style='text-align: center;'>Welcome {username['username']}</h1>", unsafe_allow_html=True)

st.write("") 
st.write("") 

topTextCols = st.columns([2.5,8,2.5])

conn = sqlite3.connect("assignments.db", check_same_thread=False)

query = """
SELECT progress
FROM assignments
WHERE user_id = ?
"""

df = pd.read_sql_query(query, conn, params=(userID,))

if not df.empty:
    overall_progress = int(df["progress"].mean())
else:
    overall_progress = 0

topTextCols[1].title("Your overall progress")

topTextCols[1].progress(overall_progress)

topTextCols[1].markdown(f"{overall_progress}% complete")

if overall_progress == 100:
    st.success("🎉 All assignments completed!")
    st.balloons()

st.write("")
st.write("")

cols = st.columns([3.2,4.4,4.4,4.4])

with cols[1]:
    if st.button("View Assignments"):
     st.switch_page(st.Page("pages/view_assignments.py"))
with cols[2]:
    if st.button("View Leaderboard"):
     st.switch_page(st.Page("pages/view_leaderboard.py"))
with cols[3]:
    if st.button("Connect"):
     st.switch_page(st.Page("pages/connect.py"))

st.write("")
st.write("")

bottomTextCols = st.columns([2.5,8,2.5])

bottomTextCols[1].write("Welcome to the Assignment Tracker App! This app is designed to help you stay organized and on top of your assignments. You can view your assignments, check the leaderboard, and connect with others. Let's get started!")

st.write("")

bottomTextCols[1].write("Assignments are linked to your account, so you can easily see your own workload and how far through it you are. As you update progress or complete assignments, your overall completion will increase.")

st.write("")

bottomTextCols[1].write("You can also check the Leaderboard to see how your progress compares with other users. It’s a simple way to stay motivated and keep moving forward with your work.")

st.write("")
st.divider()
