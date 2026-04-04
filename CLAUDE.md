# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ZSAgenda is a Django web application for scheduling school registration time slots for a Czech primary school ("Škola Na Pohodu"). Parents select available time slots to register their children for school enrollment.

## Key Commands

All commands run from `zsagenda/` (the inner directory containing `manage.py`):

```bash
python manage.py runserver          # Dev server
python manage.py test regform       # Run all tests
python manage.py test regform.tests.test_views.TestRegistrationAnswerForm.test_form_creates_registration_answer  # Single test
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Create new migrations
```

Linting (tools installed in pyenv virtualenv `zsagenda`):
```bash
ruff check .
mypy --config-file=pyproject.toml .
pylint --rcfile=pyproject.toml .
```

## Architecture

Single Django app (`regform`) with function-based views. SQLite database.

**Models** (`regform/models.py`):
- `RegistrationDate` — available time slots. `is_available()` checks if slot is taken.
- `RegistrationAnswer` — form submissions (one-to-one with RegistrationDate). Has auto-generated `identifier` (e.g. "R01"). `substitute=True` marks waitlist entries.
- `SubstituteContact` — waitlist contact info (currently unused, commented out in admin).

**Views** (`regform/views.py`):
- `display_form` (GET/POST `/`) — main registration form. Checks slot availability, handles duplicate prevention (90-day window by child name + birth date), sends confirmation email.
- `registration_closed` (GET/POST `/registrace-ukoncena/`) — closed page with substitute/waitlist form.
- `registration_done` (GET `/registrace-dokoncena/`) — success confirmation.
- `is_registration_open` (GET `/is-reg-open/`) — JSON API for external sites to check status. Supports CORS.

**Forms** (`regform/forms.py`):
- `RegistrationAnswerForm` — main form. Dynamically populates `reg_date` with future available slots. Server-side race condition protection in `clean_reg_date()`.
- `SubstituteContactForm` — subset of fields, marks `substitute=True`.

**Email** (`regform/utils.py`): Two email functions using templates in `templates/mail/`. Configuration via `local_settings.py` (EMAIL_SENDER, EMAIL_REPLYTO, EMAIL_CC).

## Settings

- `zsagenda/zsagenda/settings.py` — main settings (DEBUG=False default, cs locale, Europe/Prague timezone, USE_TZ=False)
- `zsagenda/zsagenda/local_settings.py` — local overrides (not in git): SECRET_KEY, DEBUG, email config, `FORCE_REPORT_OPEN` for testing
- Django 2.1.x; Bootstrap 4.2.1 frontend

## Branches

- `master` — main development branch (PR target)
- `production` — production deployments
- `dj5` — Django 5.0 compatibility work
