#!/usr/bin/env python3

import argparse
from cloudpathlib import AnyPath

import hail as hl
import pandas as pd
import requests

from cpg_utils.hail_batch import init_batch, dataset_path, output_path

CONSEQUENCE_TERMS = [
    "transcript_ablation",
    "splice_acceptor_variant",
    "splice_donor_variant",
    "stop_gained",
    "frameshift_variant",
    "stop_lost",
    "start_lost",  # new in v81
    "initiator_codon_variant",  # deprecated
    "transcript_amplification",
    "inframe_insertion",
    "inframe_deletion",
    "missense_variant",
    "protein_altering_variant",  # new in v79
    "splice_region_variant",
    "incomplete_terminal_codon_variant",
    "start_retained_variant",
    "stop_retained_variant",
    "synonymous_variant",
    "coding_sequence_variant",
    "mature_miRNA_variant",
    "5_prime_UTR_variant",
    "3_prime_UTR_variant",
    "non_coding_transcript_exon_variant",
    "non_coding_exon_variant",  # deprecated
    "intron_variant",
    "NMD_transcript_variant",
    "non_coding_transcript_variant",
    "nc_transcript_variant",  # deprecated
    "upstream_gene_variant",
    "downstream_gene_variant",
    "TFBS_ablation",
    "TFBS_amplification",
    "TF_binding_site_variant",
    "regulatory_region_ablation",
    "regulatory_region_amplification",
    "feature_elongation",
    "regulatory_region_variant",
    "feature_truncation",
    "intergenic_variant",
]

# Maps each consequence term to its rank in the list
CONSEQUENCE_TERM_RANK = hl.dict({term: rank for rank, term in enumerate(CONSEQUENCE_TERMS)})

PLOF_CONSEQUENCE_TERMS = hl.set(
    [
        "transcript_ablation",
        "splice_acceptor_variant",
        "splice_donor_variant",
        "stop_gained",
        "frameshift_variant",
    ]
)

GNOMAD_V2_EXOMES = (
    "gs://gcp-public-data--gnomad/release/2.1.1/ht/exomes/gnomad.exomes.r2.1.1.sites.ht"
)
GNOMAD_V2_GENOMES = (
    "gs://gcp-public-data--gnomad/release/2.1.1/ht/genomes/gnomad.genomes.r2.1.1.sites.ht"
)
GNOMAD_V2_EXOME_LIFTOVER = 'gs://cpg-common-main/references/liftover/hg37_pruned/gnomad.exomes.r2.1.1.sites.liftover_grch37.ht'
GNOMAD_V2_GENOME_LIFTOVER = 'gs://cpg-common-main/references/liftover/hg37_pruned/gnomad.genomes.r2.1.1.sites.liftover_grch37.ht'
GNOMAD_V2_CONSTRAINT = "gs://gcp-public-data--gnomad/release/2.1.1/constraint/gnomad.v2.1.1.lof_metrics.by_transcript.ht"
GNOMAD_V2_CURATION = [
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/all_homozygous_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/lysosomal_storage_disease_genes_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/haploinsufficient_genes_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/metabolic_conditions_genes_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/gnomAD_addendum_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/AP4_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/FIG4_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/MCOLN1_curation_results.csv",
    "https://storage.googleapis.com/gcp-public-data--gnomad/truth-sets/source/lof-curation/NSD1_curation_results.csv",
]
GNOMAD_V3_GENOMES = (
    "gs://gcp-public-data--gnomad/release/3.1.1/ht/genomes/gnomad.genomes.v3.1.1.sites.ht"
)
GNOMAD_V3_EXOME_LIFTOVER = (
    'gs://cpg-common-main/references/liftover/gnomad.exomes.r2.1.1.sites.liftover_grch38.ht'
)
GNOMAD_V3_GENOME_LIFTOVER = (
    'gs://cpg-common-main/references/liftover/gnomad.genomes.r2.1.1.sites.liftover_grch38.ht'
)


