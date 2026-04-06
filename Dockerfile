FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ARG APP_UID=1000
ARG APP_GID=1000

# Create app user with configurable UID/GID (defaults match common setups)
RUN groupadd -f -g ${APP_GID} appuser && \
    useradd -u ${APP_UID} -g ${APP_GID} -m appuser

WORKDIR /app

# Install dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

RUN mkdir -p /app/data/static /app/data/media /app/data/logs /app/data/database && \
    chown -R appuser:appuser /app

ENV PYTHONPATH=/app/zsagenda
ENV DJANGO_SETTINGS_MODULE=zsagenda.settings.production
ENV DJANGO_DATA_DIR=/app/data
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE ${APP_PORT:-8000}

USER appuser

WORKDIR /app/zsagenda
# ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "zsagenda.wsgi:application", "--bind", "0.0.0.0:8000"]
