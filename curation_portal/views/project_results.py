from django.db import transaction
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ChoiceField, ModelSerializer, SerializerMethodField
from rest_framework.views import APIView

from curation_portal.models import CurationResult, Project, Variant, User, FLAG_FIELDS
from curation_portal.serializers import ImportedResultSerializer, CustomFlagCurationResultSerializer


class VariantSerializer(ModelSerializer):
    class Meta:
        model = Variant
        fields = ("id", "variant_id")


class CuratorSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class EditorSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class CurationResultSerializer(ModelSerializer):
    variant = SerializerMethodField()

    def get_variant(self, obj):  # pylint: disable=no-self-use
        return VariantSerializer(obj.assignment.variant).data

    curator = SerializerMethodField()

    def get_curator(self, obj):  # pylint: disable=no-self-use
        return CuratorSerializer(obj.assignment.curator).data

    editor = SerializerMethodField()

    def get_editor(self, obj):  # pylint: disable=no-self-use
        return EditorSerializer(obj.assignment.result.editor).data

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
            "variant",
            "curator",
            "editor",
        )


class ProjectResultsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        if not self.request.user.has_perm("curation_portal.change_project", project):
            if not self.request.user.has_perm("curation_portal.view_project", project):
                raise NotFound

            raise PermissionDenied

        return project

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        project = self.get_project()

        results = CurationResult.objects.filter(
            assignment__variant__project=project
        ).prefetch_related("assignment__curator", "assignment__variant", "custom_flags__flag")
        serializer = CurationResultSerializer(results, many=True)
        return Response({"results": serializer.data})

    def post(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        project = self.get_project()

        serializer = ImportedResultSerializer(
            data=request.data, context={"project": project, "request": request}, many=True
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            serializer.save()
            project.save()  # Save project to set updated_at timestamp

        return Response({})
