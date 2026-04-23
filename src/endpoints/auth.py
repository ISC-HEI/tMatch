
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import RedirectResponse

from services.db import get_db

async def create_session(request: Request):
    token = request.query_params.get("token")
    if not token:
        return RedirectResponse("/")

    db = get_db()
    auth_token = db.get_auth_token(token)

    if (
        auth_token is None
        or auth_token.expires_at < datetime.now(timezone.utc)
    ):
        return RedirectResponse("/")

    db.remove(auth_token)

    session = db.create_session(auth_token.user_id, auth_token.program_id)

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
