from datetime import datetime, timedelta

import streamlit as st

from constants import (
    LOCKOUT_MINUTES,
    LOCKOUT_THRESHOLD,
    MENTOR_USER_MAP,
    PASSWORD_MIN_LENGTH,
    PASSWORD_REQUIRE_DIGIT,
    USERS,
)
from utils import password_policy_ok, verify_password


def login_panel():
    st.sidebar.subheader("Login")
    username = st.sidebar.text_input("Username", key="login_username")
    password = st.sidebar.text_input("Password", type="password", key="login_password")
    if st.sidebar.button("Sign in"):
        locked_until = st.session_state.failed_logins.get(username)
        if isinstance(locked_until, datetime) and datetime.now() < locked_until:
            st.sidebar.error("Account temporarily locked. Try again later.")
            st.session_state.data.log_event("login_blocked", username, "lockout")
            return
        if not password_policy_ok(password, PASSWORD_MIN_LENGTH, PASSWORD_REQUIRE_DIGIT):
            st.sidebar.error("Password policy not met.")
            st.session_state.data.log_event("login_failed", username, "policy")
            return
        user = USERS.get(username)
        if not user or not verify_password(password, user["password_hash"]):
            st.sidebar.error("Invalid credentials.")
            attempts = st.session_state.failed_logins.get(username, 0)
            attempts = attempts + 1 if isinstance(attempts, int) else 1
            if attempts >= LOCKOUT_THRESHOLD:
                st.session_state.failed_logins[username] = datetime.now() + timedelta(
                    minutes=LOCKOUT_MINUTES
                )
                st.session_state.data.log_event("login_lockout", username, "threshold reached")
            else:
                st.session_state.failed_logins[username] = attempts
                st.session_state.data.log_event("login_failed", username, "invalid")
            return
        st.session_state.user = username
        st.session_state.role = user["role"]
        st.session_state.failed_logins.pop(username, None)
        if user["role"] == "mentor":
            st.session_state.mentor = MENTOR_USER_MAP.get(username)
            if not st.session_state.mentor:
                st.sidebar.error("No mentor mapping found for this account.")
                st.session_state.user = None
                st.session_state.role = None
                return
        st.session_state.data.log_event("login_success", username, user["role"])
        st.sidebar.success(f"Signed in as {username} ({user['role']}).")
