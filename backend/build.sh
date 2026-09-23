#!/usr/bin/env bash
# Render build script for SkillMap AI backend
# This runs during the Render build phase (not the start phase).
set -euo pipefail

echo ">>> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ">>> Collecting static files..."
python manage.py collectstatic --noinput

echo ">>> Running database migrations..."
python manage.py migrate --noinput

echo ">>> Build complete."
