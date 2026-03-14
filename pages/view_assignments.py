import streamlit as st
from numpy.random import default_rng as rng
import pandas as pd
import sqlite3
from pathlib import Path

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

st.title("Upcoming Assignments")

# Connect to database
conn = sqlite3.connect("assignments.db")

# Get assignments
query = "SELECT id, name, module_name, module_code, due_date, progress FROM assignments"


df = pd.read_sql_query(query, conn)

# Table header
header = st.columns([3,3,2,2,2,2])
header[0].write("**Name**")
header[1].write("**Module Name**")
header[2].write("**Module Code**")
header[3].write("**Due Date**")
header[4].write("**Progress**")
header[5].write("**View Details**")

st.divider()

# Rows
for index, row in df.iterrows():

    cols = st.columns([3,3,2,2,2,2])

    cols[0].write(row["name"])
    cols[1].write(row["module_name"])
    cols[2].write(row["module_code"])
    cols[3].write(row["due_date"])
    cols[4].write(f"{row['progress']}%")

    if cols[5].button("View", key=row["id"]):
        st.session_state["selected_assignment"] = row["id"]
        st.switch_page("pages/assignment_details.py")


if st.button("Add Assignment", type="primary"):
    st.switch_page(st.Page("pages/add_assignments.py"))