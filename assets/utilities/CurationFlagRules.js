import verdicts from "../constants/verdicts";
import { FLAGS } from "../constants/flags";

export class CurationResultVerdictValidator {
  constructor() {
    this.flags = FLAGS.map((f) => f.key);
  }

  isValid(result) {
    const { verdict } = result;
    if (!verdict) return true;

    return this.getValidVerdicts(result).includes(verdict);
  }

  verdictIsAllowed(result, verdict) {
    return this.getValidVerdicts(result).includes(verdict);
  }

  getValidVerdicts(result) {
    const flags = Object.fromEntries(
      Object.entries(result).filter(([key]) => this.flags.includes(key))
    );

    // Note: These don't include custom flags.
    const anyFlagChecked = Object.values(flags).some((v) => v);

    if (!anyFlagChecked) {
      // if no flags selected, only lof can be chosen as verdict
      return ["lof"];
    }

    if (flags.flag_flow_chart_overridden) {
      // overrides rules, allow all.
      return [...verdicts];
    }

    if (flags.flag_no_read_data) {
      return ["uncertain"];
    }

    if (flags.flag_reference_error) {
      return ["not_lof"];
    }

    if (
      flags.flag_mapping_error ||
      flags.flag_genotyping_error ||
      flags.flag_inconsequential_transcript ||
      flags.flag_rescue
    ) {
      return ["uncertain", "likely_not_lof", "not_lof"];
    }

    // If at least one flag is selected (that's not [mapping_error, genotype_error,
    // inconsequential_transcript, rescue, no_read_data, reference_error, flow_Chart_overridden,
    // any custom_flag]) then only 'LoF', 'likely LoF' and 'Uncertain' can be selected
    if (anyFlagChecked) {
      return ["lof", "likely_lof", "uncertain"];
    }

    // No rules are satisfied, no verdicts are allowed.
    return [];
  }
}

export default CurationResultVerdictValidator;
