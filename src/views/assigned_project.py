
from collections.abc import Sequence
import streamlit as st

from components.project import show_project
from models.user import User
from services.db import get_db
from utils.nav import allowed, protect
import pandas as pd

protect("assigned_project")

db = get_db()

user: User = st.session_state.user
roles = user.get_roles(st.session_state.program_id)

def get_assignment_dataframe(students: Sequence[User]) -> pd.DataFrame:
    """
    Build a DataFrame of project assignments from a list of student User objects.
    Each student must have: uid, display_name (or cn), and project (can be None).
    """
    rows = []
    for student in students:
        project = student.project
        rows.append({
            "Student ID":   student.ldap_uid,
            "Project ID":   project.id   if project else None,
            "Project Title":project.title if project else "⚠️ Not assigned",
            "Supervisor":   project.teacher.ldap_uid if project else "—",
        })

    df = pd.DataFrame(rows)
    return df


def show_assignments(students: Sequence[User]):
    st.title("Project Assignments")

    df = get_assignment_dataframe(students)

    total      = len(df)
    assigned   = df["Project ID"].notna().sum()
    unassigned = total - assigned

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Students",    total)
    col2.metric("Assigned",          assigned)
    col3.metric("⚠️ Not Assigned",   unassigned)

    filter_unassigned = st.checkbox("Show only unassigned students")
    if filter_unassigned:
        df = df[df["Project ID"].isna()]

    def highlight_unassigned(row: pd.Series):
        color = "background-color: #4A000D" if pd.isna(row["Project ID"]) else ""
        return [color] * len(row)

    st.dataframe(
        df.style.apply(highlight_unassigned, axis=1),
        width="stretch",
        hide_index=True,
    )

def students_view():
    if user.project is not None:
        show_project(user.project)

    else:
        st.info("No projects have been assigned to you yet.")

def director_view():
    show_assignments(db.get_students(st.session_state.program_id))

if allowed(roles, ["program director"]):
    director_view()

elif allowed(roles, ["student"]):
    students_view()

