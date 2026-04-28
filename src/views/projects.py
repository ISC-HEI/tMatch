
import streamlit as st

from models.user import User
from services.db import get_db
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
    st.caption(f"Rate each project from 0 (lowest) to {projects_number } (highest). Your scores are private.")

    st.divider()

    cols = st.columns([4, 2, 0.8])
    cols[0].markdown("**Project**")
    cols[1].markdown("**Rating**")

    st.divider()

    for project in projects:
        pid = project.id
        rating = project.get_rating_from(st.session_state.user.id)
        cols = st.columns([4, 2, 0.8])

        cols[0].write(project.title)

        if rating is not None:
            cols[1].markdown(
                f"<span style='background:#E1F5EE; color:#085041; padding:3px 10px; " +
                f"border-radius:6px; font-weight:500;'>{rating.value}</span>",
                unsafe_allow_html=True,
            )

        else:
            cols[1].markdown(
                "<span style='color:#9CA3AF;'>—</span>",
                unsafe_allow_html=True,
            )

        if cols[2].button("Open", key=f"open_{pid}"):
            st.session_state.selected_project = project.id
            st.switch_page(project_detail_page)


def render_for_others():
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
