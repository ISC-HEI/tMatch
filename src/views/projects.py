
import streamlit as st

from services.db import get_db

db = get_db()

projects = db.get_projects()
projects_number = len(projects)


st.title("Projects")
st.caption(f"Rate each project from 0 (lowest) to {projects_number } (highest). Your scores are private.")

st.divider()

cols = st.columns([4, 2, 1, 0.8])
cols[0].markdown("**Project**")
cols[1].markdown("**Keywords**")
cols[2].markdown("**Your score**")

st.divider()

for project in projects:
    pid = project.id
    score = st.session_state.ratings.get(pid)
    cols = st.columns([4, 2, 1, 0.8])

    cols[0].write(project.title)
    cols[1].write(project.projects_keywords)

    if score is not None:
        cols[2].markdown(
            f"<span style='background:#E1F5EE; color:#085041; padding:3px 10px; " +
            f"border-radius:6px; font-weight:500;'>{score}</span>",
            unsafe_allow_html=True,
        )

    else:
        cols[2].markdown(
            "<span style='color:#9CA3AF;'>—</span>",
            unsafe_allow_html=True,
            )

    if cols[3].button("Open", key=f"open_{pid}"):
        st.switch_page("project_detail")
