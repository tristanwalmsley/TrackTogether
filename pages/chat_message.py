import streamlit as st
import sqlite3
from header import show_header

# ---------------------------------------------------
# Page configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Track Together",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# Track Together. Made by Aparna, Tabitha, Tristan."
    }
)

show_header()

# ---------------------------------------------------
# Defines connections to databases.
# ---------------------------------------------------

# Chat connection.
conn = sqlite3.connect("chat.db")
cursor = conn.cursor()

# Users connection.
conn2 = sqlite3.connect("users.db")
cursor2 = conn2.cursor()

st.Page("pages/chat_message.py")

st.title("Chat:")
user_id = st.session_state.get("user_id")

# Makes user login in not logged in.
if (user_id == None):
    st.switch_page("streamlit_app.py")

# Gets module code from session storage.
module_code = st.session_state.get("module_code")

# Gets name from the database.
cursor2.execute("SELECT fName FROM users WHERE id = ?", (user_id,))
user = cursor2.fetchone()

if user:
    username = user[0]
else:
    st.error("User is not found!")
    st.stop()

# Gets all of the records from the database.
cursor.execute("SELECT fName, message FROM chat WHERE module_code = ? ORDER BY id", (module_code,))
messages = cursor.fetchall()

# Writes the name and message to the chat space.
for name, msg in messages:
    with st.chat_message(name):
        st.write(msg)

# Sets up the chat screen.
prompt = st.chat_input("Say something")
if prompt:
    cursor.execute(
        "INSERT INTO chat (fName, message, module_code) VALUES (?, ?, ?)",
        (username, prompt, module_code)
    )

    # Commits the connection.
    conn.commit()

    with st.chat_message(username):
        st.write(prompt)
    