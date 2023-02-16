from django.core.management import BaseCommand

from curation_portal.models import User, Variant, Project, CurationAssignment, VariantAnnotation


VARIANTS = [
    {
        "reference_genome": "GRCh37",
        "variant_id": "1-898599-G-A",
        "liftover_variant_id": "1-963219-G-A",
        "chrom": "1",
        "pos": 898599,
        "xpos": 1000898599,
        "ref": "G",
        "alt": "A",
        "qc_filter": None,
        "AC": 1,
        "AN": 243720,
        "AF": 0.0000041,
        "n_homozygotes": 0,
        "annotations": [
            {
                "consequence": "stop_gained",
                "gene_id": "ENSG00000187961",
                "gene_symbol": "KLHL17",
                "loftee": None,
                "loftee_filter": None,
                "loftee_flags": None,
                "transcript_id": "ENST00000466300",
            }
        ],
    },
    {
        "reference_genome": "GRCh37",
        "variant_id": "1-949643-AC-A",
        "liftover_variant_id": None,
        "chrom": "2",
        "pos": 949643,
        "xpos": 1000949643,
        "ref": "AC",
        "alt": "A",
        "qc_filter": None,
        "AC": 1,
        "AN": 31398,
        "AF": 0.000031849162367029746,
        "n_homozygotes": 0,
        "annotations": [
            {
                "consequence": "frameshift_variant",
                "gene_id": "ENSG00000187608",
                "gene_symbol": "ISG15",
                "loftee": None,
                "loftee_filter": None,
                "loftee_flags": None,
                "transcript_id": "ENST00000379389",
            }
        ],
    },
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("username", help="Username of user to create assignments for")
        parser.add_argument("project", help="Name of project to add variants to")

    def handle(self, *args, **options):
        user, _ = User.objects.get_or_create(username=options["username"])
        project, _ = Project.objects.get_or_create(name=options["project"])

        project.owners.add(user)

        for variant_props in VARIANTS:
            # Pop annotations key before creating variant
            annotations = variant_props.pop("annotations", [])
            variant, _ = Variant.objects.get_or_create(**variant_props, project=project)

            for annotation_kwargs in annotations:
                VariantAnnotation.objects.get_or_create(variant=variant, **annotation_kwargs)

            CurationAssignment.objects.get_or_create(curator=user, variant=variant)
