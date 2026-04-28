
from dataclasses import dataclass, field
import smtplib
from email.mime.text import MIMEText
import ssl
import streamlit as st

from models.project import Project
from services.db import get_db
from services.ldap import get_email_by_uid

@dataclass
class Mail:
    subject: str
    content: str
    to: list[str]
    bcc: list[str] = field(default_factory=list)
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

    def project_supervision(self, project: Project):
        teacher_email = get_email_by_uid(project.teacher.ldap_uid)

        if teacher_email is None:
            return

        mail = Mail(
            f"New project supervised by you",
            f"A new project as been set as supervised by you :\n{project.title}",
            to=[teacher_email]
        )

        self._send(mail)

    def project_creation(self, project: Project):
        self.project_supervision(project)

        db = get_db()

        students = db.get_students(project.program_id)

        student_emails = [
            email for student in students
            if (email := get_email_by_uid(student.ldap_uid)) is not None
        ]

        mail = Mail(
            f"New project created",
            f"A new project has been created, please rate it and adjust previous ratings if needed :\n{project.title}",
            to=[self._sender],
            bcc=student_emails
        )

        self._send(mail)

    def _send(self, mail: Mail) -> None:
        all_recipents = mail.to + mail.bcc

        msg = MIMEText(mail.content, mail.subtype)
        msg["Subject"] = mail.subject
        msg["From"] = self._sender
        msg["To"] = ", ".join(mail.to)

        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        with smtplib.SMTP(self._server, self._port, timeout=10) as smtp:
            smtp.starttls(context=context)
            smtp.login(self._username, self._password)

            smtp.sendmail(self._sender, all_recipents, msg.as_string())
