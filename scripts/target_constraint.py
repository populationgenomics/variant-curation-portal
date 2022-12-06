#!/usr/bin/env python3

'''Joins a list of target gene symbols with the gnomAD v2 gene constraint table.'''

import hail as hl
from cloudpathlib import AnyPath
from cpg_utils.hail_batch import init_batch, dataset_path, output_path

GENE_SYMBOLS = 'targets/v0/target_gene_symbols.txt'
# https://gnomad.broadinstitute.org/downloads#v2-constraint
CONSTRAINT_TABLE = 'gs://gcp-public-data--gnomad/release/2.1.1/constraint/gnomad.v2.1.1.lof_metrics.by_transcript.ht'


def main():
    '''Main entrypoint.'''
    init_batch()

    with AnyPath(dataset_path(GENE_SYMBOLS)).open() as f:
        # Convert to upper case to avoid capitalization mismatches.
        target_symbols = set(s.strip().upper() for s in f.readlines())

    ht = hl.read_table(CONSTRAINT_TABLE)
    ht = ht.filter(hl.set(target_symbols).contains(ht.gene))
    ht = ht.repartition(10)

    # Write to the analysis bucket, so we can easily inspect the results in a notebook.
    joint_table_path = output_path('target_constraint.ht', 'analysis')
    ht.write(joint_table_path)
    print('Finished writing joint table.')

    # Log any unmapped gene symbols.
    ht = hl.read_table(joint_table_path)
    print('Number of rows:', ht.count())
    joint_table_symbols = set(ht.gene.collect())
    unmapped_symbols = target_symbols - joint_table_symbols
    print('Unmapped symbols:', ', '.join(unmapped_symbols))


if __name__ == '__main__':
    main()
