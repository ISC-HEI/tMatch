
from datetime import datetime, timezone
import streamlit as st

from models.session import Session
from models.user import User
from services.db import get_db
from services.ldap import authenticate
from utils.logger import logger

db = get_db()

def create_session(user: User):
    """Create a session for a user by redirecting to the auth endpoint.

    Args:
        user: The User object to create a session for.
    """

    auth_token = db.create_auth_token(user.id)
    st.markdown(f'<meta http-equiv="refresh" content="0;url=/auth/create_session?token={auth_token.id}">', unsafe_allow_html=True)

def logout(session: Session) -> None:
    """Log out a user by removing their session.

    Args:
        session: The Session object to remove.
    """

    db.remove(session)
    logger.info(f"User logged out: {session.user.ldap_uid}")


def login(uid: str, password: str) -> User|None:
    """Log in a user with LDAP credentials.

    Args:
        uid: The LDAP UID of the user.
        password: The user's password.

    Returns:
        The User object if login successful, None otherwise.
    """

    user_infos = authenticate(uid, password)

    if user_infos is None or user_infos["uid"] is None:
        logger.warn(f"Login failed for user: {uid}")
        return None

    user = db.get_user(user_infos["uid"])

    create_session(user)

    logger.info(f"User logged in: {uid}")

    return user

def validate_session() -> Session|None:
    """Validate the current session from cookies.

    Returns:
        The Session object if valid, None otherwise.
    """

    cookies = st.context.cookies
    
    if "sid" not in cookies:
        return None

    sid = cookies["sid"]
    session = db.get_session(sid)

    if session is None:
        return None

    if session.expires_at < datetime.now(timezone.utc):
        logger.info(f"Session expired, removed for user: {session.user.ldap_uid}")
        db.remove(session)
        return None

    return session
