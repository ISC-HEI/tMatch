
import streamlit as st

from models.role import Role

login_page = st.Page("views/login.py", title="Login", default=True)
manage_projects_page = st.Page("views/manage_projects.py", title="Manage Projects")
project_detail_page = st.Page("views/project_detail.py", title="View Project Details", visibility="hidden")
projects_page = st.Page("views/projects.py", title="View Projects List")
assigned_project_page = st.Page("views/assigned_project.py", title="Assigned Project")

PAGE_CONFIG = {
    "manage_projects": manage_projects_page,
    "project_detail": project_detail_page,
    "projects": projects_page,
    "assigned_project": assigned_project_page,
}

PAGE_ROLES = {
    "manage_projects": ["secretary", "teacher"],
    "project_detail": ["program director", "secretary", "teacher", "student"],
    "projects": ["program director", "secretary", "teacher", "student"],
    "assigned_project": ["student"]
}

def allowed(roles: list[Role], allowed_roles: list[str]):
    """Check if any of the user's roles are in the allowed roles list.

    Args:
        roles: List of Role objects.
        allowed_roles: List of allowed role names.

    Returns:
        True if at least one role matches, False otherwise.
    """

    for role in roles:
        if role.name in allowed_roles:
            return True

    return False

def protect(page_name: str):
    """Protect a page by checking user authentication and authorization.

    Args:
        page_name: Name of the page to protect.
    """

    user = st.session_state.get("user")

    if user is None:
        st.switch_page(login_page)

    roles = user.get_roles(st.session_state.program_id)

    if page_name == "landing":
        return

    allowed_roles = PAGE_ROLES.get(page_name, [])
    if not allowed(roles, allowed_roles):
        st.switch_page(projects_page)
