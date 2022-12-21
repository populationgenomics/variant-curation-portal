import { mapValues, isEqual } from "lodash";

export const FLAGS = [
  // # Technical
  "flag_no_read_data",
  "flag_reference_error",
  // ## Mapping errors
  "flag_self_chain",
  "flag_str_or_low_complexity",
  "flag_low_umap_m50",
  // ### Dubious read alignment
  "flag_mismapped_read",
  "flag_complex_event",
  "flag_stutter",
  "flag_unknown",
  // ## Genotyping errors
  "flag_low_genotype_quality",
  "flag_low_read_depth",
  "flag_allele_balance",
  "flag_gc_rich",
  "flag_homopolymer_or_str",
  "flag_strand_bias",

  // # Impact
  // ## Inconsequential transcript
  "flag_multiple_annotations",
  "flag_pext_less_than_half_max",
  "flag_uninformative_pext",
  "flag_minority_of_transcripts",
  "flag_weak_exon_conservation",
  "flag_untranslated_transcript",
  // ## Rescue
  "flag_mnp",
  "flag_frame_restoring_indel",
  "flag_first_150_bp",
  "flag_in_frame_sai",
  "flag_methionine_resuce",
  "flag_escapes_nmd",
  "flag_low_truncated",

  // # Comment
  "flag_second_opinion_required",
  "flag_flow_chart_overridden",
];

export const FLAG_CODES = {
  // # Technical
  flag_no_read_data: "NR",
  flag_reference_error: "RE",
  // ## Mapping errors
  flag_self_chain: "SC",
  flag_str_or_low_complexity: "LC",
  flag_low_umap_m50: "M5",
  // ### Dubious read alignment
  flag_mismapped_read: "MM",
  flag_complex_event: "CE",
  flag_stutter: "TS",
  flag_unknown: "UN",
  // ## Genotyping errors
  flag_low_genotype_quality: "GQ",
  flag_low_read_depth: "RD",
  flag_allele_balance: "BA",
  flag_gc_rich: "GC",
  flag_homopolymer_or_str: "HO",
  flag_strand_bias: "BI",

  // # Impact
  // ## Inconsequential transcript
  flag_multiple_annotations: "MA",
  flag_pext_less_than_half_max: "P5",
  flag_uninformative_pext: "UP",
  flag_minority_of_transcripts: "MI",
  flag_weak_exon_conservation: "WE",
  flag_untranslated_transcript: "UT",
  // ## Rescue
  flag_mnp: "IN",
  flag_frame_restoring_indel: "FR",
  flag_first_150_bp: "F1",
  flag_in_frame_sai: "IF",
  flag_methionine_resuce: "MR",
  flag_escapes_nmd: "EN",
  flag_low_truncated: "TR",

  // # Comment
  flag_second_opinion_required: "OR",
  flag_flow_chart_overridden: "FO",
};

export const FLAG_LABELS = {
  // # Technical
  flag_no_read_data: "No read data",
  flag_reference_error: "Reference error",
  // ## Mapping errors
  flag_self_chain: "Self chain > 5",
  flag_str_or_low_complexity: "STR/Low complexity",
  flag_low_umap_m50: "Umap M50 < 0.5",
  // ### Dubious read alignment
  flag_mismapped_read: "Mis-mapped read",
  flag_complex_event: "Complex event",
  flag_stutter: "Stutter",
  flag_unknown: "Unknown",
  // ## Genotyping errors
  flag_low_genotype_quality: "Genotype quality < 30",
  flag_low_read_depth: "Read depth < 15",
  flag_allele_balance: "Allele balance het. < 0.25, hom. < 0.8",
  flag_gc_rich: "GC rich +/- 50 bp",
  flag_homopolymer_or_str: "Homopolymer/STR > 5",
  flag_strand_bias: "Strand bias",

  // # Impact
  // ## Inconsequential transcript
  flag_multiple_annotations: "Multiple annotations",
  flag_pext_less_than_half_max: "pext < 50% max",
  flag_uninformative_pext: "Uninformative pext",
  flag_minority_of_transcripts: "Minority of transcripts ≤ 50%",
  flag_weak_exon_conservation: "Weak exon conservation",
  flag_untranslated_transcript: "Untranslated transcript",
  // ## Rescue
  flag_mnp: "In-phase MNV",
  flag_frame_restoring_indel: "Frame-restoring indel",
  flag_first_150_bp: "First 150 bp",
  flag_in_frame_sai: "In-frame SAI ≥ 0.2",
  flag_methionine_resuce: "Methionine rescue",
  flag_escapes_nmd: "Escapes NMD",
  flag_low_truncated: "< 25% truncated",

  // # Comment
  flag_second_opinion_required: "Second opinion required",
  flag_flow_chart_overridden: "Flow chart overridden",
};

export const FLAG_SHORTCUTS = mapValues(FLAG_CODES, code =>
  code
    .toLowerCase()
    .split("")
    .join(" ")
);

if (process.env.NODE_ENV === "development") {
  const flagCodes = Object.values(FLAG_CODES);

  const duplicateCodes = new Set(flagCodes.filter((s, i, a) => i !== a.indexOf(s)));
  if (duplicateCodes.size > 0) {
    throw new Error(`Duplicate flag codes: ${Array.from(duplicateCodes).join(", ")}`);
  }

  if (!isEqual(FLAGS.sort(), Object.keys(FLAG_LABELS).sort())) {
    throw new Error("FLAGS and FLAG_LABELS must define the same keys.");
  }

  if (!isEqual(FLAGS.sort(), Object.keys(FLAG_CODES).sort())) {
    throw new Error("FLAGS and FLAG_SHORTCUTS must define the same keys.");
  }
}
