
import streamlit as st
from services.auth import validate_session
from services.db import get_db
from utils.nav import PAGE_ROLES, PAGE_CONFIG, allowed, landing_page, login_page

st.session_state.session = validate_session()

if st.session_state.session is not None:
    st.session_state.user = st.session_state.session.user

else:
    st.session_state.user = None

pg = None

user = st.session_state.user
session = st.session_state.session

page_list = []

db = get_db()

programs = db.get_programs()

if "program_id" not in st.session_state:
    st.session_state.program_id = programs[0].id

def set_program():
    st.session_state.program_id = st.session_state.program_selector 

if session and user:
    roles = user.get_roles(st.session_state.program_id)

    with st.sidebar:
        st.space("stretch")

        options = { p.id: p for p in programs }
        program_id = st.session_state.program_id

        program_id: int = st.selectbox(
            "Program",
            options,
            format_func=lambda program_id: options[program_id].name,
            on_change=set_program,
            key="program_selector",
            index=programs.index(options[program_id]),
        )

        st.session_state.program_id = program_id

    if len(roles) == 0:
        page_list = [landing_page]
    else:
        page_list = [
            PAGE_CONFIG[page_name]
            for page_name, allowed_roles in PAGE_ROLES.items()
            if allowed(roles, allowed_roles)
        ]
        if not page_list:
            page_list = [landing_page]

else:
    page_list = [login_page]


pg = st.navigation(page_list)
pg.run()
