import hail as hl
from cpg_utils.hail_batch import init_batch, output_path

def main():

    parser = argparse.ArgumentParser(description="Subset a hail table to N random variants and write to JSON.")
    parser.add_argument(
        "--hail-table",
        type=str,
        help="Hail variants table to sample from.",
    )
    parser.add_argument(
        "--n-variants",
        type=int,
        default=10,
        help="Number of variants to sample.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1,
        help="Seed for the random sampler.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Relative dataset path (analysis category) for sampled variants file.",
    )

    init_batch()

    # Read in the hail table.
    variants = hl.read_table(args.hail_table)

    # Convert to a list of JSON structs.
    rows = variants.annotate(json=hl.json(variants.row_value)).key_by().select("json").collect()

    # Set the random sampler seed, and extract the requested number of variants.
    random.seed(args.seed)
    random.sample(rows, args.n_variants)
    
    # Write the output to a JSON file.
    with open_file(output_path(args.output, "analysis"), "w") as f:
        f.write("[" + ",".join([row.json for row in rows]) + "]")


if __name__ == '__main__':
    main()