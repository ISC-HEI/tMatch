
#!/bin/sh
set -e

echo "Running migrations..."
uv run alembic upgrade head

echo "Seeding database..."
uv run python seed.py

echo "Starting app..."
exec uv run streamlit run main.py
