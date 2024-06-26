import json
import csv
import re

from django.db.models import Prefetch
from django.http import HttpResponse
from django_filters import FilterSet
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from curation_portal.models import (
    CurationAssignment,
    Project,
    VariantAnnotation,
    CustomFlag,
    FLAG_FIELDS,
    FLAG_LABELS,
    CurationResult,
    CustomFlagCurationResult,
    User,
)

from curation_portal.serializers import ExportedResultSerializer


class ExportResultsFilter(FilterSet):
    class Meta:
        model = CurationAssignment
        fields = {"curator__username": ["exact"]}


class ExportProjectResultsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_project(self):
        project = get_object_or_404(Project, id=self.kwargs["project_id"])
        if not self.request.user.has_perm("curation_portal.view_project", project):
            raise NotFound

        return project

    def get(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        project = self.get_project()

        completed_assignments = (
            CurationAssignment.objects.filter(
                variant__project=project, result__verdict__isnull=False
            )
            .select_related("curator", "variant", "result")
            .prefetch_related(
                Prefetch(
                    "variant__annotations",
                    queryset=VariantAnnotation.objects.only(
                        "variant_id", "gene_id", "gene_symbol", "transcript_id"
                    ),
                )
            )
        )

        # Project owners can download all results for the project and optionally filter them
        # by curator.
        # Curators can only download their own results.
        if request.user.has_perm("curation_portal.change_project", project):
            filter_params = request.query_params
        else:
            filter_params = {"curator__username": request.user.username}

        filtered_assignments = ExportResultsFilter(
            filter_params,
            queryset=completed_assignments,
        )

        # Prefetch related objects and annotations
        filtered_assignments_qs = filtered_assignments.qs.prefetch_related(
            Prefetch(
                "result__custom_flags",
                queryset=CustomFlagCurationResult.objects.select_related("flag"),
            ),
            Prefetch(
                "result__editor",
                queryset=User.objects.only("username"),
            ),
        )

        # Include project name and (if applicable) curator name in downloaded file name.
        filename_prefix = f"{project.name}"
        if "curator__username" in filter_params:
            filename_prefix += "_" + filter_params["curator__username"]

        # Based on django.utils.text.get_valid_filename, but replace characters with "-" instead
        # of removing them.
        filename_prefix = re.sub(r"(?u)[^-\w]", "-", filename_prefix)

        if request.query_params.get("format") == "json":
            return self.get_json_response(filtered_assignments_qs, filename_prefix)
        else:
            return self.get_csv_response(filtered_assignments_qs, filename_prefix)

    def get_json_response(self, filtered_assignments_qs, filename_prefix):
        response = HttpResponse(content_type="application/json")
        response["Content-Disposition"] = f'attachment; filename="{filename_prefix}_results.json"'

        project = self.get_project()
        curation_results = CurationResult.objects.filter(
            assignment__in=filtered_assignments_qs
        ).prefetch_related(
            Prefetch(
                "custom_flags",
                queryset=CustomFlagCurationResult.objects.select_related("flag"),
            ),
        )
        serializer = ExportedResultSerializer(
            instance=curation_results,
            many=True,
            context={"project": project},
        )
        response.write(json.dumps(serializer.data))

        return response

    def get_csv_response(self, filtered_assignments_qs, filename_prefix):
        result_fields = ["notes", "curator_comments", "should_revisit", "verdict", *FLAG_FIELDS]

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename_prefix}_results.csv"'

        writer = csv.writer(response)

        header_row = ["Variant ID", "Gene", "Transcript", "Curator", "Editor"] + [
            FLAG_LABELS.get(f, " ".join(word.capitalize() for word in f.split("_")))
            for f in result_fields
        ]
        # Custom flag headers
        custom_flags = CustomFlag.objects.all()
        header_row += [f.label for f in custom_flags]

        writer.writerow(header_row)

        for assignment in filtered_assignments_qs:
            editor = assignment.result.editor
            custom_flag_results = {
                flag.flag.key: flag.checked for flag in assignment.result.custom_flags.all()
            }

            row = (
                [
                    assignment.variant.variant_id,
                    ";".join(
                        set(
                            f"{annotation.gene_id}:{annotation.gene_symbol}"
                            for annotation in assignment.variant.annotations.all()
                        )
                    ),
                    ";".join(
                        set(
                            annotation.transcript_id
                            for annotation in assignment.variant.annotations.all()
                        )
                    ),
                    assignment.curator.username,
                    editor.username if editor else None,
                ]
                + [getattr(assignment.result, f) for f in result_fields]
                # Custom flag results
                + [custom_flag_results.get(flag.key, False) for flag in custom_flags]
            )
            writer.writerow(row)

        return response