def load_gnomad_v2_variants():
    exomes = hl.read_table(GNOMAD_V2_EXOMES)
    exomes = exomes.select(exome=exomes.row_value)

    genomes = hl.read_table(GNOMAD_V2_GENOMES)
    genomes = genomes.select(genome=genomes.row_value)

    exomes = exomes.select_globals()
    genomes = genomes.select_globals()
    ds = exomes.join(genomes, how="outer")
    ds = ds.annotate(vep=hl.or_else(ds.exome.vep, ds.genome.vep))
    ds = ds.annotate(exome=ds.exome.drop("vep"), genome=ds.genome.drop("vep"))

    return ds


def load_gnomad_v3_variants():
    ds = hl.read_table(GNOMAD_V3_GENOMES)
    ds = ds.select(genome=ds.row_value.drop("vep"), vep=ds.vep)
    ds = ds.annotate(exome=hl.missing(ds.genome.dtype))

    return ds


def add_liftover_mapping(ds, reference_genome, sequencing_type='genome'):
    """
    Load the gnomAD liftover Hail tables depending on the reference genome
    Add a mapping from the hg37 sites to the hg38 sites to the dataset (or vice versa)
    """
    if reference_genome == "GRCh37":
        # hg38 fields: ['locus', 'alleles']
        if sequencing_type == 'exome':
            exome_liftover_mapping = hl.read_table(GNOMAD_V2_EXOME_LIFTOVER)
            ds = ds.annotate(
                liftover_locus=exome_liftover_mapping[ds.locus, ds.alleles].locus,
                liftover_alleles=exome_liftover_mapping[ds.locus, ds.alleles].alleles,
            )
            
        elif sequencing_type == 'genome':
            genome_liftover_mapping = hl.read_table(GNOMAD_V2_GENOME_LIFTOVER)
            ds = ds.annotate(
                liftover_locus=genome_liftover_mapping[ds.locus, ds.alleles].locus,
                liftover_alleles=genome_liftover_mapping[ds.locus, ds.alleles].alleles,
            )
        else:
            raise Exception(f"Invalid sequencing type {sequencing_type}")

    elif reference_genome == "GRCh38":
        # hg37 fields: ['original_locus', 'original_alleles']
        if sequencing_type == 'exome':
            exome_liftover_mapping = hl.read_table(GNOMAD_V3_EXOME_LIFTOVER)
            ds = ds.annotate(
                liftover_locus=exome_liftover_mapping[ds.locus, ds.alleles].original_locus,
                liftover_alleles=exome_liftover_mapping[ds.locus, ds.alleles].original_alleles,
            )
            
        elif sequencing_type == 'genome':
            genome_liftover_mapping = hl.read_table(GNOMAD_V3_GENOME_LIFTOVER)
            ds = ds.annotate(
                liftover_locus=genome_liftover_mapping[ds.locus, ds.alleles].original_locus,
                liftover_alleles=genome_liftover_mapping[ds.locus, ds.alleles].original_alleles,
            )
        else:
            raise Exception(f"Invalid sequencing type {sequencing_type}")

    else:
        raise Exception(f"Invalid reference genome {reference_genome}")

    return ds


def variant_id(locus, alleles):
    if hl.is_missing(locus) or hl.is_missing(alleles):
        return hl.missing(hl.tstr)
    return (
        locus.contig.replace("^chr", "")
        + "-"
        + hl.str(locus.position)
        + "-"
        + alleles[0]
        + "-"
        + alleles[1]
    )


def add(a, b):
    return hl.or_else(a, 0) + hl.or_else(b, 0)


