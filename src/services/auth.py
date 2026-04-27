
from datetime import datetime, timezone
import streamlit as st

from models.session import Session
from models.user import User
from services.db import get_db
from services.ldap import authenticate

db = get_db()

def create_session(user: User, program_id: int):
    auth_token = db.create_auth_token(user.id, program_id)
    st.markdown(f'<meta http-equiv="refresh" content="0;url=/auth/create_session?token={auth_token.id}">', unsafe_allow_html=True)

def logout(session: Session) -> None:
    db.remove(session)


def login(email: str, password: str, program_id: int) -> User|None:
    user_infos = authenticate(email, password)

    if user_infos is None or user_infos["uid"] is None:
        return None

    user = db.get_user(user_infos["uid"])
    
    create_session(user, program_id)

    return user

def validate_session() -> Session|None:
    cookies = st.context.cookies
    
    if "sid" not in cookies:
        return None

    sid = cookies["sid"]
    session = db.get_session(sid)

    if session is None:
        return None

    if session.expires_at < datetime.now(timezone.utc):
        db.remove(session)
        return None

    return session
