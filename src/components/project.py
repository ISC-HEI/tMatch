
import streamlit as st
from components.keywords import render_keywords
from models.project import Project


def show_project(project: Project):
    st.divider()
 
    st.title(project.title)
    render_keywords(project.projects_keywords)

    st.markdown(
        f"<p style='color:#9CA3AF; font-size:0.9rem; margin-top:4px;'>" +
        f"👤 Supervised by <strong style='color:#F9FAFB;'>{project.teacher.ldap_uid}</strong>" +
        f"</p>",
        unsafe_allow_html=True,
    )

    for paragraph in project.description.split("\n"):
        st.write(paragraph)

    st.divider()
