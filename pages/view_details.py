import streamlit as st
import sqlite3
import pandas as pd
import time

# ---------------------------------------------------
# Page config
# ---------------------------------------------------
st.set_page_config(
    page_title="Assignment Details",
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
# Helper function for progress bar color
# ---------------------------------------------------
def progress_color(percent: int) -> str:
    if percent < 40:
        return "red"
    elif percent < 75:
        return "orange"
    else:
        return "green"

# ---------------------------------------------------
# Connect to assignments database
# ---------------------------------------------------
conn = sqlite3.connect("assignments.db", check_same_thread=False)
cursor = conn.cursor()

assignment_id = st.session_state.get("selected_assignment")

# Fetch assignment
assignment_query = "SELECT * FROM assignments WHERE id = ?"
assignment_df = pd.read_sql_query(assignment_query, conn, params=(assignment_id,))

if assignment_df.empty:
    st.error("Assignment not found.")
    st.stop()

assignment = assignment_df.iloc[0]
is_complete = bool(assignment["complete"])

st.title(f"{assignment['name']}")

# ---------------------------------------------------
# Fetch tasks for this assignment
# ---------------------------------------------------
tasks_query = "SELECT * FROM tasks WHERE assignment_id = ? ORDER BY due_date"
tasks_df = pd.read_sql_query(tasks_query, conn, params=(assignment_id,))

# Calculate assignment progress based on tasks
total_tasks = len(tasks_df)
completed_tasks = tasks_df["completed"].sum() if total_tasks > 0 else 0
progress_percent = int((completed_tasks / total_tasks) * 100) if total_tasks > 0 else 0

# Update assignment progress in database
cursor.execute(
    "UPDATE assignments SET progress = ? WHERE id = ?",
    (progress_percent, assignment_id)
)
conn.commit()

# Display toast notifications based on progress
if progress_percent == 100:
    st.toast("This assignment has reached 100%. Consider marking it complete.", icon="✅", duration=7)
    st.balloons()
elif progress_percent >= 74:
    st.toast("This assignment has reached a first class! Try to reach 100%.", icon="✅", duration=7)
elif progress_percent >= 40:
    st.toast("Assignment has reached 40% progress. Keep going!", icon="✅", duration=7)

# ---------------------------------------------------
# Progress bar
# ---------------------------------------------------
color = progress_color(progress_percent)
st.markdown(
    f"""
    <div style="background-color:#eee;border-radius:8px;height:22px;">
        <div style="
            width:{progress_percent}%;
            background-color:{color};
            height:22px;
            border-radius:8px;
            text-align:center;
            color:white;
            font-weight:bold;">
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown(f"### :{color}[{progress_percent}% complete]")
st.caption(f"{completed_tasks} of {total_tasks} tasks completed")

if is_complete:
    st.success("This assignment has been marked as completed.")
    st.toast("Tasks are locked, but notes can still be edited.", icon="🔒", duration=30)

st.divider()

# ---------------------------------------------------
# Assignment details
# ---------------------------------------------------
st.subheader("Details")
col1, col2 = st.columns(2)
col1.markdown(f"**Module Name:** {assignment['module_name']}")
col2.markdown(f"**Start Date:** {assignment['start_date']}")

col3, col4 = st.columns(2)
col3.markdown(f"**Module Code:** {assignment['module_code']}")
col4.markdown(f"**Due Date:** {assignment['due_date']}")

st.divider()

# ---------------------------------------------------
# Tasks list
# ---------------------------------------------------
st.subheader("Tasks")
if tasks_df.empty:
    st.info("No tasks yet. Add one below to start tracking progress.")

for _, task in tasks_df.iterrows():
    cols = st.columns([3, 2, 4, 1, 1, 1])

    # Task name
    if task["completed"]:
        cols[0].markdown(f":gray[{task['name']}]")
    else:
        cols[0].write(task["name"])

    # Task due date
    due_date = pd.to_datetime(task["due_date"])
    if not task["completed"] and due_date < pd.Timestamp.today():
        cols[1].markdown(f":red[{task['due_date']}]")
    else:
        cols[1].write(task["due_date"])

    # Task description
    cols[2].write(task["description"])

    # Task completion checkbox (if assignment not complete)
    if not is_complete:
        completed_checkbox = cols[3].checkbox(
            "",
            value=bool(task["completed"]),
            key=f"task_{task['id']}"
        )
        if completed_checkbox != bool(task["completed"]):
            cursor.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (int(completed_checkbox), task["id"])
            )
            conn.commit()
            st.rerun()
    else:
        cols[3].write("✔" if task["completed"] else "")

    # Edit / Delete buttons (if assignment not complete)
    if not is_complete:
        if cols[4].button("Edit", key=f"edit_task_{task['id']}"):
            st.session_state["editing_task"] = task["id"]
        if cols[5].button("Delete", key=f"delete_task_{task['id']}"):
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task["id"],))
            conn.commit()
            st.rerun()

# ---------------------------------------------------
# Edit task form
# ---------------------------------------------------
if "editing_task" in st.session_state:
    task_id = st.session_state["editing_task"]
    task_df = pd.read_sql_query("SELECT * FROM tasks WHERE id = ?", conn, params=(task_id,))
    if not task_df.empty:
        task = task_df.iloc[0]
        st.divider()
        st.subheader("Edit Task")

        with st.form("edit_task_form"):
            edit_name = st.text_input("Task Name", value=task["name"])
            edit_due = st.date_input("Due Date", value=pd.to_datetime(task["due_date"]))
            edit_desc = st.text_area("Description", value=task["description"])

            col1, col2 = st.columns(2)
            save_btn = col1.form_submit_button("Save Changes")
            cancel_btn = col2.form_submit_button("Cancel")

            if save_btn:
                cursor.execute(
                    "UPDATE tasks SET name=?, description=?, due_date=? WHERE id=?",
                    (edit_name, edit_desc, str(edit_due), task_id)
                )
                conn.commit()
                del st.session_state["editing_task"]
                st.toast("Task successfully edited.", icon="✏️")
                time.sleep(1)
                st.rerun()

            if cancel_btn:
                del st.session_state["editing_task"]
                st.rerun()

# ---------------------------------------------------
# Add task form
# ---------------------------------------------------
if not is_complete:
    if st.button("Add Task"):
        st.session_state["show_task_form"] = not st.session_state.get("show_task_form", False)

if st.session_state.get("show_task_form"):
    with st.form("add_task_form"):
        task_name = st.text_input("Task Name")
        task_due = st.date_input("Task Due Date")
        task_desc = st.text_area("Description")

        submitted = st.form_submit_button("Create Task")
        if submitted:
            cursor.execute(
                "INSERT INTO tasks (assignment_id, name, description, due_date, completed) VALUES (?, ?, ?, ?, ?)",
                (assignment_id, task_name, task_desc, str(task_due), 0)
            )
            conn.commit()
            st.session_state["show_task_form"] = False
            st.toast("Task added! Good luck!", icon="🖊️")
            st.rerun()

# ---------------------------------------------------
# Notes
# ---------------------------------------------------
st.divider()
st.subheader("Notes")

notes_value = st.text_area(label="", value=assignment.get("notes", ""), height=200)

if st.button("Save Notes"):
    cursor.execute("UPDATE assignments SET notes = ? WHERE id = ?", (notes_value, assignment_id))
    conn.commit()
    st.toast("Notes successfully updated!", icon="📜")

# ---------------------------------------------------
# Return button
# ---------------------------------------------------
if st.button("Return to View Assignments"):
    st.switch_page("pages/view_assignments.py")