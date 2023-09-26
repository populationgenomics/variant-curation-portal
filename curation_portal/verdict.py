from rest_framework.exceptions import ValidationError

from curation_portal.constants import VERDICTS
from curation_portal.models import CurationResult


def allowed_verdicts(curation_result):
    if isinstance(curation_result, CurationResult):
        curation_result = {
            f.name: getattr(curation_result, f.name) for f in curation_result._meta.get_fields()
        }

    if not isinstance(curation_result, dict):
        raise TypeError("curation_result must be a dict or CurationResult instance")

    any_flag_checked = any(
        [value for (key, value) in curation_result.items() if key.startswith("flag_")]
    )

    if not any_flag_checked:
        return ["lof"]

    if curation_result.get("flag_flow_chart_overridden", False):
        return [*VERDICTS]

    if curation_result.get("flag_no_read_data", False):
        return ["uncertain"]

    if curation_result.get("flag_reference_error", False):
        return ["not_lof"]

    if (
        curation_result.get("flag_mapping_error", False)
        or curation_result.get("flag_genotyping_error", False)
        or curation_result.get("flag_inconsequential_transcript", False)
        or curation_result.get("flag_rescue", False)
    ):
        return ["uncertain", "likely_not_lof", "not_lof"]

    if any_flag_checked:
        return ["lof", "likely_lof", "uncertain"]

    return []


def verdict_is_valid(curation_result):
    if isinstance(curation_result, CurationResult):
        curation_result = {
            f.name: getattr(curation_result, f.name) for f in curation_result._meta.get_fields()
        }

    if not isinstance(curation_result, dict):
        raise TypeError("curation_result must be a dict or CurationResult instance")

    verdict = curation_result.get("verdict", None)
    if not verdict:
        return True

    allowed = allowed_verdicts(curation_result)
    return verdict in allowed


def validate_result_verdict(data):
    if not verdict_is_valid(data):
        allowed = allowed_verdicts(data)
        human_readable_allowed = [f"{v} ({VERDICTS.index(v) + 1})" for v in allowed]
        raise ValidationError(
            detail={
                "verdict": f"Verdict is not compatible with the current selection of flags. "
                f"Compatible choices are {', '.join(human_readable_allowed)}."
            }
        )

    return
