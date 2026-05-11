
import streamlit as st
from services.auth import login
from services.db import get_db
from utils.logger import logger

db = get_db()

if "user" in st.session_state and st.session_state.user:
    st.switch_page("pages/landing.py")

with st.form("Login"):
    uid = st.text_input("UID", key="uid")
    password = st.text_input("Password", key="password", type="password")

    if st.form_submit_button("Login", key="login_btn"):
        if user := login(uid, password):
            st.session_state.user = user
            logger.info(f"User logged in: {uid}")
            st.success("Successfully logged in")
        else:
            logger.warn(f"Invalid credentials for: {uid}")
            st.error("Invalid credentials")
