import json
from pathlib import Path

from django.contrib.auth.models import Permission
from django.core.management import BaseCommand
from django.db import transaction

from curation_portal.models import CurationAssignment, Project, User
from curation_portal.serializers import VariantSerializer


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--variants",
            type=Path,
            required=True,
            help="Path to JSON file containing variants.",
        )
        parser.add_argument(
            "--username",
            type=str,
            default="someuser",
            help="Username of user to create assignments for",
        )
        parser.add_argument(
            "--project",
            type=str,
            default="test-project",
            help="Name of project to add variants to",
        )

    def handle(self, *args, **options):
        file = options["variants"]
        if not file.exists():
            raise FileNotFoundError(f"File {file} does not exist.")

        with transaction.atomic():
            user, _ = User.objects.get_or_create(username=options["username"])
            project, _ = Project.objects.get_or_create(name=options["project"])

            project.owners.add(user)
            user.user_permissions.add(Permission.objects.get(codename="add_project"))
            user.user_permissions.add(Permission.objects.get(codename="add_variant"))

            with file.open("r") as f:
                data = json.load(f)

                serializer = VariantSerializer(data=data, context={"project": project}, many=True)
                serializer.is_valid(raise_exception=True)
                variants = serializer.save()

                for variant in variants:
                    CurationAssignment.objects.update_or_create(curator=user, variant=variant)
