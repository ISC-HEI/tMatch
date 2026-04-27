import streamlit as st
from models.session import Session
from services.db import get_db
import pandas as pd
from utils.nav import protect

protect("manage_users")

db = get_db()

session: Session = st.session_state.session
program_id: int = st.session_state.program_id

users = db.get_users()

user_df = pd.DataFrame([
    {
        "ID": u.id,
        "LDAP UID": u.ldap_uid,
        "Roles": (roles := u.get_roles(program_id)) and [role.name for role in roles],
    }
    for u in users
    if not (len(u.get_roles(program_id)) == 0 and len(u.program_memberships) > 0) 
]).set_index("ID")

st.dataframe(user_df)
