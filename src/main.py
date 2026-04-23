from streamlit.starlette import App
from starlette.routing import Route
from endpoints.auth import create_session

app = App("app.py", routes=[
    Route("/auth/create_session", create_session)
])
