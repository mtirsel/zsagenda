FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Copy application
COPY zsagenda/ ./zsagenda/

# Collect static files (requires SECRET_KEY at build time)
ARG SECRET_KEY=build-placeholder
RUN DJANGO_SETTINGS_MODULE=zsagenda.settings.production \
    SECRET_KEY=${SECRET_KEY} \
    uv run python zsagenda/manage.py collectstatic --noinput

EXPOSE ${PORT:-8000}

CMD uv run gunicorn zsagenda.wsgi:application --chdir zsagenda --bind 0.0.0.0:${PORT:-8000}
