# pylint: disable=redefined-outer-name,unused-argument
import pytest
from rest_framework.test import APIClient

from curation_portal.constants import VERDICTS
from curation_portal.models import (
    CurationAssignment,
    CurationResult,
    Project,
    User,
    Variant,
    CustomFlag,
)

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


@pytest.fixture(scope="module")
def db_setup(django_db_setup, django_db_blocker, create_variant):
    with django_db_blocker.unblock():
        project = Project.objects.create(id=1, name="Test Project")
        variant1 = create_variant(
            project,
            "1-100-A-G",
            annotations=[
                {
                    "consequence": "frameshift_variant",
                    "gene_id": "g2",
                    "gene_symbol": "GENETWO",
                    "transcript_id": "t2",
                }
            ],
        )
        variant2 = create_variant(
            project,
            "1-100-A-C",
            annotations=[
                {
                    "consequence": "frameshift_variant",
                    "gene_id": "g3",
                    "gene_symbol": "GENETHREE",
                    "transcript_id": "t3",
                }
            ],
        )
        variant3 = create_variant(
            project,
            "1-100-A-AT",
            annotations=[
                {
                    "consequence": "frameshift_variant",
                    "gene_id": "g2",
                    "gene_symbol": "GENETWO",
                    "transcript_id": "t2",
                }
            ],
        )
        variant4 = create_variant(
            project,
            "1-100-A-AC",
            annotations=[
                {
                    "consequence": "frameshift_variant",
                    "gene_id": "g1",
                    "gene_symbol": "GENEONE",
                    "transcript_id": "t1",
                }
            ],
        )

        user1 = User.objects.create(username="user1@example.com")
        user2 = User.objects.create(username="user2@example.com")
        user3 = User.objects.create(username="user3@example.com")
        user4 = User.objects.create(username="user4@example.com")

        project.owners.set([user1])
        CurationAssignment.objects.create(curator=user2, variant=variant1)
        CurationAssignment.objects.create(curator=user2, variant=variant2)
        CurationAssignment.objects.create(curator=user2, variant=variant3)
        CurationAssignment.objects.create(curator=user2, variant=variant4)
        CurationAssignment.objects.create(curator=user3, variant=variant2)

        yield

        project.delete()

        user1.delete()
        user2.delete()
        user3.delete()
        user4.delete()


def test_curate_variant_view_requires_authentication(db_setup):
    client = APIClient()

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.get(f"/api/project/1/variant/{variant1.id}/curate/")
    assert response.status_code == 403

    response = client.post(f"/api/project/1/variant/{variant1.id}/curate/", {}, format="json")
    assert response.status_code == 403


@pytest.mark.parametrize(
    "username,expected_status_code",
    [
        ("user1@example.com", 404),
        ("user2@example.com", 200),
        ("user3@example.com", 404),
        ("user4@example.com", 404),
    ],
)
def test_curate_variant_view_can_only_be_viewed_by_variant_curators(
    db_setup, username, expected_status_code
):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.get(f"/api/project/1/variant/{variant1.id}/curate/")
    assert response.status_code == expected_status_code

    response = client.post(f"/api/project/1/variant/{variant1.id}/curate/", {}, format="json")
    assert response.status_code == expected_status_code


@pytest.mark.parametrize(
    "username,expected_status_code",
    [
        ("user1@example.com", 200),
        ("user2@example.com", 200),
        ("user3@example.com", 404),
        ("user4@example.com", 404),
    ],
)
def test_curate_variant_view_can_only_be_viewed_by_project_owners_when_specifying_result_curators_id(
    db_setup, username, expected_status_code
):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    curator = User.objects.get(username="user2@example.com")
    response = client.get(f"/api/project/1/variant/{variant1.id}/curate/?curator={curator.id}")
    assert response.status_code == expected_status_code

    response = client.post(
        path=f"/api/project/1/variant/{variant1.id}/curate/",
        data={"curator": curator.id},
        format="json",
    )
    assert response.status_code == expected_status_code


def test_curate_variant_view_cannot_be_viewed_by_project_owners_when_not_specifying_result_curators_id(
    db_setup,
):
    client = APIClient()
    owner = User.objects.get(username="user1@example.com")
    client.force_authenticate(owner)

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.get(f"/api/project/1/variant/{variant1.id}/curate/")
    assert response.status_code == 404

    response = client.post(
        path=f"/api/project/1/variant/{variant1.id}/curate/",
        data={},
        format="json",
    )
    assert response.status_code == 404


def test_curate_variant_stores_result(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    assert not CurationResult.objects.filter(
        assignment__curator__username="user2@example.com",
        assignment__variant__project=1,
        assignment__variant__variant_id="1-100-A-G",
    ).exists()

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/",
        {
            "verdict": "lof",
            "notes": "LoF for sure",
            "curator_comments": "This is a Loss of Function variant",
        },
        format="json",
    )

    assert response.status_code == 200

    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__project=1, variant__variant_id="1-100-A-G"
    )

    assert assignment.result
    assert assignment.result.verdict == "lof"
    assert assignment.result.notes == "LoF for sure"
    assert assignment.result.curator_comments == "This is a Loss of Function variant"


def test_curate_variant_view_sets_editor_if_request_is_from_a_project_owner(db_setup):
    client = APIClient()
    owner = User.objects.get(username="user1@example.com")
    curator = User.objects.get(username="user2@example.com")

    client.force_authenticate(owner)

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.post(
        path=f"/api/project/1/variant/{variant1.id}/curate/",
        data={"curator": curator.id},
        format="json",
    )
    assert response.status_code == 200

    result = CurationResult.objects.filter(
        assignment__curator__username="user2@example.com",
        assignment__variant__project=1,
        assignment__variant__variant_id="1-100-A-G",
    )
    assert result.exists()
    assert result.first().editor == owner


