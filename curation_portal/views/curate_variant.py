# pylint: disable=too-many-locals
import os

from cloudpathlib.anypath import to_anypath
from django.conf import settings
from django.http.response import FileResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ChoiceField, ModelSerializer
from rest_framework.views import APIView

from curation_portal.filters import AssignmentFilter
from curation_portal.models import (
    FLAG_FIELDS,
    CurationAssignment,
    CurationResult,
    Variant,
    VariantAnnotation,
    VariantTag,
)
from curation_portal.serializers import CustomFlagCurationResultSerializer


class VariantAnnotationSerializer(ModelSerializer):
    class Meta:
        model = VariantAnnotation
        exclude = ("id", "variant")


class VariantTagSerializer(ModelSerializer):
    class Meta:
        model = VariantTag
        fields = ("label", "value")


class VariantSerializer(ModelSerializer):
    annotations = VariantAnnotationSerializer(many=True)
    tags = VariantTagSerializer(many=True)

    class Meta:
        model = Variant
        exclude = ("project",)


class CurationResultSerializer(ModelSerializer):
    verdict = ChoiceField(
        ["lof", "likely_lof", "uncertain", "likely_not_lof", "not_lof"],
        required=False,
        allow_null=True,
    )
    custom_flags = CustomFlagCurationResultSerializer(required=False, allow_null=True)

    class Meta:
        model = CurationResult
        fields = (
            *FLAG_FIELDS,
            "custom_flags",
            "notes",
            "curator_comments",
            "should_revisit",
            "verdict",
        )

    def create(self, validated_data):
        # Pop before calling super's update so we can handle the saving of custom flags manually.
        custom_flags = validated_data.pop("custom_flags", {})

        instance = super().create(validated_data)

        self.fields["custom_flags"].create(instance, custom_flags)
        return instance

    def update(self, instance, validated_data):
        # Pop before calling super's update so we can handle the saving of custom flags manually.
        custom_flags = validated_data.pop("custom_flags", {})

        instance = super().update(instance, validated_data)

        self.fields["custom_flags"].create(instance, custom_flags)
        return instance


def serialize_adjacent_variant(variant_values):
    if not variant_values:
        return None

    return {"id": variant_values["variant"], "variant_id": variant_values["variant__variant_id"]}


class ReadsFileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_assignment(self):
        try:
            assignment = self.request.user.curation_assignments.select_related("variant").get(
                variant=self.kwargs["variant_id"], variant__project=self.kwargs["project_id"]
            )
            return assignment
        except CurationAssignment.DoesNotExist as error:
            raise NotFound from error

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        assignment = self.get_assignment()  # 404 if assignment doesn't exist for a curator

        insecure_path = request.GET.get("file")
        if not insecure_path:
            raise ParseError

        # Add trailing slash into allowed directories if it doesn't exist.
        allowed_directories = [
            f"{allowed}/" if not allowed.endswith("/") else allowed
            for allowed in settings.ALLOWED_DIRECTORIES
        ]

        # Validate file path, and ensure it is from an allowed directory.
        secure_path = None
        for allowed in allowed_directories:
            # Clip the 'gs://' replacing it with '/' to get the real path since os.path.realpath
            # will try to express the path as a local path.
            path_to_validate = insecure_path
            if "gs://" in path_to_validate:
                path_to_validate = path_to_validate.replace("gs://", "/")

            # Real path will resolve symlinks and relative paths to prevent directory traversal.
            real_path = os.path.realpath(path_to_validate)
            if "gs://" in insecure_path:
                real_path = "gs:/" + real_path

            # File path is valid if it is relative to the allowed directory once directory
            # traversal has been resolved.
            if os.path.commonprefix([real_path, allowed]) == allowed:
                secure_path = to_anypath(allowed) / os.path.relpath(real_path, start=allowed)
                break

        if not secure_path:
            raise NotFound("Directory does not exist.")

        reads = assignment.variant.reads or []
        if str(secure_path) not in reads:
            raise NotFound("File not listed in variant.")

        secure_path = to_anypath(secure_path)
        if not secure_path.exists():
            raise NotFound("File for variant does not exist.")

        if not secure_path.is_file():
            raise ParseError("'file' must be a file, not a directory.")

        def stream_contents():
            # Using buffer_size to stream in manageable chunks.
            buffer_size = 8192
            with secure_path.open(mode="rb", buffering=buffer_size) as handle:
                for chunk in handle:
                    yield chunk

        return FileResponse(stream_contents(), as_attachment=False)


class CurateVariantView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_assignment(self):
        try:
            assignment = (
                self.request.user.curation_assignments.select_related("variant", "result")
                .prefetch_related("variant__annotations", "variant__tags", "result__custom_flags")
                .get(variant=self.kwargs["variant_id"], variant__project=self.kwargs["project_id"])
            )

            return assignment
        except CurationAssignment.DoesNotExist as error:
            raise NotFound from error

    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        assignment = self.get_assignment()

        filtered_assignments = AssignmentFilter(
            request.GET,
            request.user.curation_assignments.filter(variant__project=assignment.variant.project),
        )

        previous_site_variants = (
            filtered_assignments.qs.filter(variant__xpos__lt=assignment.variant.xpos)
            .order_by("variant__xpos", "variant__ref", "variant__alt")
            .reverse()
            .values("variant", "variant__variant_id")
        )
        num_previous_site_variants = previous_site_variants.count()
        previous_site_variant = previous_site_variants.first()

        colocated_variants = (
            filtered_assignments.qs.filter(variant__xpos=assignment.variant.xpos)
            .order_by("variant__xpos", "variant__ref", "variant__alt")
            .values("variant", "variant__variant_id")
        )

        next_site_variant = (
            filtered_assignments.qs.filter(variant__xpos__gt=assignment.variant.xpos)
            .order_by("variant__xpos", "variant__ref", "variant__alt")
            .values("variant", "variant__variant_id")
            .first()
        )

        surrounding_variants = [previous_site_variant, *colocated_variants, next_site_variant]
        index_in_surrounding_variants = [
            v["variant__variant_id"] if v is not None else None for v in surrounding_variants
        ].index(assignment.variant.variant_id)

        previous_variant = surrounding_variants[index_in_surrounding_variants - 1]
        next_variant = surrounding_variants[index_in_surrounding_variants + 1]

        index = num_previous_site_variants + index_in_surrounding_variants - 1

        return Response(
            {
                "index": index,
                "variant": VariantSerializer(assignment.variant).data,
                "next_variant": serialize_adjacent_variant(next_variant),
                "previous_variant": serialize_adjacent_variant(previous_variant),
                "result": CurationResultSerializer(assignment.result).data,
            }
        )

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        assignment = self.get_assignment()

        if assignment.result:
            result = assignment.result
        else:
            result = CurationResult()

        serializer = CurationResultSerializer(result, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        assignment.result = result
        assignment.save()

        return Response({})
