import json
from pathlib import Path

from django.contrib.auth.models import Permission
from django.core.management import BaseCommand
from django.db import transaction
from django.conf import settings

from curation_portal.models import CurationAssignment, Project, User, Variant, VariantAnnotation


DATA_DIR = Path(settings.BASE_DIR) / "data"


class Command(BaseCommand):
    def add_arguments(self, parser):
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
        parser.add_argument(
            "--variants",
            type=Path,
            default=DATA_DIR / "variants.json",
            help="Path to JSON file containing variants.",
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

            for variant_props in json.load(file.open("r")):
                # Pop annotations key before creating variant
                annotations = variant_props.pop("annotations", [])
                variant_props["reads"] = [
                    r.replace("{data}", str(DATA_DIR)) if "{data}" in r else r
                    for r in variant_props.get("reads", [])
                ]
                variant, _ = Variant.objects.update_or_create(**variant_props, project=project)

                for annotation_kwargs in annotations:
                    VariantAnnotation.objects.update_or_create(variant=variant, **annotation_kwargs)

                CurationAssignment.objects.update_or_create(curator=user, variant=variant)
