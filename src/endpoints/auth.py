
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import RedirectResponse

from services.db import get_db
from utils.logger import logger

async def create_session(request: Request):
    """Create a session from an auth token.

    Validates the token, creates a session, and sets a cookie.

    Args:
        request: The HTTP request.

    Returns:
        Redirect to home on success or failure.
    """

    token = request.query_params.get("token")
    if not token:
        logger.warn("Auth endpoint: missing token")
        return RedirectResponse("/")

    db = get_db()
    auth_token = db.get_auth_token(token)

    if (
        auth_token is None
        or auth_token.expires_at < datetime.now(timezone.utc)
    ):
        logger.warn("Auth endpoint: token expired or invalid")
        return RedirectResponse("/")

    db.remove(auth_token)

    session = db.create_session(auth_token.user_id)
    logger.info(f"Session created for user_id: {auth_token.user_id}")

    response = RedirectResponse("/")
    response.set_cookie(
        key="sid",
        value=str(session.id),
        httponly=True,
        secure=True, 
        samesite="strict",
        max_age=60*60*24*7 #7 days
    )
    return response
