import pytest
from django.conf import settings
from rest_framework.test import APIClient

from curation_portal.models import CurationAssignment, Project, User, Variant

pytestmark = pytest.mark.django_db  # pylint: disable=invalid-name


@pytest.fixture(scope="module", autouse=True)
def db_setup(django_db_setup, django_db_blocker, create_variant):  # pylint: disable=unused-argument
    with django_db_blocker.unblock():
        project = Project.objects.create(id=1, name="Test Project")
        variant = create_variant(project, "1-100-A-G")

        user1 = User.objects.create(username="user1@example.com")
        user2 = User.objects.create(username="user2@example.com")

        CurationAssignment.objects.create(curator=user1, variant=variant)

        yield

        project.delete()

        user1.delete()
        user2.delete()


def test_reads_file_view_requires_authentication():
    client = APIClient()

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    response = client.get(f"/api/project/1/variant/{variant.id}/reads/")
    assert response.status_code == 403


@pytest.mark.parametrize(
    "username,expected_status_code",
    [
        ("user1@example.com", 200),
        ("user2@example.com", 404),
    ],
)
def test_reads_file_view_can_only_be_viewed_by_variant_curators(
    tmp_path, username, expected_status_code
):
    client = APIClient()
    client.force_authenticate(User.objects.get(username=username))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "reads.bam"
    reads_file.touch()

    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={reads_file}")
    assert response.status_code == expected_status_code


def test_can_access_files_relative_to_allowed_directory(tmp_path):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "subfolder" / "reads.bam"
    reads_file.parent.mkdir()
    reads_file.touch()

    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={reads_file}")
    assert response.status_code == 200


def test_cannot_access_files_outside_allowed_directory(tmp_path):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = "/home/usr/reads.bam"
    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={reads_file}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Directory does not exist."}


@pytest.mark.parametrize("paths", ["..", "./..", "../..", "../../.."])
def test_reads_file_view_cannot_access_parents_of_allowed_directory(tmp_path, paths):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "reads.bam"
    reads_file.touch()

    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]

    attempted_path = tmp_path / paths / "reads.bam"
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={attempted_path}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Directory does not exist."}


@pytest.mark.parametrize("paths", ["..", "./..", "../../protected-bams", "../project-2"])
def test_reads_file_view_cannot_access_parents_of_allowed__gcsdirectory(paths):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    base_path = "gs://my-bucket/these-bams-only/project-1/"
    reads_file = base_path + "reads.bam"

    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [base_path]

    attempted_path = base_path + paths + "/reads.bam"
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={attempted_path}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Directory does not exist."}


def test_reads_file_view_can_only_access_existing_files(tmp_path):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "reads.bam"
    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]

    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={reads_file}")
    assert response.status_code == 404
    assert response.json() == {"detail": "File for variant does not exist."}


def test_reads_file_view_can_only_access_file_listed_in_variant_reads_attribute(tmp_path):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "reads.bam"
    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]

    different = tmp_path / "reads2.bam"
    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={different}")
    assert response.status_code == 404
    assert response.json() == {"detail": "File not listed in variant."}


def test_reads_file_view_file_cannot_be_a_directory(tmp_path):
    client = APIClient()
    client.force_authenticate(User.objects.get(username="user1@example.com"))

    variant = Variant.objects.get(variant_id="1-100-A-G", project__id=1)

    reads_file = tmp_path / "directory"
    reads_file.mkdir()

    variant.reads = [reads_file]
    variant.save()

    settings.ALLOWED_DIRECTORIES = [str(tmp_path)]

    response = client.get(f"/api/project/1/variant/{variant.id}/reads/?file={reads_file}")
    assert response.status_code == 400
    assert response.json() == {"detail": "'file' must be a file, not a directory."}
