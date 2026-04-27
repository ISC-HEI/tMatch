
import streamlit as st
from models.projects_keyword import ProjectsKeyword


def render_keywords(project_keywords: list[ProjectsKeyword]): 
    with st.container(horizontal=True):
        for label in [pk.keyword.name for pk in project_keywords]:
            st.badge(label, color="blue")

        st.space("stretch")

 
