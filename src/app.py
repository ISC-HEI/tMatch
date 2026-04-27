
import streamlit as st
from services.auth import validate_session
from utils.nav import PAGE_ROLES, PAGE_CONFIG, landing_page, login_page

st.session_state.session = validate_session()

if st.session_state.session is not None:
    st.session_state.user = st.session_state.session.user

else:
    st.session_state.user = None

pg = None

user = st.session_state.user
session = st.session_state.session

page_list = []

if session and user:
    role = user.get_role(session.program.id)

    if role is None:
        page_list = [landing_page]
    else:
        page_list = [
            PAGE_CONFIG[page_name]
            for page_name, allowed_roles in PAGE_ROLES.items()
            if role.name in allowed_roles
        ]
        if not page_list:
            page_list = [landing_page]

else:
    page_list = [login_page]


pg = st.navigation(page_list)
pg.run()
