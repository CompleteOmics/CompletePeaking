import argparse
from completepeaker_proteomics.core import process_folder

def main():
    p = argparse.ArgumentParser(description="CompletePeaker - Proteomics")
    p.add_argument("--input-folder", "-i", required=True)
    p.add_argument("--output-folder", "-o", required=True)
    p.add_argument("--rt-peptides-file", "-r", required=True)
    p.add_argument("--model-file", "-m", required=True)
    p.add_argument("--verbose", "-v", action="store_true", help="print detailed progress")
    p.add_argument("--limit", type=int, default=0, help="process only N CSVs (0 = all)")
    args = p.parse_args()

    process_folder(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        rt_peptides_file=args.rt_peptides_file,
        model_file=args.model_file,
        verbose=args.verbose,
        limit=args.limit,
    )

if __name__ == "__main__":
    main()
