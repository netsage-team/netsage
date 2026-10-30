#!/bin/sh
set -eu

# Apply database migrations before accepting web requests.
echo "Applying Django database migrations..."
python manage.py migrate --noinput

# Replace the shell with Gunicorn for proper signal handling.
echo "Starting NetSage..."
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8000}"
