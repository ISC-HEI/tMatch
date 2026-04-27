
import streamlit as st

from models.project import Project
from services.db import get_db
from utils.nav import protect

protect("project")

db = get_db()

projects = db.get_projects()
projects_number = len(projects)

if "selected_project" not in st.session_state or st.session_state.selected_project is None:
    project = projects[0]
else:
    project: Project = st.session_state.selected_project

pid = project.id
score = project.get_rating_from(st.session_state.user.id)
already_rated = score is not None
 
if st.button("← Back to projects"):
    st.switch_page("projects")
 
st.divider()
 
st.title(project.title)
st.caption(project.projects_keywords)
st.write(project.description)
 
st.divider()
 
st.subheader("Your rating")
 
if already_rated:
    st.success(f"You rated this project **{score} / {projects_number }**.")
    if st.button("Edit my rating"):
        del st.session_state.ratings[pid]
        st.rerun()

else:
    chosen = st.slider(
        label="Score",
        min_value=0,
        max_value=projects_number,
        value=projects_number  // 2,
        step=1,
        help=f"0 = lowest, {projects_number} = highest",
    )
 
    st.caption(f"Selected: **{chosen} / {projects_number}**")
 
    if st.button("Submit rating", type="primary"):
        st.session_state.ratings[pid] = chosen
        st.rerun()
