export const FLAGS = [
  // # Technical
  { key: "flag_no_read_data", label: "No read data", shortcut: "NR" },
  { key: "flag_reference_error", label: "Reference error", shortcut: "RE" },
  // ## Mapping Error
  { key: "flag_mapping_error", label: "Mapping Error", shortcut: null },
  { key: "flag_self_chain", label: "Self chain > 5", shortcut: "C5" },
  { key: "flag_str_or_low_complexity", label: "STR/Low complexity", shortcut: "LC" },
  { key: "flag_low_umap_m50", label: "Umap M50 < 0.5", shortcut: "M5" },
  // ### Dubious Read Alignment
  { key: "flag_dubious_read_alignment", label: "Dubious Read Alignment", shortcut: null },
  { key: "flag_mismapped_read", label: "Mis-mapped read", shortcut: "MM" },
  { key: "flag_complex_event", label: "Complex Event", shortcut: "CE" },
  { key: "flag_stutter", label: "Stutter", shortcut: "FS" },
  { key: "flag_repetitive_sequence", label: "Repetitive sequence", shortcut: "RS" },
  { key: "flag_dubious_other", label: "Other", shortcut: "DO" },
  // ## Genotyping Error
  { key: "flag_genotyping_error", label: "Genotyping Error", shortcut: null },
  { key: "flag_low_genotype_quality", label: "Genotype quality < 30", shortcut: "GQ" },
  { key: "flag_low_read_depth", label: "Read depth < 15", shortcut: "RD" },
  { key: "flag_allele_balance", label: "Allele balance het. < 0.25, hom. < 0.8", shortcut: "BA" },
  { key: "flag_gc_rich", label: "GC rich +/- 50 bp", shortcut: "GC" },
  { key: "flag_homopolymer_or_str", label: "Homopolymer/STR > 5", shortcut: "HO" },
  { key: "flag_strand_bias", label: "Strand bias", shortcut: "BI" },
  // # Impact
  // ## Inconsequential Transcript
  { key: "flag_inconsequential_transcript", label: "Inconsequential Transcript", shortcut: null },
  { key: "flag_multiple_annotations", label: "Multiple annotations", shortcut: "MA" },
  { key: "flag_pext_less_than_half_max", label: "pext < 50% max", shortcut: "P5" },
  { key: "flag_uninformative_pext", label: "Uninformative pext", shortcut: "UP" },
  { key: "flag_minority_of_transcripts", label: "Minority of transcripts ≤ 50%", shortcut: "MI" },
  {
    key: "flag_minor_protein_isoform",
    label: "Minor protein isoform (MANE/APPRIS)",
    shortcut: "MP",
  },
  { key: "flag_weak_exon_conservation", label: "Weak exon conservation", shortcut: "WE" },
  { key: "flag_untranslated_transcript", label: "Untranslated transcript", shortcut: "UT" },
  // ## Rescue
  { key: "flag_rescue", label: "Rescue", shortcut: null },
  { key: "flag_mnp", label: "In-phase MNV", shortcut: "IN" },
  { key: "flag_frame_restoring_indel", label: "Frame-restoring indel", shortcut: "FR" },
  { key: "flag_first_150_bp", label: "First 150 bp", shortcut: "F1" },
  { key: "flag_in_frame_sai", label: "In-frame SAI ≥ 0.2", shortcut: "IF" },
  { key: "flag_methionine_resuce", label: "Methionine rescue", shortcut: "MR" },
  { key: "flag_escapes_nmd", label: "Escapes NMD", shortcut: "EN" },
  { key: "flag_low_truncated", label: "< 25% truncated", shortcut: "TR" },
  // # Comment
  { key: "flag_complex_splicing", label: "Complex splicing 🐰", shortcut: "CS" },
  { key: "flag_complex_other", label: "Complex other 🐰", shortcut: "CO" },
  { key: "flag_second_opinion_required", label: "Second opinion required", shortcut: "OR" },
  { key: "flag_flow_chart_overridden", label: "Flow chart overridden", shortcut: "FO" },
  {
    key: "flag_sanger_confirmation_recommended",
    label: "Sanger confirmation recommended",
    shortcut: "CR",
  },
];

export const FLAG_CODES = Object.fromEntries(FLAGS.map(f => [f.key, f.shortcut]));
export const FLAG_LABELS = Object.fromEntries(FLAGS.map(f => [f.key, f.label]));
export const FLAG_SHORTCUTS = Object.fromEntries(
  FLAGS.map(f => [
    f.key,
    f.shortcut
      ? f.shortcut
          .toLowerCase()
          .split("")
          .join(" ")
      : f.shortcut,
  ])
);

if (process.env.NODE_ENV === "development") {
  const flagCodes = Object.values(FLAG_CODES).filter(v => v != null);

  const duplicateCodes = new Set(flagCodes.filter((s, i, a) => i !== a.indexOf(s)));
  if (duplicateCodes.size > 0) {
    throw new Error(`Duplicate flag codes: ${Array.from(duplicateCodes).join(", ")}`);
  }
}
