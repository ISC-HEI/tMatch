
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
import ssl
import streamlit as st

from models.project import Project
from services.ldap import get_email_by_uid

@dataclass
class Mail:
    subject: str
    content: str
    to: str
    subtype: str = "plain"

class Mailer:
    _server: str
    _port: int
    _username: str
    _password: str
    _sender: str

    def __init__(self) -> None:
        self._server = st.secrets.mailer.smtpserver
        self._port = st.secrets.mailer.smtpserverport
        self._username = st.secrets.mailer.smtpusername
        self._password = st.secrets.mailer.smtppassword
        self._sender = st.secrets.mailer.sender

    def project_creation(self, project: Project):
        teacher_email = get_email_by_uid(project.teacher.ldap_uid)

        if teacher_email is None:
            return

        mail = Mail(
            f"New project created and supervised by you",
            f"A new project as been set as supervised by you :\n{project.title}",
            teacher_email
        )

        self._send(mail)

    def _send(self, mail: Mail) -> None:
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        with smtplib.SMTP(self._server, self._port, timeout=10) as smtp:
            smtp.starttls(context=context)
            smtp.login(self._username, self._password)

            msg = MIMEText(mail.content, mail.subtype)
            msg["Subject"] = mail.subject
            msg["From"] = self._sender

            smtp.sendmail(self._sender, mail.to, msg.as_string())
