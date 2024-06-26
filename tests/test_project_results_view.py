# pylint: disable=redefined-outer-name,unused-argument
import pytest
from django.utils.dateparse import parse_datetime
from rest_framework.test import APIClient

from curation_portal.constants import VERDICTS
from curation_portal.models import (
    CurationAssignment,
    CurationResult,
    Project,
    User,
    CustomFlag,
    CustomFlagCurationResult,
    Variant,
)

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


@pytest.fixture(scope="module")
def db_setup(django_db_setup, django_db_blocker, create_variant):
    with django_db_blocker.unblock():
        project = Project.objects.create(id=1, name="Test Project")
        variant1 = create_variant(project, "1-100-A-G")
        create_variant(project, "1-200-G-A")
        create_variant(project, "1-300-T-C")

        user1 = User.objects.create(username="user1@example.com")
        user2 = User.objects.create(username="user2@example.com")
        user3 = User.objects.create(username="user3@example.com")

        project.owners.set([user1])
        CurationAssignment.objects.create(curator=user2, variant=variant1)

        yield

        project.delete()

        user1.delete()
        user2.delete()
        user3.delete()


def test_results_requires_authentication(db_setup):
    client = APIClient()
    response = client.get("/api/project/1/results/", format="json")
    assert response.status_code == 403


@pytest.mark.parametrize(
    "username,expected_status_code",
    [("user1@example.com", 200), ("user2@example.com", 403), ("user3@example.com", 404)],
)
def test_results_can_only_be_viewed_by_project_owners(db_setup, username, expected_status_code):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))
    response = client.get("/api/project/1/results/", format="json")
    assert response.status_code == expected_status_code


def test_upload_results_requires_authentication(db_setup):
    client = APIClient()
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-100-A-G", "curator": "user3@example.com", "verdict": "uncertain"}],
        format="json",
    )
    assert response.status_code == 403


@pytest.mark.parametrize(
    "username,expected_status_code",
    [("user1@example.com", 200), ("user2@example.com", 403), ("user3@example.com", 404)],
)
def test_results_can_only_be_uploaded_by_project_owners(db_setup, username, expected_status_code):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-100-A-G", "curator": "user3@example.com"}],
        format="json",
    )
    assert response.status_code == expected_status_code


def test_upload_results_creates_assignments_and_results(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-100-A-G", "curator": "user3@example.com", "verdict": "lof"}],
        format="json",
    )
    assert response.status_code == 200

    query = {"assignment__variant__variant_id": "1-100-A-G", "assignment__variant__project": 1}
    assert CurationResult.objects.filter(**query).exists()
    result = CurationResult.objects.get(**query)
    assert result.verdict == "lof"


def test_upload_results_validates_variant_ids(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "foo", "curator": "user2@example.com"}],
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.parametrize("verdict", ["some_invalid_verdict", ""])
def test_upload_results_validates_verdicts(db_setup, verdict):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-200-G-A", "curator": "user2@example.com", "verdict": verdict}],
        format="json",
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    "flags,verdict,status_code",
    [
        ({}, "lof", 200),
        # Test flow_chart_overridden flag
        *[({"flag_flow_chart_overridden": True}, v, 200) for v in VERDICTS],
        # Test no_read_data flag
        *[({"flag_no_read_data": True}, v, 200 if v in ["uncertain"] else 400) for v in VERDICTS],
        # Test reference_error flag
        *[({"flag_reference_error": True}, v, 200 if v in ["not_lof"] else 400) for v in VERDICTS],
        # Test flags for uncertain, likely_not_lof, and not_lof verdicts
        *[
            (
                {"flag_mapping_error": True},
                v,
                200 if v in ["uncertain", "likely_not_lof", "not_lof"] else 400,
            )
            for v in VERDICTS
        ],
        *[
            (
                {"flag_genotyping_error": True},
                v,
                200 if v in ["uncertain", "likely_not_lof", "not_lof"] else 400,
            )
            for v in VERDICTS
        ],
        *[
            (
                {"flag_inconsequential_transcript": True},
                v,
                200 if v in ["uncertain", "likely_not_lof", "not_lof"] else 400,
            )
            for v in VERDICTS
        ],
        *[
            (
                {"flag_rescue": True},
                v,
                200 if v in ["uncertain", "likely_not_lof", "not_lof"] else 400,
            )
            for v in VERDICTS
        ],
        # Test any other flag
        *[
            (
                {"flag_strand_bias": True},
                v,
                200 if v in ["lof", "likely_lof", "uncertain"] else 400,
            )
            for v in VERDICTS
        ],
    ],
)
def test_upload_results_validates_verdict_flag_rules(db_setup, flags, verdict, status_code):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-200-G-A", "curator": "user2@example.com", "verdict": verdict, **flags}],
        format="json",
    )
    assert response.status_code == status_code
    if status_code == 400:
        assert (
            "Verdict is not compatible with the current selection of flags"
            in response.json()[0]["verdict"][0]
        )


