import streamlit as st
import sqlite3
import pandas as pd

st.Page("pages/view_assignments.py")

st.set_page_config(
    page_title="Assignment Tracker",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Assignment Tracker. Made by Aparna, Tabitha, Tristan."
    }
)

col1, col2 = st.columns([6, 1])
with col1:
    if st.button("🏠"):
        st.switch_page(st.Page("pages/home_page.py"))
with col2:
    if st.button("👤"):
        st.switch_page(st.Page("pages/my_profile.py"))

st.markdown("<h1 style='text-align: center;'>Assignment Leaderboard</h1>", unsafe_allow_html=True)

users_conn = sqlite3.connect("users.db")
assign_conn = sqlite3.connect("assignments.db")

# Load users
users_df = pd.read_sql_query(
    "SELECT id, username FROM users",
    users_conn
)

# Load assignments
assign_df = pd.read_sql_query(
    "SELECT user_id, progress FROM assignments",
    assign_conn
)

# Merge them
merged = pd.merge(
    users_df,
    assign_df,
    left_on="id",
    right_on="user_id",
    how="left"
)

# Calculate average progress per user
leaderboard = (
    merged.groupby("username")["progress"]
    .mean()
    .fillna(0)
    .round(1)
    .reset_index()
)

leaderboard = leaderboard.sort_values(
    by="progress",
    ascending=False
).reset_index(drop=True)

if leaderboard.empty:
    st.info("No assignments yet.")
else:
    header = st.columns([1.1,2,2,2])
    header[1].write("**Rank**")
    header[2].write("**Username**")
    header[3].write("**Progress**")

    for i, row in leaderboard.iterrows():

        rank = i + 1

        cols = st.columns([1.1,2,2,2])

        medal = ""
        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"

        cols[1].markdown(f"### {rank} {medal}")
        cols[2].write(row["username"])
        cols[3].write(f"{row['progress']}%")