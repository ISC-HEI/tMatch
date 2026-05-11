from pathlib import Path
import streamlit as st
import yaml

from services.db import get_db
from services.mail import Mailer
from utils.nav import protect
from utils.logger import logger

protect("manage_projects")

db = get_db()

st.title("Create Projects")

mode: str = st.selectbox(
    "Mode",
    ("from file", "manual"),
    index=0,
)

st.text(mode)

with st.form("add_form"):
    teachers = db.get_teachers(st.session_state.program_id)
    teachers_map = { t.id: t for t in teachers }
    
    project_file = None
    title = ""
    description = ""
    specs = None
    teacher_id: int = 0

    if mode == "from file":
        project_file = st.file_uploader("Project file", type=["yaml"], key="pf")

        teacher_id = st.selectbox(
            "Teacher",
            teachers_map,
            format_func=lambda teacher_id: teachers_map[teacher_id].ldap_uid,
            index=0,
        )

        specs = st.file_uploader("Specifications", type=["pdf"], key="specs")

    else:
        title = st.text_input("Title", key="title")
        description = st.text_input("Description", key="description")
        teacher_id = st.selectbox(
            "Teacher",
            teachers_map,
            format_func=lambda teacher_id: teachers_map[teacher_id].ldap_uid,
            index=0,
        )
        specs = st.file_uploader("Specifications", type=["pdf"], key="specs")

    sb = st.form_submit_button("Create project", key="submit_btn")

    if sb and mode == "from file" and project_file is not None and specs is not None:
        project_dict = yaml.load(project_file.getvalue(), yaml.BaseLoader)
        
        if "title" not in project_dict or "description" not in project_dict:
            st.error("Invalid yaml file, missing required properties !")

        else:
            specs_dir = Path("specs")
            specs_dir.mkdir(exist_ok=True)
        
            filename = f"{specs.name}"
            filepath = specs_dir / filename

            with open(filepath, "wb") as f:
                f.write(specs.getvalue())

            project = db.create_project(st.session_state.user.id, teacher_id, project_dict["title"], project_dict["description"], f"specs/{specs.name}", st.session_state.program_id)

            if project:
                logger.info(f"Project created: {project_dict['title']}")
                st.success("Project created successfully !")
                mailer = Mailer()
                mailer.project_creation(project)

            else:
                logger.warn(f"Project creation failed: {project_dict['title']}")
                st.error("Project already exists !")

    elif sb and mode == "manual" and specs is not None and description != "" and title != "":
        specs_dir = Path("specs")
        specs_dir.mkdir(exist_ok=True)
        
        filename = f"{specs.name}"
        filepath = specs_dir / filename

        with open(filepath, "wb") as f:
            f.write(specs.getvalue())

        project = db.create_project(
            st.session_state.user.id, teacher_id, title, description, f"specs/{specs.name}", st.session_state.program_id
        )

        if project:
            logger.info(f"Project created: {title}")
            st.success("Project created successfully !")
            mailer = Mailer()
            mailer.project_creation(project)

        else:
            logger.warn(f"Project creation failed: {title}")
            st.error("Project already exists !")

    elif sb and mode == "manual" and ( specs is None or description == "" or title == "" ):
        st.error("Missing required inputs !")

    elif sb and mode == "from file" and ( project_file is None or specs is None ):
        st.error("Missing required inputs !")
