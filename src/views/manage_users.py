import streamlit as st
from models.session import Session
from services.db import get_db
import pandas as pd
from utils.nav import protect

protect("manage_users")

db = get_db()

session: Session = st.session_state.session

users = db.get_users()

user_df = pd.DataFrame([
    {
        "ID": u.id,
        "LDAP UID": u.ldap_uid,
        "Role": (role := u.get_role(session.program_id)) and role.name,
    }
    for u in users
    if u.get_role(session.program_id)
]).set_index("ID")

st.dataframe(user_df)
