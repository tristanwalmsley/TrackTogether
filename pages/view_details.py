import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("assignments.db", check_same_thread=False)

assignment_id = st.session_state.get("selected_assignment")

query = "SELECT * FROM assignments WHERE id = ?"
assignment = pd.read_sql_query(query, conn, params=(assignment_id,))

st.title("Assignment Details")

if not assignment.empty:

    a = assignment.iloc[0]

    # --- LOAD TASKS FIRST ---
    tasks = pd.read_sql_query(
        "SELECT * FROM tasks WHERE assignment_id = ?",
        conn,
        params=(assignment_id,)
    )

    # --- CALCULATE PROGRESS ---
    total_tasks = len(tasks)
    completed_tasks = tasks["completed"].sum() if total_tasks > 0 else 0

    progress_percent = 0 if total_tasks == 0 else int((completed_tasks / total_tasks) * 100)

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE assignments SET progress = ? WHERE id = ?",
        (progress_percent, assignment_id)
    )

    conn.commit()

    # --- HEADER ---
    st.subheader(a["name"])

    st.progress(progress_percent / 100)
    st.write(f"{progress_percent}% complete")
    st.caption(f"{completed_tasks} of {total_tasks} tasks completed")

    st.divider()

    col1, col2 = st.columns(2)
    col1.markdown(f"**Module Name:** {a['module_name']}")
    col2.markdown(f"**Module Code:** {a['module_code']}")

    col3, col4 = st.columns(2)
    col3.markdown(f"**Start Date:** {a['start_date']}")
    col4.markdown(f"**Due Date:** {a['due_date']}")

    st.divider()
    st.subheader("Tasks")

    for _, task in tasks.iterrows():

        cols = st.columns([3,2,4,1,1])

        cols[0].write(task["name"])
        cols[1].write(task["due_date"])
        cols[2].write(task["description"])

        completed = cols[3].checkbox(
            "Done",
            value=bool(task["completed"]),
            key=f"task_{task['id']}"
        )

        if completed != bool(task["completed"]):

            cursor = conn.cursor()

            cursor.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?",
                (int(completed), task["id"])
            )

            conn.commit()
            st.rerun()
        
        if cols[4].button("Delete", key=f"delete_{task['id']}"):

            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task["id"],)
            )

            conn.commit()

            st.rerun()

if st.button("Add Task"):
    st.session_state["show_task_form"] = True

if st.session_state.get("show_task_form"):

    with st.form("add_task"):

        task_name = st.text_input("Task Name")
        task_due = st.date_input("Task Due Date")
        task_desc = st.text_area("Description")

        submitted = st.form_submit_button("Create Task")

        if submitted:

            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO tasks (assignment_id, name, description, due_date, completed)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    assignment_id,
                    task_name,
                    task_desc,
                    str(task_due),
                    0
                )
            )

            conn.commit()

            st.session_state["show_task_form"] = False
            st.success("Task added!")

            st.rerun()

st.divider()
st.subheader("Notes")

notes_val = st.text_area(
    "Assignment Notes",
    value=a.get("notes", ""),
    height=200
)

if st.button("Save Notes"):

    cursor = conn.cursor()

    cursor.execute(
        "UPDATE assignments SET notes = ? WHERE id = ?",
        (notes_val, assignment_id)
    )

    conn.commit()

    st.success("Notes saved")