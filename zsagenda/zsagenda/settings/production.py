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
