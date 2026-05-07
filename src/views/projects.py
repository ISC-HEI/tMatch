
import streamlit as st

from models.user import User
from services.db import get_db
from utils.assignment import start_assignment
from utils.nav import allowed, project_detail_page, protect

protect("projects")

db = get_db()

program = db.get_program(st.session_state.program_id)
projects = program.projects if program is not None else []
projects_number = len(projects)

user: User = st.session_state.user
roles = user.get_roles(st.session_state.program_id)

st.title("Projects")

def render_for_students():
    st.caption(f"Rate each project from 0 (lowest) to {projects_number} (highest).")
    st.divider()

    cols = st.columns([4, 3, 4, 1.5])
    cols[0].markdown("**Project**")
    cols[1].markdown("**Teacher**")
    cols[2].markdown("**Rating**")
    st.divider()

    for project in projects:
        pid = project.id
        rating = project.get_rating_from(st.session_state.user.id)

        cols = st.columns([4, 3, 4, 1.5])
        cols[0].write(project.title)
        cols[1].write(project.teacher.ldap_uid)

        with cols[2]:
            slider_val = st.slider(
                label="rating",
                min_value=0,
                max_value=projects_number,
                value=rating.value if rating is not None else 0,
                key=f"slider_{pid}",
                label_visibility="hidden",
            )
            if st.button("Submit rating", key=f"submit_{pid}", type="primary"):
                db.apply_rating(project.id, user.id, slider_val)

        if cols[3].button("Detail", key=f"detail_{pid}"):
            st.session_state.selected_project = project.id
            st.switch_page(project_detail_page)

def render_for_others():
    if st.button("Start assignment"):
        if start_assignment(st.session_state.program_id):
            st.success("Successfuly started the assignment algorithm. You'll receive the result by email later.")

        else:
            st.error("Some students haven't rated all projects yet. They'll be notified now.")

    st.divider()

    cols = st.columns([4, 0.8])
    cols[0].markdown("**Project**")

    st.divider()

    for project in projects:
        pid = project.id
        cols = st.columns([4, 0.8])
        cols[0].write(project.title)

        if cols[1].button("Open", key=f"open_{pid}"):
            st.session_state.selected_project = project.id
            st.switch_page(project_detail_page)
        

if allowed(roles, ["student"]):
    render_for_students()

else:
    render_for_others()
