# pylint: disable=redefined-outer-name,unused-argument
import pytest
from rest_framework.test import APIClient

from curation_portal.models import User, UserSettings

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


@pytest.fixture(scope="module")
def db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        user = User.objects.create(username="user@example.com")
        UserSettings.objects.create(
            user=user,
            ucsc_username="user",
            ucsc_session_name_grch37="test_session_grch37",
            ucsc_session_name_grch38="test_session_grch38",
        )

        yield

        user.delete()


def test_profile_view_requires_authentication(db_setup):
    client = APIClient()
    response = client.get("/api/profile/")
    assert response.status_code == 403


@pytest.mark.parametrize("username", ["user@example.com"])
def test_profile_view_returns_username(db_setup, username):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))
    response = client.get("/api/profile/").json()
    assert response["user"]["username"] == username


@pytest.mark.parametrize("username", ["user@example.com"])
def test_profile_view_return_settings(db_setup, username):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))
    response = client.get("/api/profile/").json()
    assert response["user"]["settings"] == {
        "ucsc_username": "user",
        "ucsc_session_name_grch37": "test_session_grch37",
        "ucsc_session_name_grch38": "test_session_grch38",
    }
