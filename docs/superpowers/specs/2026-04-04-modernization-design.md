# ZSAgenda Modernization Design

## Goal

Modernize the ZSAgenda Django app: merge existing upgrade branches, move to Django 5.2 LTS, containerize with Docker, and adopt modern Python tooling (pyproject.toml + uv).

## Merge Strategy

1. Merge `django51-compatibility-fix` into `master` — it is the superset of all work (includes `dj5` plus admin fix).
2. Create a new feature branch from merged `master` for all modernization work.

## Django 5.2 LTS Upgrade

- Change dependency from `django~=5.1.0` to `django>=5.2,<5.3`.
- Fix any deprecations introduced in 5.2 (expected to be minimal).
- Use Python 3.13 (latest stable).

## pyproject.toml + uv

Replace `requirements/` directory with a PEP 621 `pyproject.toml`:

```toml
[project]
name = "zsagenda"
version = "1.0.0"
description = "School registration time slot scheduler"
requires-python = ">=3.13"
dependencies = [
    "django>=5.2,<5.3",
    "gunicorn",
]

[dependency-groups]
dev = [
    "model-bakery",
    "pudb",
    "pylint",
    "pylint-django",
    "ruff",
]

[tool.pylint]
# existing config carried over

[tool.ruff]
# existing config carried over
```

- Remove `requirements/` directory.
- Remove mypy config and mypy-related dev dependencies.
- `uv.lock` checked into git.

## Settings Refactor

Split `zsagenda/zsagenda/settings.py` into:

```
zsagenda/zsagenda/settings/
├── __init__.py       # empty
├── base.py           # shared settings, secrets from env vars
├── dev.py            # imports base, sets dev overrides
└── production.py     # imports base, sets production overrides
```

### base.py

All shared configuration. Secrets read from environment:

```python
SECRET_KEY = os.environ["SECRET_KEY"]
```

Paths use a `DATA_DIR` base for mounted directories:

```python
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
```

Database, static root, logs, media all derive from `DATA_DIR`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DATA_DIR, "database", "db.sqlite3"),
    }
}
STATIC_ROOT = os.path.join(DATA_DIR, "static")
MEDIA_ROOT = os.path.join(DATA_DIR, "media")
```

Other settings (INSTALLED_APPS, MIDDLEWARE, TEMPLATES, etc.) remain as-is from the django51 branch.

`FORCE_REPORT_OPEN` defaults to `False` in base.

### dev.py

```python
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
FORCE_REPORT_OPEN = True  # convenient for development
```

Database can use a local path (default DATA_DIR = `<project>/data`).

### production.py

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ["zapis.skolanapohodu.cz"]

# Email (SMTP)
EMAIL_HOST = "..."
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = "..."
EMAIL_HOST_PASSWORD = "..."

REG_FORM_EMAIL_SENDER = "ZS Na Pohodu <noreply@zapis.skolanapohodu.cz>"
REG_FORM_EMAIL_REPLYTO = "ZS Na Pohodu <info@skolanapohodu.cz>"
REG_FORM_EMAIL_CC = ["info@skolanapohodu.cz"]
CONTACT_URL = "https://www.skolanapohodu.cz/kontakty/"
```

### Selection

`DJANGO_SETTINGS_MODULE` env var selects the profile. Defaults to `zsagenda.settings.production` in Docker.

## Docker

### Dockerfile

```dockerfile
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

CMD uv run gunicorn zsagenda.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

The CMD port and actual exposed port are controlled via env var at runtime through docker-compose.

### docker-compose.yml

```yaml
name: zsagenda
services:
  web:
    build: .
    env_file: .env
    ports:
      - "${PORT:-8000}:${PORT:-8000}"
    volumes:
      - ./data/database:/app/data/database
      - ./data/static:/app/data/static
      - ./data/media:/app/data/media
      - ./data/logs:/app/data/logs
    command: >
      uv run gunicorn zsagenda.wsgi:application
      --bind 0.0.0.0:${PORT:-8000}
      --workers 2
      --access-logfile /app/data/logs/access.log
      --error-logfile /app/data/logs/error.log
```

### .env.example

```
DJANGO_SETTINGS_MODULE=zsagenda.settings.production
SECRET_KEY=change-me
PORT=8000
```

## Container Mount Points

All host-mounted data lives under `/app/data/`:

| Path | Purpose |
|------|---------|
| `/app/data/database/` | SQLite database file |
| `/app/data/static/` | Collected static files (served by external web server) |
| `/app/data/media/` | User-uploaded media (future use) |
| `/app/data/logs/` | Gunicorn access and error logs |

## Cleanup

- Remove `requirements/` directory.
- Remove `local_settings.py` import from settings but don't delete the file.
- Remove mypy configs.
- Update `.gitignore` (add `.env`, `data/`, `uv.lock` — keep tracked, remove mypy references).
- Update `CLAUDE.md` to reflect new commands and structure.

## What's NOT Changing

- App code (regform models, views, forms, templates) — only what's needed for Django 5.2 compat.
- SQLite as the database engine.
- Bootstrap 4.2.1 frontend.
- Overall URL structure and functionality.
