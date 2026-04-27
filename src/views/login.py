
import streamlit as st
from services.auth import login
from services.db import get_db

db = get_db()

if "user" in st.session_state and st.session_state.user:
    st.switch_page("pages/landing.py")

with st.form("Login"):
    programs = db.get_programs()
    programs_map = {p.id: p for p in programs}

    program_id: int = st.selectbox(
        "Program",
        programs_map,
        format_func=lambda program_id: programs_map[program_id].name,
        index=0,
    )

    uid = st.text_input("UID", key="uid")
    password = st.text_input("Password", key="password", type="password")

    if st.form_submit_button("Login", key="login_btn"): 
        if user := login(uid, password, program_id):
            st.session_state.user = user
            st.session_state.program = db.get_program(program_id)
            st.success("Successfully logged in")
        else:
            st.error("Invalid credentials")
