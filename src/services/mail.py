
from collections.abc import Sequence
from dataclasses import dataclass, field
import smtplib
from email.mime.text import MIMEText
import ssl
import streamlit as st

from models.project import Project
from models.user import User
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

        student_emails = self._get_user_emails(students)

        mail = Mail(
            f"New project created",
            f"A new project has been created, please rate it and adjust previous ratings if needed :\n{project.title}",
            to=[self._sender],
            bcc=student_emails
        )

        self._send(mail)

    def students_reminder(self, students: list[User], urgent: bool = False):
        student_emails = self._get_user_emails(students)

        mail = Mail(
            f"Project rating reminder {'[URGENT]' if urgent else ''}",
            f"Do not forget to rate all projects. Please proceed as soon as possible to maximize your chances to get one you like.",
            to=[self._sender],
            bcc=student_emails
        )

        self._send(mail)

    def project_assignment(self, program_id: int):
        db = get_db()

        students = db.get_students(program_id)
        teachers = db.get_teachers(program_id)

        student_mail = Mail(
            "Project assignment",
            "Projects have been assigned to students. Please check which project has been assigned to you.",
            to=[self._sender],
            bcc=self._get_user_emails(students)
        )

        teacher_mail = Mail(
            "Projects assignment",
            "Projects have been assigned to students. Please check which students you'll work with.",
            to=[self._sender],
            bcc=self._get_user_emails(teachers)
        )

        self._send(student_mail)
        self._send(teacher_mail)

    def _get_user_emails(self, users: list[User]|Sequence[User]):
        return [
            email for user in users
            if (email := get_email_by_uid(user.ldap_uid)) is not None
        ]

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
