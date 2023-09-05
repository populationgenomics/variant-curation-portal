"""Django settings for tests."""

from .base import *  # pylint: disable=wildcard-import,unused-wildcard-import


SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

ALLOWED_DIRECTORIES = os.getenv("ALLOWED_DIRECTORIES", STATIC_URL).split(",")
