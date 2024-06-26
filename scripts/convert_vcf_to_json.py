#!/usr/bin/env python3

# pip install PyVCF==0.6.8 tqdm==4.31.1

import argparse
import gzip
import json
import re

import hail as hl
import vcf
from tqdm import tqdm

RANKED_CONSEQUENCE_TERMS = [
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

CONSEQUENCE_TERM_RANK = {term: rank for rank, term in enumerate(RANKED_CONSEQUENCE_TERMS)}


def get_rank(annotation):
    terms = annotation["Consequence"].split("&")
    return min(CONSEQUENCE_TERM_RANK.get(t) for t in terms)


def variant_coordinate_id(locus):
    return locus.contig.replace("^chr", "") + "-" + hl.str(locus.position)


def convert_vcf_to_json(vcf_path, output_path, reference_genome="GRCh37", tag_fields=None):
    variants = {}

    # Initialise reference genome with liftover information
    hl_reference_genome = hl.get_reference(reference_genome)
    if reference_genome == "GRCh37":
        hl_reference_genome.add_liftover(
            "gs://hail-common/references/grch37_to_grch38.over.chain.gz",
            "GRCh38",
        )
    else:
        hl_reference_genome.add_liftover(
            "gs://hail-common/references/grch38_to_grch37.over.chain.gz",
            "GRCh37",
        )

    with gzip.open(vcf_path, "rt") as vcf_file:
        reader = vcf.Reader(vcf_file, compressed=False)

        csq_header = (
            reader.infos["CSQ"]  # pylint: disable=unsubscriptable-object
            .desc.split("Format: ")[1]
            .split("|")
        )

        for row in tqdm(reader, unit=" rows"):
            if len(row.ALT) > 1:
                raise Exception(
                    "VCF contains multiallelic rows, which are not supported by this script"
                )

            # Parse CSQ field
            vep_annotations = [dict(zip(csq_header, v.split("|"))) for v in row.INFO.get("CSQ", [])]

            # Filter to only LoF annotations
            lof_annotations = [
                annotation
                for annotation in vep_annotations
                if get_rank(annotation) <= CONSEQUENCE_TERM_RANK.get("frameshift_variant")
            ]

            # Sort annotations by severity
            lof_annotations = sorted(lof_annotations, key=get_rank)

            variant_id = "-".join(
                map(str, [re.sub(r"^chr", "", row.CHROM), row.POS, row.REF, row.ALT[0]])
            )

            if not lof_annotations:
                print(f"Skipping {variant_id}, no LoF annotations")
                continue

            liftover_field = "liftover_37" if reference_genome == "GRCh38" else "liftover_38"
            liftover_variant_id = row.INFO.get(liftover_field, None)
            if liftover_variant_id:
                liftover_variant_id = liftover_variant_id.replace(":", "-")
            else:
                # Compute and store a chr:pos of liftover variant, since we don't need the
                # allele info
                liftover_variant_id = hl.eval(
                    variant_coordinate_id(
                        hl.liftover(
                            hl.parse_variant(variant_id.replace("-", ":"), reference_genome)[0],
                            "GRCh38" if reference_genome == "GRCh37" else "GRCh37",
                        )
                    )
                )

            if variant_id not in variants:
                variants[variant_id] = {
                    "reference_genome": reference_genome,
                    "variant_id": variant_id,
                    "liftover_variant_id": liftover_variant_id,
                    "qc_filter": (row.FILTER.join(",") if row.FILTER else "PASS"),
                    "AC": row.INFO["AC"],
                    "AN": row.INFO["AN"],
                    "AF": row.INFO["AF"],
                    "n_homozygotes": sum(1 for s in list(row.samples) if s["GT"] == "1/1"),
                    "annotations": [],
                    "tags": [],
                }

            variant = variants[variant_id]

            for annotation in lof_annotations:
                variant["annotations"].append(
                    {
                        "consequence": annotation["Consequence"],
                        "gene_id": annotation["Gene"],
                        "gene_symbol": annotation["SYMBOL"],
                        "transcript_id": annotation["Feature"],
                        "loftee": annotation["LoF"],
                        "loftee_filter": annotation["LoF_filter"],
                        "loftee_flags": annotation["LoF_flags"],
                    }
                )

            if tag_fields:
                for field, label in tag_fields.items():
                    value = row.INFO.get(field, None)
                    if value is not None:
                        variant["tags"].append({"label": label, "value": value})

    with open(output_path, "w") as output_file:
        json.dump(list(variants.values()), output_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("vcf_path")
    parser.add_argument("output_path")
    parser.add_argument("--reference-genome", choices=["GRCh37", "GRCh38"], default="GRCh37")
    parser.add_argument("--tag-field", action="append", default=[])

    args = parser.parse_args()

    tag_fields = {}
    for tag_field in args.tag_field:
        try:
            [field, label] = tag_field.split("=")
        except ValueError:
            field = label = tag_field

        tag_fields[field] = label

    convert_vcf_to_json(
        args.vcf_path,
        args.output_path,
        reference_genome=args.reference_genome,
        tag_fields=tag_fields,
    )


if __name__ == "__main__":
    main()
