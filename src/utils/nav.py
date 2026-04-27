
import streamlit as st

login_page = st.Page("views/login.py", title="Login", default=True)
landing_page = st.Page("views/landing.py", title="Home")
manage_projects_page = st.Page("views/manage_projects.py", title="Manage Projects")
manage_users_page = st.Page("views/manage_users.py", title="Manage Users")
project_detail_page = st.Page("views/project_detail.py", title="View Project Details", visibility="hidden")
projects_page = st.Page("views/projects.py", title="View Projects List")

PAGE_CONFIG = {
    "landing": landing_page,
    "manage_projects": manage_projects_page,
    "manage_users": manage_users_page,
    "project_detail": project_detail_page,
    "projects": projects_page,
}

PAGE_ROLES = {
    "landing": ["program_director", "secretary", "teacher", "student"],
    "manage_projects": ["secretary", "teacher"],
    "manage_users": ["secretary"],
    "project_detail": ["program director", "secretary", "teacher", "student"],
    "projects": ["program director", "secretary", "teacher", "student"]
}

def protect(page_name: str):
    session = st.session_state.get("session")
    user = st.session_state.get("user")

    if user is None or session is None or session.program_id is None:
        st.switch_page("views/login.py")

    role = user.get_role(session.program_id)

    allowed_roles = PAGE_ROLES.get(page_name, [])
    if role is None or role.name not in allowed_roles:
        st.switch_page("views/landing.py")