def test_curate_variant_view_unsets_editor_if_request_is_from_assigned_curator(db_setup):
    client = APIClient()
    owner = User.objects.get(username="user1@example.com")
    curator = User.objects.get(username="user2@example.com")

    client.force_authenticate(curator)

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)
    assignment = CurationAssignment.objects.get(curator=curator, variant=variant1)
    result, _ = CurationResult.objects.get_or_create(editor=owner)
    assignment.result = result
    assignment.save()

    response = client.post(
        path=f"/api/project/1/variant/{variant1.id}/curate/",
        data={},
        format="json",
    )
    assert response.status_code == 200

    result.refresh_from_db()
    assignment.refresh_from_db()

    assert assignment.result == result
    assert result.editor is None


def test_curate_variant_stores_custom_flags(db_setup):
    flag = CustomFlag.objects.create(key="flag_foo_bar", label="Flag Foo Bar", shortcut="FB")

    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    assert not CurationResult.objects.filter(
        assignment__curator__username="user2@example.com",
        assignment__variant__project=1,
        assignment__variant__variant_id="1-100-A-G",
    ).exists()

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/",
        {"custom_flags": {"flag_foo_bar": True}},
        format="json",
    )

    assert response.status_code == 200

    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__project=1, variant__variant_id="1-100-A-G"
    )

    assert assignment.result
    assert assignment.result.custom_flags.first().flag.key == flag.key
    assert assignment.result.custom_flags.first().checked


def test_curate_variant_stores_custom_flag_defaults(db_setup):
    flag = CustomFlag.objects.create(key="flag_foo_bar", label="Flag Foo Bar", shortcut="FB")

    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    assert not CurationResult.objects.filter(
        assignment__curator__username="user2@example.com",
        assignment__variant__project=1,
        assignment__variant__variant_id="1-100-A-G",
    ).exists()

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/",
        {"custom_flags": {}},
        format="json",
    )

    assert response.status_code == 200

    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__project=1, variant__variant_id="1-100-A-G"
    )

    assert assignment.result
    assert assignment.result.custom_flags.first().flag.key == flag.key
    assert not assignment.result.custom_flags.first().checked


def test_curate_variant_fails_if_custom_flag_does_not_exist(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    assert not CurationResult.objects.filter(
        assignment__curator__username="user2@example.com",
        assignment__variant__project=1,
        assignment__variant__variant_id="1-100-A-G",
    ).exists()

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/",
        {"custom_flags": {"flag_foo_bar": True}},
        format="json",
    )

    assert response.status_code == 400
    assert "'flag_foo_bar' does not exist" in str(response.data[0])

    assignment = CurationAssignment.objects.get(
        curator__username="user2@example.com", variant__project=1, variant__variant_id="1-100-A-G"
    )

    assert not assignment.result


@pytest.mark.parametrize("verdict", ["some_invalid_verdict", ""])
def test_curate_variant_validates_verdict_choice(db_setup, verdict):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/", {"verdict": verdict}, format="json"
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
def test_curate_variant_validates_verdict_flag_rules(db_setup, flags, verdict, status_code):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant1 = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.post(
        f"/api/project/1/variant/{variant1.id}/curate/",
        {"verdict": verdict, **flags},
        format="json",
    )
    assert response.status_code == status_code


def test_curate_variant_orders_multiallelic_variants(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    assigned_variants = [
        a["variant"]["variant_id"]
        for a in client.get("/api/project/1/assignments/").json().get("assignments")
    ]
    assert assigned_variants == ["1-100-A-AC", "1-100-A-AT", "1-100-A-C", "1-100-A-G"]

    variants = [
        ("1-100-A-AC", 0, None, "1-100-A-AT"),
        ("1-100-A-AT", 1, "1-100-A-AC", "1-100-A-C"),
        ("1-100-A-C", 2, "1-100-A-AT", "1-100-A-G"),
        ("1-100-A-G", 3, "1-100-A-C", None),
    ]

    for (
        variant_id,
        expected_index,
        expected_previous_variant_id,
        expected_next_variant_id,
    ) in variants:
        variant = Variant.objects.get(variant_id=variant_id, project__id=1)
        response = client.get(f"/api/project/1/variant/{variant.id}/curate/").json()

        assert response["index"] == expected_index

        if expected_previous_variant_id:
            assert response["previous_variant"]["variant_id"] == expected_previous_variant_id
        else:
            assert response["previous_variant"] is None

        if expected_next_variant_id:
            assert response["next_variant"]["variant_id"] == expected_next_variant_id
        else:
            assert response["next_variant"] is None


def test_curate_variant_adjacent_variants_respects_filters(db_setup):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user2@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-AT", project_id=1)

    response = client.get(f"/api/project/1/variant/{variant.id}/curate/").json()
    assert response["previous_variant"]["variant_id"] == "1-100-A-AC"
    assert response["next_variant"]["variant_id"] == "1-100-A-C"
    assert response["index"] == 1

    response = client.get(
        f"/api/project/1/variant/{variant.id}/curate/",
        {"variant__annotation__gene_symbol": "GENETWO"},
    ).json()
    assert response["previous_variant"] is None
    assert response["next_variant"]["variant_id"] == "1-100-A-G"
    assert response["index"] == 0
