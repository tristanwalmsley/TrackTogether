import streamlit as st
import pandas as pd
import sqlite3
import time

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Assignment Tracker",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Assignment Tracker. Made by Aparna, Tabitha, Tristan."
    }
)

# ---------------------------------------------------
# Navigation buttons (Home / Profile)
# ---------------------------------------------------
col1, col2 = st.columns([6, 1])
with col1:
    if st.button("🏠 Home"):
        st.switch_page("pages/home_page.py")
with col2:
    if st.button("👤 Profile"):
        st.switch_page("pages/my_profile.py")

# ---------------------------------------------------
# Get user information
# ---------------------------------------------------
user_id = st.session_state.get("user_id")

# Connect to users database to get username
users_conn = sqlite3.connect("users.db")
username_query = "SELECT username FROM users WHERE id = ?"
username_df = pd.read_sql_query(username_query, users_conn, params=(user_id,))

if not username_df.empty:
    username = username_df.iloc[0]["username"]
    st.markdown(f"<h1 style='text-align: center;'>Upcoming Assignments - {username}</h1>", unsafe_allow_html=True)

# ---------------------------------------------------
# Connect to assignments database
# ---------------------------------------------------
assign_conn = sqlite3.connect("assignments.db")

# SQL queries
query_active = """
SELECT id, name, module_name, module_code, due_date, progress
FROM assignments
WHERE complete = 0 AND user_id = ?
ORDER BY due_date
"""

query_completed = """
SELECT id, name, module_name, module_code, due_date, progress
FROM assignments
WHERE complete = 1 AND user_id = ?
ORDER BY due_date
"""

# Fetch assignments
df_active = pd.read_sql_query(query_active, assign_conn, params=(user_id,))
df_completed = pd.read_sql_query(query_completed, assign_conn, params=(user_id,))

# ---------------------------------------------------
# Highlight next assignment due
# ---------------------------------------------------
if not df_active.empty:
    next_due = df_active.iloc[0]
    st.info(
        f"Next deadline: **{next_due['name']}** "
        f"({next_due['module_code']}) due {next_due['due_date']}"
    )
else:
    st.success("You have no active assignments right now.")
    st.toast(body="Congrats, you have no active assignments!", icon="🎉")

# ---------------------------------------------------
# Active assignments table
# ---------------------------------------------------
# Table header
header_cols = st.columns([4, 3, 1.5, 1.2, 1, 0.85, 0.78, 0.96, 1.5])
header_cols[0].write("**Name**")
header_cols[1].write("**Module Name**")
header_cols[2].write("**Module Code**")
header_cols[3].write("**Due Date**")
header_cols[4].write("**Progress**")
header_cols[5].write("")  # View
header_cols[6].write("")  # Edit
header_cols[7].write("")  # Delete
header_cols[8].write("")  # Complete

st.divider()

# Display each active assignment row
for _, row in df_active.iterrows():
    cols = st.columns([4, 3, 1.5, 1.2, 1, 0.85, 0.78, 0.96, 1.5])

    # Assignment info
    cols[0].write(row["name"])
    cols[1].write(row["module_name"])
    cols[2].write(row["module_code"])
    cols[3].write(row["due_date"])

    # Progress coloring
    progress = row["progress"]
    if progress < 40:
        cols[4].markdown(f":red[{progress}%]")
    elif progress < 75:
        cols[4].markdown(f":orange[{progress}%]")
    else:
        cols[4].markdown(f":green[{progress}%]")

    # Actions: View, Edit, Delete
    if cols[5].button("View", key=f"view_{row['id']}"):
        st.session_state["selected_assignment"] = row["id"]
        st.switch_page("pages/view_details.py")

    if cols[6].button("Edit", key=f"edit_{row['id']}"):
        st.session_state["edit_assignment"] = row["id"]
        st.switch_page("pages/edit_assignments.py")

    if cols[7].button("Delete", key=f"delete_{row['id']}"):
        cursor = assign_conn.cursor()
        cursor.execute("DELETE FROM assignments WHERE id = ?", (row["id"],))
        assign_conn.commit()
        st.rerun()

    # Complete button logic
    due_date = pd.to_datetime(row["due_date"])
    today = pd.Timestamp.today()
    can_complete = progress >= 75 or today >= due_date

    complete_key = f"complete_{row['id']}"
    if cols[8].button("Complete", key=complete_key):
        if can_complete:
            cursor = assign_conn.cursor()
            cursor.execute("UPDATE assignments SET complete = 1 WHERE id = ?", (row["id"],))
            assign_conn.commit()
            st.success("Assignment marked complete!")
            st.rerun()
        else:
            st.toast("Unable to mark assignment complete!", duration=10)
            time.sleep(0.5)
            st.toast("You can only complete assignments that are above 74% progress or have reached their due date.", duration=13)

# ---------------------------------------------------
# Add assignment button
# ---------------------------------------------------
if st.button("Add Assignment", type="primary"):
    st.switch_page("pages/add_assignments.py")

st.divider()

# ---------------------------------------------------
# Completed assignments table
# ---------------------------------------------------
st.header("Completed Assignments")
for _, row in df_completed.iterrows():
    cols = st.columns([4, 3, 1.5, 1.2, 1, 0.85, 0.78, 0.96, 1.5])
    cols[0].write(row["name"])
    cols[1].write(row["module_name"])
    cols[2].write(row["module_code"])
    cols[3].write(row["due_date"])
    cols[4].write(f"{row['progress']}%")

    if cols[5].button("View", key=f"view_complete_{row['id']}"):
        st.session_state["selected_assignment"] = row["id"]
        st.switch_page("pages/view_details.py")

    if cols[8].button("Uncomplete", key=f"uncomplete_{row['id']}"):
        cursor = assign_conn.cursor()
        cursor.execute("UPDATE assignments SET complete = 0 WHERE id = ?", (row["id"],))
        assign_conn.commit()
        st.success("Assignment marked incomplete!")
        st.rerun()