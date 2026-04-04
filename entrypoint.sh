#!/bin/sh
set -e

# Create data directories if they don't exist
mkdir -p /app/data/database /app/data/static /app/data/media /app/data/logs

# Run migrations
uv run python zsagenda/manage.py migrate --noinput

# Collect static files into mounted volume
uv run python zsagenda/manage.py collectstatic --noinput

exec "$@"
