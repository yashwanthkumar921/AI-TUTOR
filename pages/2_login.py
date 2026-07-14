import streamlit as st
import json
import hashlib
import streamlit as st

import streamlit as st


USER_FILE = "users.json"

# ✅ Load users from JSON
def load_users():
    try:
        with open(USER_FILE, "r") as f:
            users = json.load(f)
            return users if isinstance(users, list) else []  # Ensure users is a list
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# ✅ Hash password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

st.title("Login")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if st.button("Login"):
    users = load_users()
    hashed_password = hash_password(password)

    for user in users:
        if user["username"] == username and user["password"] == hashed_password:
            st.success(f"Welcome, {username}! Redirecting...")

            # ✅ Save login state
            st.session_state["logged_in"] = True
            st.session_state["username"] = username

            # ✅ Redirect to home.py
            st.switch_page("pages/3_home.py")
            st.rerun()
            break
    else:
        st.error("Invalid username or password!")

# ✅ Redirect to home.py after successful login
if st.session_state.get("logged_in"):
     st.switch_page("pages/3_home.py")