# pylint: disable=redefined-outer-name,unused-argument
import pytest

from curation_portal.models import CurationResult, CustomFlag, CustomFlagCurationResult

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


def test_creating_a_new_instance_adds_all_custom_flags(
    django_db_setup,
    django_db_blocker,
):
    with django_db_blocker.unblock():
        CustomFlag.objects.create(key="new_flag", label="New Flag", shortcut="NF")

        assert CustomFlagCurationResult.objects.count() == 0
        result = CurationResult.objects.create()

        assert result.custom_flags.count() == 1


def test_deleting_curation_result_deletes_related_custom_curation_result(
    django_db_setup,
    django_db_blocker,
):
    with django_db_blocker.unblock():
        result = CurationResult.objects.create()

        assert result.custom_flags.count() == 0
        assert CustomFlagCurationResult.objects.count() == 0

        CustomFlag.objects.create(key="new_flag", label="New Flag", shortcut="NF")
        assert result.custom_flags.count() == 1
        assert CustomFlagCurationResult.objects.count() == 1

        result.delete()

        assert CustomFlag.objects.count() == 1
        assert CustomFlagCurationResult.objects.count() == 0
