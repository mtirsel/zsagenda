from .base import *  # noqa: F401,F403

DEBUG = True
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

REG_FORM_EMAIL_SENDER = "ZS Test <noreply@localhost>"
REG_FORM_EMAIL_REPLYTO = "ZS Test <info@localhost>"
REG_FORM_EMAIL_CC = []
CONTACT_URL = "http://localhost:8000/"

FORCE_REPORT_OPEN = True
