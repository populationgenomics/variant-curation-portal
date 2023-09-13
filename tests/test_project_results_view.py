# pylint: disable=redefined-outer-name,unused-argument
import pytest
from rest_framework.test import APIClient

from curation_portal.models import (
    CurationAssignment,
    CurationResult,
    Project,
    User,
    CustomFlag,
    CustomFlagCurationResult,
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
        [{"variant_id": "1-100-A-G", "curator": "user3@example.com", "verdict": "uncertain"}],
        format="json",
    )
    assert response.status_code == expected_status_code


def test_upload_results_creates_assignments_and_results(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"variant_id": "1-100-A-G", "curator": "user3@example.com", "verdict": "likely_lof"}],
        format="json",
    )
    assert response.status_code == 200

    query = {"assignment__variant__variant_id": "1-100-A-G", "assignment__variant__project": 1}
    assert CurationResult.objects.filter(**query).exists()
    result = CurationResult.objects.get(**query)
    assert result.verdict == "likely_lof"


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


def test_upload_results_rejects_results_for_assignments_that_already_exist(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))
    response = client.post(
        "/api/project/1/results/",
        [{"curator": "user2@example.com", "variant_id": "1-100-A-G"}],
        format="json",
    )

    assert response.status_code == 400
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


def test_upload_results_sets_project_owner_as_editor(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": "user3@example.com",
                "variant_id": "1-100-A-G",
                "verdict": "likely_lof",
                "editor": "user1@example.com",
            }
        ],
        format="json",
    )

    assert response.status_code == 200, response.json()

    result = CurationResult.objects.get(assignment__variant__variant_id="1-100-A-G")
    assert result.editor.username == "user1@example.com"


@pytest.mark.parametrize(
    "curator,editor,error_field,error_message",
    [
        (
            "user1@example.com",
            "user1@example.com",
            "non_field_errors",
            "'curator' and 'editor' cannot be the same user",
        ),
        (
            "user3@example.com",
            "user2@example.com",
            "editor",
            "User 'user2@example.com' is not a project owner",
        ),
        (
            "user3@example.com",
            "not_a_user",
            "editor",
            "Invalid username.",
        ),
    ],
)
def test_upload_results_rejects_results_when_editor_is_improperly_configured(
    db_setup, curator, editor, error_field, error_message
):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    response = client.post(
        "/api/project/1/results/",
        [
            {
                "curator": curator,
                "variant_id": "1-100-A-G",
                "editor": editor,
            }
        ],
        format="json",
    )

    assert response.status_code == 400
    assert error_message in response.json()[0][error_field]
    assert not CurationResult.objects.filter(assignment__variant__variant_id="1-100-A-G").exists()
