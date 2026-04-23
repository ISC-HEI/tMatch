
import streamlit as st

from models.session import Session
from services.db import get_db
import pandas as pd

from utils.nav import protect

protect("manage_users")

db = get_db()

session: Session = st.session_state.session

users = db.get_users()

if "user_df" not in st.session_state:
    st.session_state.user_df = pd.DataFrame([
        {
            "ID": u.id,
            "LDAP UID": u.ldap_uid,
            "Role": (role := u.get_role(session.program_id)) and role.name,
        }
        for u in users
        if u.get_role(session.program_id)
    ]).set_index("ID")

df = st.session_state.user_df  # already indexed by ID

# Header
cols = st.columns([2, 3, 2, 1, 1])
for col, header in zip(cols, ["ID", "LDAP UID", "Role", "Edit", "Delete"]):
    col.markdown(f"**{header}**")

st.divider()

for user_id, row in df.iterrows():
    cols = st.columns([2, 3, 2, 1, 1])
    cols[0].write(user_id)
    cols[1].write(row["LDAP UID"])
    cols[2].write(row["Role"] or "—")

    if cols[3].button("✏️", key=f"edit_{user_id}"):
        st.session_state.editing_user = user_id

    if cols[4].button("🗑️", key=f"delete_{user_id}"):
        st.session_state.deleting_user = user_id


if "deleting_user" in st.session_state:
    uid = st.session_state.deleting_user
    ldap = df.loc[uid, "LDAP UID"]
    st.warning(f"Delete **{ldap}** (ID {uid})?")
    c1, c2 = st.columns(2)
    if c1.button("Confirm delete"):
        # your actual delete logic here, e.g.:
        # session.delete_user(uid)
        st.session_state.user_df = df.drop(index=uid)
        del st.session_state.deleting_user
        st.rerun()
    if c2.button("Cancel"):
        del st.session_state.deleting_user
        st.rerun()

# Edit form
if "editing_user" in st.session_state:
    uid = st.session_state.editing_user
    row = df.loc[uid]
    with st.form(key="edit_form"):
        st.markdown(f"**Editing {row['LDAP UID']}**")
        new_role = st.selectbox("Role", options=db.get_roles(),
                                index=["admin", "student", "teacher"].index(row["Role"]))
        if st.form_submit_button("Save"):
            st.session_state.user_df.at[uid, "Role"] = new_role
            del st.session_state.editing_user

            st.rerun()
