from django.core.management import BaseCommand

from curation_portal.models import CustomFlag


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("key", help="Unique key identifier")
        parser.add_argument("label", help="Human-readable flag label")
        parser.add_argument("shortcut", help="Keyboard shortcut")

    def handle(self, *args, **options):
        CustomFlag.objects.create(
            key=options["key"], label=options["label"], shortcut=options["shortcut"]
        )
