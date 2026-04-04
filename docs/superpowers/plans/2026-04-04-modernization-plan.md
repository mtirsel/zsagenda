# ZSAgenda Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Merge Django upgrade branches, upgrade to Django 5.2 LTS, containerize with Docker, and adopt pyproject.toml + uv tooling.

**Architecture:** Single Django app with settings split into base/dev/production profiles, secrets via env vars, SQLite with volume-mounted data directory, Gunicorn in a Docker container.

**Tech Stack:** Python 3.13, Django 5.2 LTS, Gunicorn, uv, Docker

**Spec:** `docs/superpowers/specs/2026-04-04-modernization-design.md`

---

## File Structure

After all tasks are complete, the project root will look like:

```
zsagenda/                          # repo root
├── pyproject.toml                 # NEW — full PEP 621 project config
├── uv.lock                        # NEW — locked dependencies
├── Dockerfile                     # NEW
├── docker-compose.yml             # NEW
├── .env.example                   # NEW
├── .gitignore                     # MODIFIED
├── CLAUDE.md                      # MODIFIED
└── zsagenda/                      # Django project root (manage.py lives here)
    ├── manage.py                  # MODIFIED (settings module default)
    ├── zsagenda/
    │   ├── settings/              # NEW directory (replaces settings.py)
    │   │   ├── __init__.py        # NEW — empty
    │   │   ├── base.py            # NEW — shared settings
    │   │   ├── dev.py             # NEW — dev overrides
    │   │   └── production.py      # NEW — production overrides
    │   ├── settings.py            # DELETED
    │   ├── urls.py                # UNCHANGED
    │   ├── wsgi.py                # MODIFIED (settings module default)
    │   └── local_settings.py      # KEPT — not deleted, not imported
    ├── regform/                   # UNCHANGED (except Django 5.2 compat if needed)
    ├── templates/                 # UNCHANGED
    └── project_static_files/      # UNCHANGED
```

Removed files:
- `requirements/base.txt`, `requirements/dev.txt`, `requirements/beta.txt`, `requirements/production.txt`

---

### Task 1: Merge Branches Into Master

**Context:** `django51-compatibility-fix` is a superset of `dj5`, which itself contains all `master` and `production` commits. We merge it into `master`.

- [ ] **Step 1: Merge django51-compatibility-fix into master**

```bash
git checkout master
git merge origin/django51-compatibility-fix -m "Merge django51-compatibility-fix into master"
```

Expected: clean merge (django51-compatibility-fix is ahead of master, no conflicts expected).

- [ ] **Step 2: Verify the merge**

```bash
git log --oneline -5
```

Expected: merge commit at top, followed by `3d34178 Revert: Restore...` and `2f7e4b6 Formatting and small fixes.`

- [ ] **Step 3: Create feature branch for modernization**

```bash
git checkout -b modernize
```

---

### Task 2: Create pyproject.toml and Set Up uv

**Files:**
- Create: `pyproject.toml`
- Delete: `requirements/base.txt`, `requirements/dev.txt`, `requirements/beta.txt`, `requirements/production.txt`

- [ ] **Step 1: Create pyproject.toml**

Write `pyproject.toml` at repo root with this content:

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
max-line-length = 120
disable = [
    "C0111",
    "C0103",
    "C0114",
    "C0115",
    "C0116",
    "R0903",
]
django-settings-module = "zsagenda.settings.base"
load-plugins = "pylint_django"

[tool.ruff]
line-length = 120

[tool.ruff.lint]
select = ["E", "F", "B"]
ignore = ["E501"]
```

- [ ] **Step 2: Remove requirements directory**

```bash
rm -rf requirements/
```

- [ ] **Step 3: Generate lock file**

```bash
uv lock
```

Expected: `uv.lock` created with resolved dependencies including Django 5.2.x.

- [ ] **Step 4: Install dependencies and verify**

```bash
uv sync
uv run python -c "import django; print(django.VERSION)"
```

Expected: Django version tuple starting with `(5, 2, ...)`.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock
git rm -r requirements/
git commit -m "Replace requirements/ with pyproject.toml + uv

Adopt PEP 621 project config. Use uv for dependency management.
Upgrade Django from 5.1 to 5.2 LTS. Remove mypy config."
```