def test_upload_results_creates_no_results_on_validation_errors(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    starting_result_count = CurationResult.objects.filter(assignment__variant__project=1).count()

    response = client.post(
        "/api/project/1/results/",
        [
            # Validation error caused by an invalid variant ID
            {"curator": "user3@example.com", "variant_id": "foo"},
            {"curator": "user3@example.com", "variant_id": "1-300-T-C"},
        ],
        format="json",
    )

    assert response.status_code == 400
    result_count = CurationResult.objects.filter(assignment__variant__project=1).count()
    assert result_count == starting_result_count


def test_upload_results_rejects_results_for_variants_that_do_not_exist(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [{"curator": "user3@example.com", "variant_id": "1-400-A-C"}],
        format="json",
    )

    assert response.status_code == 400
    assert not CurationResult.objects.filter(assignment__variant__variant_id="1-400-A-C").exists()


def test_upload_results_updates_results_for_assignments_that_already_exist(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"curator": "user2@example.com", "variant_id": "1-100-A-G"}],
        format="json",
    )

    assert response.status_code == 200
    assert (
        CurationAssignment.objects.filter(
            variant__project=1,
            variant__variant_id="1-100-A-G",
            curator__username="user2@example.com",
        ).count()
        == 1
    )


def test_upload_results_rejects_duplicate_assignments(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [
            {"curator": "user2@example.com", "variant_id": "1-200-G-A"},
            {"curator": "user2@example.com", "variant_id": "1-200-G-A"},
            {"curator": "user3@example.com", "variant_id": "1-300-T-C"},
            {"curator": "user3@example.com", "variant_id": "1-300-T-C"},
        ],
        format="json",
    )

    assert response.status_code == 400
    response = response.json()
    assert "non_field_errors" in response
    assert (
        "Duplicate results for user2@example.com (variants 1-200-G-A), user3@example.com (variants 1-300-T-C)"
        in response["non_field_errors"]
    )

    assert not CurationResult.objects.filter(
        assignment__variant__project=1,
        assignment__variant__variant_id="1-200-G-A",
        assignment__curator__username="user2@example.com",
    ).exists()
    assert not CurationResult.objects.filter(
        assignment__variant__project=1,
        assignment__variant__variant_id="1-300-T-C",
        assignment__curator__username="user3@example.com",
    ).exists()


def test_upload_results_sets_custom_flags(db_setup):
    custom_flag = CustomFlag.objects.create(
        key="flag_foo_bar",
        label="Flag Foo Bar",
        shortcut="FB",
    )

    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user1@example.com",
                "variant_id": "1-100-A-G",
                "custom_flags": {"flag_foo_bar": True},
            }
        ],
        format="json",
    )

    assert response.status_code == 200
    assert CurationResult.objects.filter(assignment__variant__variant_id="1-100-A-G").exists()

    result = CurationResult.objects.get(assignment__variant__variant_id="1-100-A-G")
    assert CustomFlagCurationResult.objects.filter(result=result, flag=custom_flag).exists()

    custom_result = CustomFlagCurationResult.objects.get(result=result, flag=custom_flag)
    assert custom_result.checked


def test_upload_results_rejects_results_with_custom_flags_that_do_not_exist(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user1@example.com",
                "variant_id": "1-100-A-G",
                "custom_flags": {"flag_foo_bar": True},
            }
        ],
        format="json",
    )

    assert response.status_code == 400
    assert "'flag_foo_bar' does not exist" in str(response.data[0])
    assert not CurationResult.objects.filter(assignment__variant__variant_id="1-100-A-G").exists()


