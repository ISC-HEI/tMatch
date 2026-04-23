
import streamlit as st
from services.auth import validate_session
from utils.nav import PAGE_ROLES

st.session_state.session = validate_session()

if st.session_state.session is not None:
    st.session_state.user = st.session_state.session.user

else:
    st.session_state.user = None

pg = None

login_page = st.Page("pages/login.py", title="Login", default=True)
landing_page = st.Page("pages/landing.py", title="Home")
manage_projects_page = st.Page("pages/manage_projects.py", title="Manage Projects")
manage_users_page = st.Page("pages/manage_users.py", title="Manage Users")
project_page = st.Page("pages/project.py", title="View Project")

pages_config = {
    "landing": landing_page,
    "manage_projects": manage_projects_page,
    "manage_users": manage_users_page,
    "project": project_page,
}

user = st.session_state.user
session = st.session_state.session

page_list = []

if session and user:
    role = user.get_role(session.program.id)

    if role is None:
        page_list = [landing_page]
    else:
        page_list = [
            pages_config[page_name]
            for page_name, allowed_roles in PAGE_ROLES.items()
            if role.name in allowed_roles
        ]
        if not page_list:
            page_list = [landing_page]

else:
    page_list = [login_page]


pg = st.navigation(page_list)
pg.run()
