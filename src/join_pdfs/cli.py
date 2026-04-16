"""CLI entry point for join-pdfs."""

import argparse
import sys
from pathlib import Path

from join_pdfs import __version__
from join_pdfs.processor import consolidate_files, group_files_by_organization


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="join-pdfs",
        description="Consolidate PDF files by organization",
    )
    parser.add_argument(
        "-i",
        "--input-folder",
        type=str,
        required=True,
        help="Path to folder containing PDF files",
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        type=str,
        default="consolidated",
        help="Output folder path (default: consolidated)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()
    input_path = Path(args.input_folder)
    output_path = Path(args.output_folder)

    if not input_path.exists():
        print(f"Error: Input folder '{input_path}' does not exist", file=sys.stderr)
        return 1

    if not input_path.is_dir():
        print(f"Error: '{input_path}' is not a directory", file=sys.stderr)
        return 1

    organizations = group_files_by_organization(input_path)

    if not organizations:
        print("No PDF files found in the input folder")
        return 0

    print(f"Found {len(organizations)} organization(s)")

    for org in organizations:
        print(f"  {org.name}: {len(org.all_files)} file(s)")
        output_file = consolidate_files(org, output_path)
        print(f"    Created: {output_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
