
import streamlit as st
from streamlit_star_rating import st_star_rating

from services.db import get_db
from utils.nav import protect

protect()

db = get_db()

projects = db.get_projects()
projects_map = { p.id: p for p in projects }

project_id: int = st.selectbox(
    "Project",
    projects_map,
    format_func=lambda project_id: projects_map[project_id].title,
    index=0,
)

project = projects_map[project_id]

st.title(project.title)

st.header("Description")
st.text(project.description)

project_rating = db.get_rating(project_id, st.session_state.user.id)

rating = st_star_rating("Like", 10, project_rating.value if project_rating is not None else 0, key=f"rating_{project_id}")

lb = st.button("Submit like")

if lb:
    db.apply_rating(project_id, st.session_state.user.id, rating)
