from django.conf import settings
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.contrib.auth.backends import RemoteUserBackend


class AuthMiddleware(RemoteUserMiddleware):
    header = settings.CURATION_PORTAL_AUTH_HEADER


class AuthBackend(RemoteUserBackend):
    def clean_username(self, username):
        # See https://cloud.google.com/iap/docs/identity-howto
        IAP_PREFIX = "accounts.google.com:"  # pylint: disable=invalid-name
        if username.startswith(IAP_PREFIX):
            username = username[len(IAP_PREFIX) :]
        return username
