
from dataclasses import dataclass
from smtplib import SMTP_SSL as SMTP
from email.mime.text import MIMEText
import streamlit as st

@dataclass
class Mail:
    subject: str
    content: str
    to: str
    subtype: str = "plain"

class Mailer:
    _server: str
    _username: str
    _password: str
    _sender: str

    def __init__(self) -> None:
        self._server = st.secrets.mailer.smtpserver
        self._username = st.secrets.mailer.smtpusername
        self._password = st.secrets.mailer.smtppassword
        self._sender = st.secrets.mailer.sender

    def send(self, mail: Mail) -> None:
        msg = MIMEText(mail.content, mail.subtype)
        msg["Subject"] = mail.subject
        msg["From"] = self._sender

        conn = SMTP(self._server)
        conn.set_debuglevel(0)
        conn.login(self._username, self._password)

        try:
            conn.sendmail(self._sender, mail.to, msg.as_string())

        finally:
            conn.quit()