def get_gnomad_lof_variants(
    gnomad_version,
    gene_ids,
    include_low_confidence=False,
    annotate_caf=False,
    flag_curated="ignore",
):
    if gnomad_version not in (2, 3):
        raise Exception(f"Invalid gnomAD version {gnomad_version}")

    if gnomad_version == 2:
        ds = load_gnomad_v2_variants()
    elif gnomad_version == 3:
        ds = load_gnomad_v3_variants()

    reference_genome = "GRCh37" if gnomad_version == 2 else "GRCh38"

    # Work around rate limit of the gnomAD API for fetching gene intervals by
    # using the GENCODE table directly.
    # Would need to provide the correct GENCODE GTF here for gnomAD v3.
    assert gnomad_version == 2

    if args.id_type == "symbol":
        gene_intervals = hl.experimental.get_gene_intervals(
            gene_symbols=gene_ids, reference_genome=reference_genome
        )
    else:
        gene_intervals = hl.experimental.get_gene_intervals(
            gene_ids=gene_ids, reference_genome=reference_genome
        )

    ds = hl.filter_intervals(ds, gene_intervals)

    gene_ids = hl.set(gene_ids)

    # Filter to variants which have pLoF consequences in the selected genes.
    ds = ds.annotate(
        lof_consequences=ds.vep.transcript_consequences.filter(
            lambda csq: (
                gene_ids.contains(csq.gene_symbol if args.id_type == "symbol" else csq.gene_id)
                & csq.consequence_terms.any(lambda term: PLOF_CONSEQUENCE_TERMS.contains(term))
                & (include_low_confidence | (csq.lof == "HC"))
            )
        )
    )
    ds = ds.filter(hl.len(ds.lof_consequences) > 0)

    # Filter to variants that passed QC filters in at least one of exomes/genomes
    ds = ds.filter((hl.len(ds.exome.filters) == 0) | (hl.len(ds.genome.filters) == 0))

    # Add the liftover mapping to hg37 or hg38 from the gnomAD liftover tables
    ds = add_liftover_mapping(ds, reference_genome, sequencing_type='exome' if args.exome else 'genome')

    # Format for the LoF curation portal.
    ds = ds.select(
        reference_genome=reference_genome,
        variant_id=variant_id(ds.locus, ds.alleles),
        # Compute and store a chr:pos of liftover variant, since we don't need the
        # allele info for the LoF curation portal.
        liftover_variant_id=variant_id(ds.liftover_locus, ds.liftover_alleles),
        qc_filter=hl.delimit(
            hl.array(ds.exome.filters)
            .map(lambda f: f + " (exomes)")
            .extend(hl.array(ds.genome.filters).map(lambda f: f + " (genomes)")),
            ", ",
        ),
        AC=add(ds.exome.freq[0].AC, ds.genome.freq[0].AC),
        AN=add(ds.exome.freq[0].AN, ds.genome.freq[0].AN),
        n_homozygotes=add(ds.exome.freq[0].homozygote_count, ds.genome.freq[0].homozygote_count),
        annotations=ds.lof_consequences.map(
            lambda csq: csq.select(
                "gene_id",
                "gene_symbol",
                "transcript_id",
                consequence=hl.sorted(csq.consequence_terms, lambda t: CONSEQUENCE_TERM_RANK[t])[0],
                loftee=csq.lof,
                loftee_flags=csq.lof_flags,
                loftee_filter=csq.lof_filter,
            )
        ),
    )

    ds = ds.annotate(
        qc_filter=hl.if_else(ds.qc_filter == "", "PASS", ds.qc_filter),
        AF=hl.if_else(ds.AN == 0, 0, ds.AC / ds.AN),
    )

    # Optionally annotate with CAF estimates.
    if annotate_caf and gnomad_version == 2:
        # Load the gnomAD v2 constraint table.
        constraint = hl.read_table(GNOMAD_V2_CONSTRAINT)

        # Filter to our genes of interest.
        constraint = constraint.filter(
            gene_ids.contains(constraint.gene if args.id_type == "symbol" else constraint.gene_id)
        )
        constraint = constraint.repartition(10)

        # Convert the constraint table to a lookup dictionary, so that map can handle it.
        caf_max = constraint.aggregate(
            hl.agg.group_by(constraint.transcript, hl.agg.max(constraint.classic_caf))
        )
        lookup = hl.dict(
            {k: caf_max[k] if caf_max[k] != None else hl.missing("float64") for k in caf_max.keys()}
        )

        # Add the CAF information for each transcript to the annotations structs.
        ds = ds.select(
            "reference_genome",
            "variant_id",
            "liftover_variant_id",
            "qc_filter",
            "AC",
            "AN",
            "n_homozygotes",
            "AF",
            annotations=ds.annotations.map(
                lambda csq: csq.annotate(
                    classic_caf=hl.if_else(
                        lookup.contains(csq.transcript_id),
                        lookup[csq.transcript_id],
                        hl.missing("float64"),
                    )
                )
            ),
        )

    # Optionally annotate with the results of the previous gnomAD v2 curation.
    if flag_curated != "ignore" and gnomad_version == 2:
        # Loop through all the curation files and read them into pandas.
        df_list = (
            pd.read_csv(file, usecols=["Variant ID", "Verdict"]) for file in GNOMAD_V2_CURATION
        )

        # Combine, and convert to a hail table.
        curation = hl.Table.from_pandas(pd.concat(df_list, ignore_index=True))

        # Key the curation results by the locus and alleles.
        curation = curation.key_by(
            **hl.parse_variant(curation["Variant ID"].replace("-", ":"), reference_genome="GRCh37")
        )

        # Annotate already-curated variants with their verdict.
        ds = ds.annotate(**curation[ds.locus, ds.alleles].select("Verdict")).rename(
            {"Verdict": "curation_verdict"}
        )

        # Optionally remove those variants that have already been curated.
        if flag_curated == "remove":
            ds = ds.filter(hl.is_missing(ds.curation_verdict))

    return ds


