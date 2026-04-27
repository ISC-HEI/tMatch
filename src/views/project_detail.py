
import streamlit as st

from components.keywords import render_keywords
from models.project import Project
from services.db import get_db
from utils.nav import projects_page, protect

protect("project_detail")

db = get_db()

user = st.session_state.user

projects = db.get_projects()
projects_number = len(projects)

if "selected_project" not in st.session_state or st.session_state.selected_project is None:
    project = projects[0]
else:
    project: Project = db.get_project(st.session_state.selected_project)

if "edit_rating" not in st.session_state:
    st.session_state.edit_rating = False

pid = project.id
rating = project.get_rating_from(user.id)
already_rated = rating is not None
 
if st.button("← Back to projects"):
    st.switch_page(projects_page)
 
st.divider()
 
st.title(project.title)
render_keywords(project.projects_keywords)
st.write(project.description)
 
st.divider()
 
st.subheader("Your rating")
 
if already_rated and not st.session_state.edit_rating:
    st.success(f"You rated this project **{rating.value} / {projects_number}**.")
    if st.button("Edit my rating"):
        st.session_state.edit_rating = True
        st.rerun()

else:
    chosen_value = st.slider(
        label="Score",
        min_value=0,
        max_value=projects_number,
        value=projects_number // 2,
        step=1,
        help=f"0 = lowest, {projects_number} = highest",
    )
 
    st.caption(f"Selected: **{chosen_value} / {projects_number}**")
 
    if st.button("Submit rating", type="primary"):
        db.apply_rating(project.id, user.id, chosen_value)
        st.session_state.edit_rating = False
        st.rerun()
