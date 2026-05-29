from __future__ import annotations

import argparse

from .io import read_leads, write_leads
from .service import LeadFilter, filter_leads, rank_leads


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Filter and rank leads from CSV data.")
    parser.add_argument("--input", required=True, help="Path to input CSV file")
    parser.add_argument("--output", required=True, help="Path to output CSV file")
    parser.add_argument("--industry", help="Filter by industry")
    parser.add_argument("--country", help="Filter by country code, e.g. US")
    parser.add_argument("--min-employees", type=int, help="Minimum employee count")
    parser.add_argument("--max-employees", type=int, help="Maximum employee count")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    leads = read_leads(args.input)
    filters = LeadFilter(
        industry=args.industry,
        country=args.country,
        min_employees=args.min_employees,
        max_employees=args.max_employees,
    )
    filtered = filter_leads(leads, filters)
    ranked = rank_leads(filtered)
    write_leads(args.output, ranked)


if __name__ == "__main__":
    main()