def open_file(path, mode="r"):
    if path.startswith("gs://"):
        return hl.hadoop_open(path, mode)
    else:
        return open(path, mode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get gnomAD pLoF variants in selected genes.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--gene-ids",
        nargs="+",
        metavar="GENE",
        help="The gene(s) to process, in the format specified by --id-type (defaults to Ensembl ID)",
    )
    group.add_argument(
        "--genes-table",
        help="relative dataset path (analysis category) to a Hail table with a gene_id field containing Ensembl IDs",
    )
    group.add_argument(
        "--genes-file",
        help="Full GCP path to a txt file with one gene per line, in the format specified by --id-type (defaults to Ensembl ID)",
    )
    parser.add_argument(
        "--id-type",
        choices=("ensembl", "symbol"),
        default="ensembl",
        help="The type of gene ID provided; must be one of 'ensembl' or 'symbol'",
    )
    parser.add_argument(
        "--gnomad-version",
        type=int,
        choices=(2, 3),
        default=2,
        help="gnomAD dataset to get variants from (defaults to %(default)s)",
    )
    parser.add_argument(
        "--include-low-confidence",
        action="store_true",
        help="Include variants marked low-confidence or otherwise flagged by LOFTEE",
    )
    parser.add_argument(
        "--annotate-caf",
        action="store_true",
        help="Annotate the variants with cumulative allele frequency estimates (gnomAD v2 only)",
    )
    parser.add_argument(
        "--flag-curated",
        type=str,
        choices=("ignore", "flag", "remove"),
        default="ignore",
        help="Optionally flag or remove variants that have already been curated (gnomAD v2 only)",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="relative dataset path (analysis category) for variants file",
    )
    parser.add_argument(
        "--exome",
        action="store_true",
        help="Use the gnomAD exome liftover tables (defaults to genome)",
    )
    args = parser.parse_args()

    init_batch()

    # Select the genes to process.
    if args.gene_ids:
        genes = args.gene_ids
    elif args.genes_file:
        with AnyPath(args.genes_file).open("r") as f:
            genes = [line.strip().split(",", 1)[0].split(None, 1)[0] for line in f if line.strip()]
    else:
        genes_table = hl.read_table(dataset_path(args.genes_table, "analysis"))
        genes = list(set(genes_table.gene_id.collect()))
        args.id_type = "ensembl"

    # Fetch the (optionally filtered and annotated) pLoF variants from the appropriate gnomAD dataset.
    variants = get_gnomad_lof_variants(
        args.gnomad_version,
        genes,
        include_low_confidence=args.include_low_confidence,
        annotate_caf=args.annotate_caf,
        flag_curated=args.flag_curated,
    )

    # Output the final dataset, as either:
    # A Hail table if extension is ".ht";
    if args.output.endswith(".ht"):
        variants.write(output_path(args.output, "analysis"))
    # A flattened TSV file, suitable for R and pandas, if extension is ".tsv.bgz";
    elif args.output.endswith(".tsv.bgz"):
        variants = variants.explode("annotations")
        variants = variants.flatten()
        variants.export(output_path(args.output, "analysis"))
    # A JSON file otherwise.
    else:
        rows = variants.annotate(json=hl.json(variants.row_value)).key_by().select("json").collect()
        with open_file(output_path(args.output, "analysis"), "w") as f:
            f.write("[" + ",".join([row.json for row in rows]) + "]")
