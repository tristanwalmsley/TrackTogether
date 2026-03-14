import streamlit as st
import sqlite3

st.Page("pages/add_assignments.py")

st.set_page_config(
    page_title="Assignment Tracker",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Assignment Tracker. Made by Aparna, Tabitha, Tristan."
    }
)

conn = sqlite3.connect("assignments.db")
cursor = conn.cursor()

def run_register_assignment():
    cursor.execute(
    """
    INSERT INTO assignments (name, module_name, module_code, start_date, due_date, progress)
    VALUES (?, ?, ?, ?, ?, ?)
    """,
    (name_val, module_name_val, module_code_val, start_date_val, due_date_val, 0)
    )

    conn.commit()

st.title("Upcoming Assignments")

with st.form("add_asignment"):
    name_val = st.text_input("Enter Assignment Name:", None, 30)
    module_name_val = st.text_input("Enter Module Name:", "", 30)
    module_code_val = st.text_input("Enter Module Code:", "CO", 6)
    start_date_val = st.date_input("Enter Start Date:", "today", "today")
    due_date_val = st.date_input("Enter Due Date:", "today", "today")

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Assignment Successfully Added")
        run_register_assignment()