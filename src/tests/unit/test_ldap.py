from unittest.mock import patch, MagicMock
import pytest
from services.ldap import (
    _get_server,
    _search_user,
    authenticate,
    get_email_by_uid,
)


@pytest.fixture(autouse=True)
def mock_logger():
    with patch("services.ldap.logger") as mock:
        yield mock


class TestSearchUser:
    """Tests for the _search_user function."""

    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_none_when_uid_empty(self, mock_conn_cls, mock_get_server):
        """Returns None when uid is empty."""
        result = _search_user("", attributes=["cn", "uid"])

        assert result is None
        mock_get_server.assert_not_called()

    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_none_when_user_not_found(self, mock_conn_cls, mock_get_server):
        """Returns None when LDAP entry not found."""
        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        mock_conn = MagicMock()
        mock_conn.entries = []
        mock_conn_cls.return_value = mock_conn

        result = _search_user("unknown", attributes=["cn", "uid"])

        assert result is None

    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_entry_when_user_found(self, mock_conn_cls, mock_get_server):
        """Returns Entry object when user is found."""
        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        mock_entry = MagicMock()
        mock_conn = MagicMock()
        mock_conn.entries = [mock_entry]
        mock_conn_cls.return_value = mock_conn

        result = _search_user("testuser", attributes=["cn", "uid"])

        assert result is mock_entry


class TestAuthenticate:
    """Tests for the authenticate function."""

    @patch("services.ldap._search_user")
    def test_returns_none_when_uid_empty(self, mock_search):
        """Returns None when uid is empty."""
        result = authenticate("", "password")

        assert result is None
        mock_search.assert_not_called()

    @patch("services.ldap._search_user")
    def test_returns_none_when_password_empty(self, mock_search):
        """Returns None when password is empty."""
        result = authenticate("uid", "")

        assert result is None
        mock_search.assert_not_called()

    @patch("services.ldap._search_user")
    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_none_when_user_not_found(self, mock_conn_cls, mock_get_server, mock_search):
        """Returns None when user doesn't exist in LDAP."""
        mock_search.return_value = None

        result = authenticate("unknown", "password")

        assert result is None

    @patch("services.ldap._search_user")
    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_none_when_password_invalid(self, mock_conn_cls, mock_get_server, mock_search):
        """Returns None when password is incorrect."""
        mock_entry = MagicMock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_entry.cn = "Test User"
        mock_entry.uid = "testuser"
        mock_search.return_value = mock_entry

        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        mock_auth_conn = MagicMock()
        mock_auth_conn.bind.return_value = False
        mock_conn_cls.return_value = mock_auth_conn

        result = authenticate("testuser", "wrongpassword")

        assert result is None

    @patch("services.ldap._search_user")
    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_dict_with_keys_on_success(self, mock_conn_cls, mock_get_server, mock_search):
        """Returns dict with dn, cn, uid keys when authentication succeeds."""
        mock_entry = MagicMock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_entry.cn = "Test User"
        mock_entry.uid = "testuser"
        mock_search.return_value = mock_entry

        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        mock_auth_conn = MagicMock()
        mock_auth_conn.bind.return_value = True
        mock_conn_cls.return_value = mock_auth_conn

        result = authenticate("testuser", "correctpassword")

        assert result is not None
        assert "dn" in result
        assert "cn" in result
        assert "uid" in result

    @patch("services.ldap._search_user")
    @patch("services.ldap._get_server")
    @patch("services.ldap.Connection")
    def test_returns_cn_as_none_when_missing(self, mock_conn_cls, mock_get_server, mock_search):
        """Returns None for cn when attribute is missing."""
        mock_entry = MagicMock()
        mock_entry.entry_dn = "uid=testuser,ou=users,dc=example,dc=com"
        mock_entry.cn = None
        mock_entry.uid = "testuser"
        mock_search.return_value = mock_entry

        mock_server = MagicMock()
        mock_get_server.return_value = mock_server

        mock_auth_conn = MagicMock()
        mock_auth_conn.bind.return_value = True
        mock_conn_cls.return_value = mock_auth_conn

        result = authenticate("testuser", "password")

        assert result is not None
        assert result["cn"] is None


class TestGetEmailByUid:
    """Tests for the get_email_by_uid function."""

    @patch("services.ldap._search_user")
    def test_returns_none_when_uid_empty(self, mock_search):
        """Returns None when uid is empty."""
        result = get_email_by_uid("")

        assert result is None
        mock_search.assert_not_called()

    @patch("services.ldap._search_user")
    def test_returns_email_string_when_found(self, mock_search):
        """Returns email as string when user is found."""
        mock_entry = MagicMock()
        mock_entry.mail = "testuser@example.com"
        mock_search.return_value = mock_entry

        result = get_email_by_uid("testuser")

        assert result == "testuser@example.com"

    @patch("services.ldap._search_user")
    def test_returns_none_when_user_not_found(self, mock_search):
        """Returns None when user doesn't exist."""
        mock_search.return_value = None

        result = get_email_by_uid("unknown")

        assert result is None

    @patch("services.ldap._search_user")
    def test_returns_none_when_mail_attribute_missing(self, mock_search):
        """Returns None when mail attribute is missing."""
        mock_entry = MagicMock()
        mock_entry.mail = None
        mock_search.return_value = mock_entry

        result = get_email_by_uid("testuser")

        assert result is None
