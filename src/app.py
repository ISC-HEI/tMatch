
import streamlit as st
from services.auth import validate_session

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

user = st.session_state.user
session = st.session_state.session

page_list = []

if session and user:
    role = user.get_role(session.program.id)

    if role is None:
        page_list = [landing_page]

    elif role.name == "secretary":
        page_list = [landing_page, manage_projects_page, manage_users_page, project_page]

    elif role.name == "teacher":
        page_list = [landing_page, manage_projects_page]

else:
    page_list = [login_page]


pg = st.navigation(page_list)
pg.run()
