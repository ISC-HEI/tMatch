
import streamlit as st

from components.keywords import render_keywords
from models.project import Project
from services.db import get_db
from utils.nav import allowed, projects_page, protect

protect("project_detail")

db = get_db()

user = st.session_state.user

program = db.get_program(st.session_state.program_id)
projects = program.projects if program is not None else []
projects_number = len(projects)

roles = user.get_roles(st.session_state.program_id)

if "selected_project" in st.session_state and st.session_state.selected_project is not None and (p := db.get_project(st.session_state.selected_project)):
    project: Project = p
else:
    project = projects[0]

if "edit_rating" not in st.session_state:
    st.session_state.edit_rating = False

if "edit_project" not in st.session_state:
    st.session_state.edit_project = False

if "confirm_delete" not in st.session_state:
    st.session_state.confirm_delete = False

pid = project.id
rating = project.get_rating_from(user.id)
already_rated = rating is not None

with st.container(horizontal=True):
    if st.button("← Back to projects"):
        st.switch_page(projects_page)
    
    st.space("stretch")

    if allowed(roles, ["secretary", "teacher"]) and st.button("Edit"):
        st.session_state.edit_project = True
        st.rerun()

    if allowed(roles, ["secretary", "teacher"]) and st.button("Delete"):
        st.session_state.confirm_delete = True
        st.rerun()

if st.session_state.edit_project:
    with st.form("edit_project_form"):
        st.subheader("Edit Project")
        title = st.text_input("Title", value=project.title)
        description = st.text_area("Description", value=project.description, height=200)
        teachers = db.get_teachers(st.session_state.program_id)
        teachers_map = {t.id: t for t in teachers}
        teacher_id = st.selectbox(
            "Teacher",
            teachers_map,
            index=list(teachers_map.keys()).index(project.teacher_id),
            format_func=lambda tid: teachers_map[tid].ldap_uid,
        )

        all_keywords = db.get_keywords()
        keyword_id_map = {k.id: k.name for k in all_keywords}
        keyword_name_map = {k.name: k.id for k in all_keywords}

        edit_key = f"edit_keywords_{project.id}"
        if edit_key not in st.session_state:
            st.session_state[edit_key] = [pk.keyword.id for pk in project.projects_keywords]

        search = st.text_input("Search keywords", key="keyword_search", placeholder="Type to filter keywords...")

        selected_ids = st.session_state[edit_key]
        selected_names = [keyword_id_map[kid] for kid in selected_ids if kid in keyword_id_map]

        if search:
            filtered_names = [k.name for k in all_keywords if search.lower() in k.name.lower()]
            display_names = sorted(set(filtered_names + selected_names))
        else:
            display_names = sorted(keyword_name_map.keys())

        chosen_names = st.multiselect(
            "Keywords",
            options=display_names,
            default=selected_names,
            help="Search above to filter keywords. Selected keywords remain visible.",
        )

        st.session_state[edit_key] = [keyword_name_map[name] for name in chosen_names]

        with st.container(horizontal=True):
            if st.form_submit_button("Save"):
                result = db.update_project(project.id, title, description, teacher_id)
                if result:
                    db.update_project_keywords(project.id, st.session_state[edit_key])
                    del st.session_state[edit_key]
                    st.session_state.edit_project = False
                    st.rerun()
                else:
                    st.error("Failed to update project. Title may already exist.")

            st.space("stretch")

            if st.form_submit_button("Cancel"):
                if edit_key in st.session_state:
                    del st.session_state[edit_key]
                st.session_state.edit_project = False
                st.rerun()

if st.session_state.confirm_delete:
    st.warning("Are you sure you want to delete this project? This action cannot be undone.")

    with st.container(horizontal=True):
        if st.button("Confirm Delete", type="primary"):
            db.remove(project)
            st.session_state.confirm_delete = False
            st.switch_page(projects_page)

        st.space("stretch")

        if st.button("Cancel"):
            st.session_state.confirm_delete = False
            st.rerun()

 
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

if allowed(roles, ["student"]):
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
