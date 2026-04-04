FROM python:3.13-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

# Copy application
COPY zsagenda/ ./zsagenda/
COPY entrypoint.sh ./

# Create app user with configurable UID/GID (defaults match common setups)
ARG APP_UID=1000
ARG APP_GID=1000
RUN groupadd -g ${APP_GID} app && \
    useradd -u ${APP_UID} -g app -d /app -s /bin/sh app && \
    chown -R app:app /app

USER app

EXPOSE ${PORT:-8000}

ENTRYPOINT ["./entrypoint.sh"]
CMD uv run gunicorn zsagenda.wsgi:application --chdir zsagenda --bind 0.0.0.0:${PORT:-8000}
