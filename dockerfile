
FROM python:3.14-slim-bookworm

COPY --from=docker.io/astral/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
  UV_LINK_MODE=copy \
  UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY src/pyproject.toml src/uv.lock .
RUN uv sync --frozen --no-install-project

COPY src/* .

RUN uv sync --frozen

CMD ["uv", "run", "streamlit", "run", "main.py"]

