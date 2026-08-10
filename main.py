"""
CLI entrypoint.

Usage:
    python main.py --generate-data     # (re)generate synthetic input datasets
    python main.py --run               # run the full QA pipeline
    python main.py --generate-data --run
"""

from __future__ import annotations

import argparse
import sys

from src.data_generator import main as generate_data
from src.pipeline import run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(description="Navigation & Places SOP Compliance QA Framework")
    parser.add_argument("--generate-data", action="store_true", help="Regenerate synthetic input datasets")
    parser.add_argument("--run", action="store_true", help="Run the QA pipeline")
    args = parser.parse_args()

    if not args.generate_data and not args.run:
        parser.print_help()
        sys.exit(0)

    if args.generate_data:
        print("Generating synthetic datasets...")
        generate_data()

    if args.run:
        print("Running QA pipeline...")
        result = run_pipeline()
        print(f"\nRecords scanned:     {result['total_records']:,}")
        print(f"Defects flagged:     {len(result['flags']):,}")
        print(f"Processing time:     {result['processing_seconds']:.2f}s")
        print(f"Structured log:      {result['log_path']}")
        print(f"Weekly report:       {result['report_path']}")


if __name__ == "__main__":
    main()
