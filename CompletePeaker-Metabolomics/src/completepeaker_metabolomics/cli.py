import csv
import argparse

from completepeaker_metabolomics.core import (
    read_data,
    preprocess_data,
    detect_peak,
    find_peak_limits_combined,
)


def main():
    p = argparse.ArgumentParser(
        description="CompletePeaker - Metabolomics: step-by-step peak boundary finder"
    )
    p.add_argument("-i", "--input", required=True, help="Path to input CSV")
    p.add_argument("-o", "--output", required=True, help="Path to output CSV")
    p.add_argument("--rt-half-window", type=float, default=1.0, help="Half-window around explicit RT (default: 1.0)")
    p.add_argument("--fraction-of-apex", type=float, default=0.05, help="Boundary threshold fraction (default: 0.05)")
    p.add_argument("--max-extension", type=int, default=50, help="Max points for extension (default: 50)")
    p.add_argument("--debug", action="store_true", help="Print extra calculations")
    p.add_argument("--verbose", action="store_true", help="Print descriptive step-by-step logs")
    args = p.parse_args()

    print(f"🚀 Starting CompletePeaker - Metabolomics")
    datasets = read_data(args.input, verbose=args.verbose)
    print(f"🧮 Total rows to process: {len(datasets)}")

    results = []
    for i, (times, intensities, molecule, explicit_rt, file_name) in enumerate(datasets, 1):
        print(f"\n——— [{i}/{len(datasets)}] Processing sample — File='{file_name}' | Molecule='{molecule}' ———")

        try:
            # 1) Smooth
            sm = preprocess_data(intensities, verbose=args.verbose)

            # 2) Find apex near explicit RT
            apex_time, apex_int, apex_idx = detect_peak(
                times,
                sm,
                explicit_rt,
                rt_half_window=args.rt_half_window,
                verbose=args.verbose,
            )

            # 3) Boundaries
            start_t, end_t = find_peak_limits_combined(
                times,
                sm,
                apex_idx,
                fraction_of_apex=args.fraction_of_apex,
                max_extension=args.max_extension,
                debug=args.debug,
                verbose=args.verbose,
            )

            print(
                f"   🏁 Result for '{molecule}' in '{file_name}': "
                f"Start={start_t:.4f}, Apex={apex_time:.4f}, End={end_t:.4f}"
            )
            results.append((file_name, molecule, start_t, end_t))

        except Exception as e:
            print(f"   ❌ Skipped Molecule='{molecule}' (File='{file_name}') — {e}")

    # Write CSV
    print(f"\n💾 Writing results to: {args.output}")
    with open(args.output, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["FileName", "Molecule", "MinStartTime", "MaxEndTime"])
        for fn, mol, st, et in results:
            w.writerow([fn, mol, f"{st:.4f}", f"{et:.4f}"])

    print(f"✅ Done. Wrote {len(results)} row(s).")


if __name__ == "__main__":
    main()
