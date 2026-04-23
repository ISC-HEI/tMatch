
import streamlit as st


PAGE_ROLES = {
    "landing": ["secretary", "teacher", "student"],
    "manage_projects": ["secretary", "teacher"],
    "manage_users": ["secretary"],
    "project": ["program director", "secretary", "teacher", "student"],
}

def protect(page_name: str):
    session = st.session_state.get("session")
    user = st.session_state.get("user")

    if user is None or session is None or session.program_id is None:
        st.switch_page("pages/login.py")

    role = user.get_role(session.program_id)

    allowed_roles = PAGE_ROLES.get(page_name, [])
    if role is None or role.name not in allowed_roles:
        st.switch_page("pages/landing.py")
