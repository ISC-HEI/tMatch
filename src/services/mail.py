
from collections.abc import Sequence
from dataclasses import dataclass, field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import streamlit as st
from jinja2 import Environment, FileSystemLoader

from models.project import Project
from models.user import User
from services.db import Db, get_db
from services.ldap import get_email_by_uid

env = Environment(loader=FileSystemLoader("emails/"))

@dataclass
class Mail:
    subject: str
    text_content: str
    html_content: str
    to: list[str]
    bcc: list[str] = field(default_factory=list)
    subtype: str = "plain"

class Mailer:
    """Email service for sending notifications."""

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
        """Notify a teacher that a project has been assigned to them.

        Args:
            project: The Project object.
        """
        
        subject: str = "Project Supervision"
        title: str = ""
        content: str = ""

        context = {
            "subject": subject,
            "title": title,
            "content": content,
            "button_text": "See Project"
        }

        template = env.get_template("email")
        html_content = template.render(**context)

        teacher_email = get_email_by_uid(project.teacher.ldap_uid)

        if teacher_email is None:
            return

        mail = Mail(
            f"{subject}",
            f"{title}\n{content}",
            html_content=html_content,
            to=[teacher_email]
        )

        self._send(mail)

    def project_creation(self, project: Project):
        """Notify students of a new project and inform the supervising teacher.

        Args:
            project: The Project object.
        """

        subject: str = ""
        title: str = ""
        content: str = ""

        context = {
            "subject": subject,
            "title": title,
            "content": content,
            "button_text": "See Project"
        }

        template = env.get_template("email")
        html_content = template.render(**context)

        self.project_supervision(project)

        db = get_db()

        students = db.get_students(project.program_id)

        student_emails = self._get_user_emails(students)

        mail = Mail(
            f"{subject}",
            f"{title}\n{content}",
            html_content=html_content,
            to=[self._sender],
            bcc=student_emails
        )

        self._send(mail)

    def students_reminder(self, students: list[User], urgent: bool = False):
        """Send a reminder email to students to rate projects.

        Args:
            students: List of User objects to remind.
            urgent: Whether the reminder is urgent.
        """

        subject: str = ""
        title: str = ""
        content: str = ""

        context = {
            "subject": subject,
            "title": title,
            "content": content,
            "button_text": "See Project"
        }

        template = env.get_template("email")
        html_content = template.render(**context)

        student_emails = self._get_user_emails(students)

        mail = Mail(
            f"{subject}",
            f"{title}\n{content}",
            html_content=html_content,
            to=[self._sender],
            bcc=student_emails
        )

        self._send(mail)

    def project_assignment(self, program_id: int):
        """Notify students and teachers of project assignments.

        Args:
            program_id: ID of the program.
        """

        db = get_db()

        self._project_assignment_students(program_id, db)
        self._project_assignment_teachers(program_id, db)

    def manual_rating_edit(self, project: Project, student: User):
        """Notify a student of a modification of one of their ratings.

        Args:
            project: Project target
            student: Student target
        """

        context = {}

        template = env.get_template("email")
        html_content = template.render(**context)

        mail = Mail(
            "Rating edit",
            f"Your rating on \"{project.title}\" was modified by the program director.",
            html_content=html_content,
            to=self._get_user_emails([student]),
            bcc=[]
        )

        self._send(mail)

    def _project_assignment_students(self, program_id: int, db: Db):
        """Notify students of project assignments

        Args:
            program_id: ID of the program
            db: database instance
        """

        subject: str = ""
        title: str = "You've been assigned a new project!"
        content: str = "Great news! The project assignments are in! Log in to the application to find out which project you've been matched with this year."

        context = {
            "subject": subject,
            "title": title,
            "content": content,
            "button_text": "See Project"
        }

        template = env.get_template("email")
        html_content = template.render(**context)

        students = db.get_students(program_id)

        mail = Mail(
            "Project Assignment",
            "Projects have been assigned to students. Please check which project has been assigned to you.",
            html_content=html_content,
            to=[self._sender],
            bcc=self._get_user_emails(students)
        )

        self._send(mail)

    def _project_assignment_teachers(self, program_id: int, db: Db):
        """Notify teachers of project assignments

        Args:
            program_id: ID of the program
            db: database instance
        """

        subject: str = ""
        title: str = ""
        content: str = ""

        context = {
            "subject": subject,
            "title": title,
            "content": content,
            "button_text": "See Project"
        }

        template = env.get_template("email")
        html_content = template.render(**context)

        teachers = db.get_teachers(program_id)

        mail = Mail(
            "Projects assignment",
            "Projects have been assigned to students. Please check which students you'll work with.",
            html_content=html_content,
            to=[self._sender],
            bcc=self._get_user_emails(teachers)
        )

        self._send(mail)



    def _get_user_emails(self, users: list[User]|Sequence[User]):
        """Get email addresses for a list of users.

        Args:
            users: List of User objects.

        Returns:
            List of email addresses.
        """


        return [
            email for user in users
            if (email := get_email_by_uid(user.ldap_uid)) is not None
        ]

    def _send(self, mail: Mail) -> None:
        """Send an email.

        Args:
            mail: The Mail object to send.
        """

        all_recipents = mail.to + mail.bcc

        msg = MIMEMultipart("alternative")
        msg["Subject"] = mail.subject
        msg["From"] = self._sender
        msg["To"] = ", ".join(mail.to)

        text_part = MIMEText(mail.text_content, "plain")
        html_part = MIMEText(mail.html_content, "html")

        msg.attach(text_part)
        msg.attach(html_part)

        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_3

        with smtplib.SMTP(self._server, self._port, timeout=10) as smtp:
            smtp.starttls(context=context)
            smtp.login(self._username, self._password)

            smtp.sendmail(self._sender, all_recipents, msg.as_string())
