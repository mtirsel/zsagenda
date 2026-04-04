# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZSAgenda is a Django web application for scheduling school registration time slots for a Czech primary school ("Škola Na Pohodu"). Parents select available time slots to register their children for school enrollment.

## Key Commands

Development (from `zsagenda/` inner directory containing `manage.py`):

```bash
SECRET_KEY=dev-key uv run python manage.py runserver       # Dev server (uses settings.dev by default)
SECRET_KEY=dev-key uv run python manage.py test regform    # Run all tests
SECRET_KEY=dev-key uv run python manage.py test regform.tests.test_forms.TestRegistrationAnswerForm  # Single test class
SECRET_KEY=dev-key uv run python manage.py migrate         # Apply migrations
SECRET_KEY=dev-key uv run python manage.py makemigrations  # Create new migrations
```

Linting (from repo root):
```bash
uv run ruff check .
uv run pylint zsagenda/regform/
```

Docker:
```bash
docker compose build                    # Build image
docker compose up -d                    # Start container
docker compose exec web uv run python zsagenda/manage.py migrate  # Run migrations
docker compose down                     # Stop container
```

## Architecture

Single Django app (`regform`) with function-based views. SQLite database. Containerized with Docker + Gunicorn.

**Models** (`regform/models.py`):
- `RegistrationDate` — available time slots. `is_available()` checks if slot is taken.
- `RegistrationAnswer` — form submissions (one-to-one with RegistrationDate). Has auto-generated `identifier` (e.g. "2601"). `substitute=True` marks waitlist entries.
- `SubstituteContact` — waitlist contact info (currently unused, commented out in admin).

**Views** (`regform/views.py`):
- `display_form` (GET/POST `/`) — main registration form. Checks slot availability, handles duplicate prevention (90-day window by child name + birth date), sends confirmation email.
- `registration_closed` (GET/POST `/registrace-ukoncena/`) — closed page with substitute/waitlist form.
- `registration_done` (GET `/registrace-dokoncena/`) — success confirmation.
- `is_registration_open` (GET `/is-reg-open/`) — JSON API for external sites to check status. Supports CORS.

**Forms** (`regform/forms.py`):
- `RegistrationAnswerForm` — main form. Dynamically populates `reg_date` with future available slots. Server-side race condition protection in `clean_reg_date()`.
- `SubstituteContactForm` — subset of fields, marks `substitute=True`.

**Email** (`regform/utils.py`): Two email functions using templates in `templates/mail/`. Configuration via settings profiles.

## Settings

Split into `zsagenda/zsagenda/settings/`:
- `base.py` — shared settings. Secrets from env vars (`SECRET_KEY`). `DATA_DIR` env var controls paths for database, static, media.
- `dev.py` — `DEBUG=True`, console email backend, `FORCE_REPORT_OPEN=True`
- `production.py` — production ALLOWED_HOSTS, SMTP email, real sender/replyto/cc

Selection: `DJANGO_SETTINGS_MODULE` env var. `manage.py` defaults to `dev`, `wsgi.py` defaults to `production`.

## Docker

- `Dockerfile` — Python 3.13-slim, uv for deps, Gunicorn WSGI server
- `docker-compose.yml` — single `web` service, env from `.env`, volume mounts at `/app/data/` for database, static, media, logs
- `.env.example` — `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `PORT`

## Dependencies

Managed via `pyproject.toml` + `uv`. Django 5.2 LTS, Gunicorn. Dev: model-bakery, pudb, pylint, ruff.

## Branches

- `master` — main development branch (PR target)
- `production` — production deployments
