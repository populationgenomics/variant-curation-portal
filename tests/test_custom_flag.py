# pylint: disable=redefined-outer-name,unused-argument
import pytest

from django.core.exceptions import ValidationError

from curation_portal.models import CurationResult, CustomFlag, CustomFlagCurationResult

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_creating_custom_flag_adds_flag_to_existing_curation_results(
    django_db_setup,
    django_db_blocker,
):
    with django_db_blocker.unblock():
        result = CurationResult.objects.create()

        assert result.custom_flags.count() == 0
        assert CustomFlagCurationResult.objects.count() == 0

        flag = CustomFlag.objects.create(key="flag_new", label="New Flag", shortcut="NF")
        assert result.custom_flags.count() == 1
        assert CustomFlagCurationResult.objects.count() == 1

        result.delete()
        flag.delete()


def test_deleting_flag_deletes_related_custom_flag_curation_result(
    django_db_setup,
    django_db_blocker,
):
    with django_db_blocker.unblock():
        result = CurationResult.objects.create()

        assert result.custom_flags.count() == 0
        assert CustomFlagCurationResult.objects.count() == 0

        flag = CustomFlag.objects.create(key="flag_new", label="New Flag", shortcut="NF")
        assert result.custom_flags.count() == 1
        assert CustomFlagCurationResult.objects.count() == 1

        flag.delete()

        assert CustomFlagCurationResult.objects.count() == 0


def test_validation_error_flag_key_does_not_start_with_the_word_flag(
    django_db_setup, django_db_blocker
):
    with django_db_blocker.unblock():
        flag = CustomFlag(key="foo_bar", label="New Flag", shortcut="FN")
        with pytest.raises(ValidationError):
            flag.full_clean()

        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="FN")
        flag.full_clean()


def test_validation_error_flag_key_is_not_in_snake_case(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        flag = CustomFlag(key="flag_foo-bar", label="New Flag", shortcut="FN")
        with pytest.raises(ValidationError):
            flag.full_clean()

        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="FN")
        flag.full_clean()


def test_validation_error_flag_key_is_not_lower_case(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        flag = CustomFlag(key="flag_FOO_BAR", label="New Flag", shortcut="FN")
        with pytest.raises(ValidationError):
            flag.full_clean()

        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="FN")
        flag.full_clean()


def test_validation_error_flag_shortcut_is_not_upper_case(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="fn")
        with pytest.raises(ValidationError, match="must be 2 uppercase alphanumeric"):
            flag.full_clean()

        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="FN")
        flag.full_clean()


def test_validation_error_flag_shortcut_starts_with_a_number(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="5N")
        with pytest.raises(ValidationError, match="must be 2 uppercase alphanumeric"):
            flag.full_clean()

        flag = CustomFlag(key="flag_foo_bar", label="New Flag", shortcut="FN")
        flag.full_clean()
