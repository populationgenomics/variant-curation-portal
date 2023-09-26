from curation_portal.constants import VERDICTS


def allowed_verdicts(curation_result):
    from curation_portal.models import CurationResult

    any_flag_checked = any(
        [
            getattr(curation_result, f.name)
            for f in CurationResult._meta.get_fields()
            if f.name.startswith("flag_")
        ]
    )

    if not any_flag_checked:
        return ["lof"]

    if curation_result.flag_flow_chart_overridden:
        return [*VERDICTS]

    if curation_result.flag_no_read_data:
        return ["uncertain"]

    if curation_result.flag_reference_error:
        return ["not_lof"]

    if (
        curation_result.flag_mapping_error
        or curation_result.flag_genotyping_error
        or curation_result.flag_inconsequential_transcript
        or curation_result.flag_rescue
    ):
        return ["uncertain", "likely_not_lof", "not_lof"]

    if any_flag_checked:
        return ["lof", "likely_lof", "uncertain"]

    return []


def verdict_is_valid(curation_result):
    if not curation_result.verdict:
        return True

    allowed = allowed_verdicts(curation_result)
    return curation_result.verdict in allowed
