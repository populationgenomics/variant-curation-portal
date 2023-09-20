import verdicts from "../constants/verdicts";

const CurationFlagRules = (flags) => {
  const verdictFlags = Object.fromEntries(verdicts.map((verdict) => [verdict, false]));
  const trueFlags = Object.entries(flags).filter(
    ([flag, val]) =>
      (flag !== "custom_flags" && val && flag !== "verdict") ||
      (flag === "custom_flags" && Object.keys(val).length)
  );
  if (!trueFlags.length) {
    // if no flags selected, only lof can be chosen as verdict
    verdictFlags["lof"] = true;
    return verdictFlags;
  }
  if (flags["flag_flow_chart_overridden"]) {
    //overrides rules
    verdictFlags["lof"] = true;
    verdictFlags["likely_lof"] = true;
    verdictFlags["uncertain"] = true;
    verdictFlags["likely_not_lof"] = true;
    verdictFlags["not_lof"] = true;
    return verdictFlags;
  }
  if (flags["flag_no_read_data"]) {
    verdictFlags["uncertain"] = true;
    return verdictFlags;
  }
  if (flags["flag_reference_error"]) {
    verdictFlags["not_lof"] = true;
    return verdictFlags;
  }
  if (
    flags["flag_mapping_error"] ||
    flags["flag_genotype_error"] ||
    flags["flag_inconsequential_transcript"] ||
    flags["flag_rescue"]
  ) {
    verdictFlags["uncertain"] = true;
    verdictFlags["likely_not_lof"] = true;
    verdictFlags["not_lof"] = true;
    return verdictFlags;
  }
  if (trueFlags.some(([flag, value]) => flag !== "custom_flags")) {
    verdictFlags["lof"] = true;
    verdictFlags["likely_lof"] = true;
    verdictFlags["uncertain"] = true;
    return verdictFlags;
  }
  return verdictFlags;
};

export default CurationFlagRules;
