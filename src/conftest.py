import pytest
from unittest.mock import MagicMock


@pytest.fixture(autouse=True)
def mock_streamlit_secrets():
    mock_secrets = MagicMock()
    mock_secrets.ldap = MagicMock()
    mock_secrets.ldap.ldaphost = "ldaps://ldap.example.com"
    mock_secrets.ldap.ldapport = "636"
    mock_secrets.ldap.ldapaccount = "cn=admin,dc=example,dc=com"
    mock_secrets.ldap.ldappassword = "password"
    mock_secrets.ldap.ldapbasedn = "dc=example,dc=com"

    mock_secrets.mailer = MagicMock()
    mock_secrets.mailer.smtpserver = "smtp.example.com"
    mock_secrets.mailer.smtpserverport = "587"
    mock_secrets.mailer.smtpusername = "user"
    mock_secrets.mailer.smtppassword = "password"
    mock_secrets.mailer.sender = "sender@example.com"

    import streamlit as st
    st.secrets = mock_secrets