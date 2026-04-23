from ldap3 import Entry, Server, Connection, ALL

LDAP_HOST = "ipa.example.test"
LDAP_BASE_DN = "cn=users,cn=accounts,dc=example,dc=test"
LDAP_PORT = 636


def _get_server():
    return Server(LDAP_HOST, port=LDAP_PORT, use_ssl=True, get_info=ALL)


def authenticate(uid: str, password: str) -> dict[str, str|None] | None:
    if not uid or not password:
        return None

    try:
        server = _get_server()
        conn = Connection(server, auto_bind=True)

        conn.search(
            LDAP_BASE_DN,
            f"(uid={uid})",
            "SUBTREE",
            attributes=["cn", "uid"],
        )

        if not conn.entries:
            conn.unbind()
            return None

        entry: Entry = conn.entries[0]
        user_dn = entry.entry_dn

        conn.unbind()

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
