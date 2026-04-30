
import streamlit as st

from components.project import show_project
from models.user import User
from services.db import get_db
from utils.nav import protect

protect("assigned_project")

db = get_db()

user: User = st.session_state.user

if user.project is not None:
    show_project(user.project)

else:
    st.info("No projects have been assigned to you yet.")
