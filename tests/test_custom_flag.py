# pylint: disable=redefined-outer-name,unused-argument
import pytest

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

        flag = CustomFlag.objects.create(key="new_flag", label="New Flag", shortcut="NF")
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

        flag = CustomFlag.objects.create(key="new_flag", label="New Flag", shortcut="NF")
        assert result.custom_flags.count() == 1
        assert CustomFlagCurationResult.objects.count() == 1

        flag.delete()

        assert CustomFlagCurationResult.objects.count() == 0