---

### Task 3: Refactor Settings Into base/dev/production

**Files:**
- Create: `zsagenda/zsagenda/settings/__init__.py`
- Create: `zsagenda/zsagenda/settings/base.py`
- Create: `zsagenda/zsagenda/settings/dev.py`
- Create: `zsagenda/zsagenda/settings/production.py`
- Delete: `zsagenda/zsagenda/settings.py`
- Modify: `zsagenda/manage.py`
- Modify: `zsagenda/zsagenda/wsgi.py`

- [ ] **Step 1: Create settings directory and __init__.py**

```bash
mkdir -p zsagenda/zsagenda/settings
touch zsagenda/zsagenda/settings/__init__.py
```

- [ ] **Step 2: Create base.py**

Write `zsagenda/zsagenda/settings/base.py`:

```python
"""
Shared Django settings for zsagenda project.
Environment-specific settings go in dev.py or production.py.
Secrets are read from environment variables.
"""

import os
from datetime import date

from django.contrib.messages import constants as messages


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))

SECRET_KEY = os.environ["SECRET_KEY"]

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "regform",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "zsagenda.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zsagenda.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(DATA_DIR, "database", "db.sqlite3"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "cs"
TIME_ZONE = "Europe/Prague"
USE_I18N = True

STATIC_URL = "/static/"
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "project_static_files"),
)
STATIC_ROOT = os.path.join(DATA_DIR, "static")
MEDIA_ROOT = os.path.join(DATA_DIR, "media")

MESSAGE_TAGS = {
    messages.ERROR: "danger",
}

FORCE_REPORT_OPEN = False

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

REG_IDENTIFIER_PREFIX = date.today().strftime("%y")
```

- [ ] **Step 3: Create dev.py**

Write `zsagenda/zsagenda/settings/dev.py`:

```python
from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REG_FORM_EMAIL_SENDER = "ZS Test <noreply@localhost>"
REG_FORM_EMAIL_REPLYTO = "ZS Test <info@localhost>"
REG_FORM_EMAIL_CC = []
CONTACT_URL = "http://localhost:8000/"

FORCE_REPORT_OPEN = True
```

- [ ] **Step 4: Create production.py**

Write `zsagenda/zsagenda/settings/production.py`:

```python
from .base import *  # noqa: F401,F403

DEBUG = False
ALLOWED_HOSTS = ["zapis.skolanapohodu.cz"]

EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_USE_TLS = False

REG_FORM_EMAIL_SENDER = "ZS Na Pohodu <noreply@zapis.skolanapohodu.cz>"
REG_FORM_EMAIL_REPLYTO = "ZS Na Pohodu <info@skolanapohodu.cz>"
REG_FORM_EMAIL_CC = ["info@skolanapohodu.cz"]
CONTACT_URL = "https://www.skolanapohodu.cz/kontakty/"
```

- [ ] **Step 5: Delete old settings.py**

```bash
rm zsagenda/zsagenda/settings.py
```

- [ ] **Step 6: Update manage.py default settings module**

In `zsagenda/manage.py`, change:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zsagenda.settings')
```

to:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zsagenda.settings.dev')
```

- [ ] **Step 7: Update wsgi.py default settings module**

In `zsagenda/zsagenda/wsgi.py`, change:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zsagenda.settings')
```

to:

```python
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zsagenda.settings.production')
```

- [ ] **Step 8: Verify settings work**

```bash
cd zsagenda && SECRET_KEY=test-key DJANGO_SETTINGS_MODULE=zsagenda.settings.dev uv run python manage.py check
```

Expected: `System check identified no issues.`

- [ ] **Step 9: Run existing tests**

```bash
cd zsagenda && SECRET_KEY=test-key DJANGO_SETTINGS_MODULE=zsagenda.settings.dev uv run python manage.py test regform
```

Expected: 2 tests pass (from `regform/tests/test_forms.py`).

- [ ] **Step 10: Commit**

```bash
git rm zsagenda/zsagenda/settings.py
git add zsagenda/zsagenda/settings/ zsagenda/manage.py zsagenda/zsagenda/wsgi.py
git commit -m "Refactor settings into base/dev/production profiles