def test_upload_results_sets_all_custom_flags_as_false_if_not_specified(db_setup):
    custom_flag = CustomFlag.objects.create(
        key="flag_foo_bar",
        label="Flag Foo Bar",
        shortcut="FB",
    )

    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [{"curator": "user1@example.com", "variant_id": "1-100-A-G"}],
        format="json",
    )

    assert response.status_code == 200
    assert CurationResult.objects.filter(assignment__variant__variant_id="1-100-A-G").exists()

    result = CurationResult.objects.get(assignment__variant__variant_id="1-100-A-G")
    assert CustomFlagCurationResult.objects.filter(result=result, flag=custom_flag).exists()

    custom_result = CustomFlagCurationResult.objects.get(result=result, flag=custom_flag)
    assert not custom_result.checked


def test_upload_sets_notes_and_curator_comments_fields(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user1@example.com",
                "variant_id": "1-100-A-G",
                "notes": "foo",
                "curator_comments": "bar",
            }
        ],
        format="json",
    )

    assert response.status_code == 200
    assert CurationResult.objects.filter(assignment__variant__variant_id="1-100-A-G").exists()

    result = CurationResult.objects.get(assignment__variant__variant_id="1-100-A-G")
    assert result.notes == "foo"
    assert result.curator_comments == "bar"


def test_upload_results_updates_fields_updated_at_timestamp_and_sets_requester_as_editor(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    # Create new assignment curation result
    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__variant_id="1-100-A-G"
    )
    assignment.result = CurationResult.objects.create()
    assignment.save()
    timestamp_before = assignment.result.updated_at

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user2@example.com",
                "variant_id": "1-100-A-G",
                "notes": "Hello, world!",
            }
        ],
        format="json",
    )

    assert response.status_code == 200, response.json()

    assignment.result.refresh_from_db()
    timestamp_after = assignment.result.updated_at
    assert assignment.result.editor.username == "user1@example.com"
    assert timestamp_before < timestamp_after


def test_upload_results_does_not_set_editor_if_requester_is_the_curator_for_an_assignment(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    # Create new assignment curation result
    assignment = CurationAssignment.objects.create(
        curator=User.objects.get(username="user1@example.com"),
        variant=Variant.objects.get(variant_id="1-100-A-G"),
    )
    assignment.result = CurationResult.objects.create()
    assignment.save()

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user1@example.com",
                "variant_id": "1-100-A-G",
                "notes": "Hello, world!",
            }
        ],
        format="json",
    )

    assert response.status_code == 200, response.json()

    assignment.result.refresh_from_db()
    assert assignment.result.editor is None


def test_upload_results_does_not_update_result_if_fields_have_not_changed(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    # Create new assignment curation result
    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__variant_id="1-100-A-G"
    )
    assignment.result = CurationResult.objects.create(notes="Hello, world!")
    assignment.save()
    timestamp_before = assignment.result.updated_at

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user2@example.com",
                "variant_id": "1-100-A-G",
                "notes": "Hello, world!",
            }
        ],
        format="json",
    )

    assert response.status_code == 200, response.json()

    assignment.result.refresh_from_db()
    timestamp_after = assignment.result.updated_at
    # No editor should be set, and the timestamp should not have changed
    assert assignment.result.editor is None
    assert timestamp_before == timestamp_after


def test_upload_results_ignores_timestamps_when_updating_existing_result(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    # Create new assignment curation result
    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__variant_id="1-100-A-G"
    )
    assignment.result = CurationResult.objects.create()
    assignment.save()

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user2@example.com",
                "variant_id": "1-100-A-G",
                "notes": "Hello, world!",
                "created_at": "2023-09-08T00:00:28.145556",
                "updated_at": "2023-09-18T07:24:24.534399",
            }
        ],
        format="json",
    )

    assert response.status_code == 200, response.json()

    assignment.result.refresh_from_db()
    assert parse_datetime(str(assignment.result.created_at)) != parse_datetime(
        "2023-09-08T00:00:28.145556"
    )
    assert parse_datetime(str(assignment.result.updated_at)) != parse_datetime(
        "2023-09-18T07:24:24.534399"
    )
