from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from curation_portal.models import Variant


class VariantsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        variants = (
            Variant.objects.filter(
                Q(project__owners__id__contains=request.user.id)
                | Q(curation_assignment__curator=request.user)
            )
            .values_list("variant_id", "liftover_variant_id", "reference_genome")
            .distinct()
        )

        return Response(
            {
                "variants": [
                    {
                        "variant_id": variant_id,
                        "liftover_variant_id": liftover_variant_id,
                        "reference_genome": reference_genome,
                    }
                    for (variant_id, liftover_variant_id, reference_genome) in variants
                ],
            }
        )
