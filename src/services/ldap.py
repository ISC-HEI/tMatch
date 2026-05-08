
from config import LDAP_BASE_DN, LDAP_HOST, LDAP_PASSWORD, LDAP_PORT, LDAP_USER
from ldap3 import Entry, Server, Connection, ALL

def _get_server():
    return Server(LDAP_HOST, port=int(LDAP_PORT), use_ssl=True, get_info=ALL)


def _search_user(uid: str, attributes: list[str]) -> Entry | None:
    """Search for a user by UID in LDAP.

    Args:
        uid: The LDAP UID to search for.
        attributes: List of LDAP attributes to retrieve.

    Returns:
        The LDAP Entry if found, None otherwise.
    """

    if not uid or uid == "":
        return None
    try:
        server = _get_server()
        conn = Connection(server, user=LDAP_USER, password=LDAP_PASSWORD, auto_bind=True)
        conn.search(LDAP_BASE_DN, f"(uid={uid})", "SUBTREE", attributes=attributes)
        entry = conn.entries[0] if conn.entries else None
        conn.unbind()
        return entry
    except Exception as e:
        print(e)
        return None


def authenticate(uid: str, password: str) -> dict[str, str|None] | None:
    """Authenticate a user against LDAP.

    Args:
        uid: The LDAP UID of the user.
        password: The user's password.

    Returns:
        A dictionary with user info (dn, cn, uid) if authenticated, None otherwise.
    """

    if not uid or not password:
        return None

    try:
        entry = _search_user(uid, attributes=["cn", "uid"])
        if not entry:
            return None

        user_dn = entry.entry_dn

        server = _get_server()
        auth_conn = Connection(server, user=user_dn, password=password)
        if not auth_conn.bind():
            auth_conn.unbind()
            return None

        user_info: dict[str, str|None] = {
            "dn": user_dn,
            "cn": str(entry.cn) if entry.cn else None,
            "uid": str(entry.uid) if entry.uid else uid,
        }

        auth_conn.unbind()
        return user_info

    except Exception as e:
        print(e)
        return None


def get_email_by_uid(uid: str) -> str | None:
    """Get the email address of a user by their UID.

    Args:
        uid: The LDAP UID of the user.

    Returns:
        The email address if found, None otherwise.
    """

    if uid == "":
        return None

    entry = _search_user(uid, attributes=["mail"])
    return str(entry.mail) if entry and entry.mail else None