Split monolithic settings.py into settings/ package.
Secrets via env vars. Environment-specific config in dev.py and production.py.
Remove local_settings.py import."
```

---

### Task 4: Docker Setup

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`
- Create: `.env.example`

- [ ] **Step 1: Create Dockerfile**

Write `Dockerfile` at repo root:

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

- [ ] **Step 2: Create docker-compose.yml**

Write `docker-compose.yml` at repo root:

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

- [ ] **Step 3: Create .env.example**

Write `.env.example` at repo root:

```
DJANGO_SETTINGS_MODULE=zsagenda.settings.production
SECRET_KEY=change-me
PORT=8000
```

- [ ] **Step 4: Create .env for local testing**

```bash
cp .env.example .env
sed -i '' 's/change-me/local-dev-secret-key-not-for-production/' .env
```

- [ ] **Step 5: Create data directories for volume mounts**

```bash
mkdir -p data/database data/static data/media data/logs
```

- [ ] **Step 6: Build Docker image**

```bash
docker compose build
```

Expected: image builds successfully, collectstatic runs without errors.

- [ ] **Step 7: Run container and verify**

```bash
docker compose up -d
sleep 2
curl -s http://localhost:8000/is-reg-open/ | head -20
docker compose down
```

Expected: JSON response `{"is_open": false}` (no registration dates exist).

- [ ] **Step 8: Commit**

```bash
git add Dockerfile docker-compose.yml .env.example
git commit -m "Add Docker and docker-compose configuration

Gunicorn WSGI server, uv-based dependency install.
Volume mounts for database, static files, media, and logs.
Port configurable via PORT env var."
```

---

### Task 5: Cleanup and Final Touches

**Files:**
- Modify: `.gitignore`
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update .gitignore**

Add these entries to `.gitignore` (if not already present):

```
# Docker / runtime
.env
data/

# uv
.venv/
```

Remove these entries if present:

```
.mypy_cache/
```

- [ ] **Step 2: Update CLAUDE.md**

Replace the contents of `CLAUDE.md` to reflect the new project structure and commands — pyproject.toml + uv, settings profiles, Docker commands, new file layout.

- [ ] **Step 3: Verify everything works end-to-end**

```bash
# Tests with dev settings
cd zsagenda && SECRET_KEY=test-key DJANGO_SETTINGS_MODULE=zsagenda.settings.dev uv run python manage.py test regform
```

Expected: all tests pass.

```bash
# Docker build and run
cd .. && docker compose build && docker compose up -d
sleep 2
curl -s http://localhost:8000/is-reg-open/
docker compose down
```

Expected: JSON response from running container.

- [ ] **Step 4: Commit**

```bash
git add .gitignore CLAUDE.md
git commit -m "Update .gitignore and CLAUDE.md for modernized setup"
```

---

### Task 6: Final Verification

- [ ] **Step 1: Run full Docker lifecycle test**

```bash
docker compose build
docker compose up -d
sleep 2
# Check app responds
curl -s http://localhost:8000/is-reg-open/
# Check static files were collected
docker compose exec web ls /app/data/static/css/
# Check logs directory is writable
docker compose exec web ls /app/data/logs/
# Run migrations inside container
docker compose exec web uv run python zsagenda/manage.py migrate
# Check admin loads
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/login/
docker compose down
```

Expected: JSON response, static files listed, 200 from admin login page.

- [ ] **Step 2: Verify no leftover files**

```bash
# Should not exist
ls requirements/ 2>&1
ls zsagenda/zsagenda/settings.py 2>&1
```

Expected: both return "No such file or directory".

- [ ] **Step 3: Review git status is clean**

```bash
git status
```

Expected: clean working tree on `modernize` branch.
