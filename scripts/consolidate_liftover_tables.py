#!/usr/bin/env python3

import hail as hl
from cpg_utils.hail_batch import init_batch

GNOMAD_V2_EXOME_LIFTOVER = (
    'gs://cpg-common-main/references/liftover/gnomad.exomes.r2.1.1.sites.liftover_grch38.ht'
)
GNOMAD_V2_GENOME_LIFTOVER = (
    'gs://cpg-common-main/references/liftover/gnomad.genomes.r2.1.1.sites.liftover_grch38.ht'
)


def load_liftover_mapping_sites_table(liftover_table_path):
    liftover_table = hl.read_table(liftover_table_path)

    # Remove all fields except the hg38 locus and alleles, and hg37 locus and alleles
    row_fields_to_keep = ['locus', 'alleles', 'original_locus', 'original_alleles']
    row_fields_to_drop = [x for x in list(liftover_table.row.keys()) if x not in row_fields_to_keep]
    global_fields_to_drop = list(liftover_table.globals.keys())

    liftover_table = liftover_table.drop(*global_fields_to_drop)
    liftover_table = liftover_table.drop(*row_fields_to_drop)

    # Re-key the table so that hg37 locus and alleles are the keys
    liftover_table = liftover_table.key_by('original_locus', 'original_alleles')

    return liftover_table


def main():
    init_batch()

    hg37_exome_liftover_table = load_liftover_mapping_sites_table(GNOMAD_V2_EXOME_LIFTOVER)
    hg37_genome_liftover_table = load_liftover_mapping_sites_table(GNOMAD_V2_GENOME_LIFTOVER)

    hg37_exome_liftover_table.write(
        'gs://cpg-common-main/references/liftover/hg37_pruned/gnomad.exomes.r2.1.1.sites.liftover_grch37.ht'
    )
    hg37_genome_liftover_table.write(
        'gs://cpg-common-main/references/liftover/hg37_pruned/gnomad.genomes.r2.1.1.sites.liftover_grch37.ht'
    )


if __name__ == '__main__':
    main()
