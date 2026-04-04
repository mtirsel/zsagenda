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

EXPOSE ${PORT:-8000}

ENTRYPOINT ["./entrypoint.sh"]
CMD uv run gunicorn zsagenda.wsgi:application --chdir zsagenda --bind 0.0.0.0:${PORT:-8000}
