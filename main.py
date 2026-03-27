from __future__ import annotations

import argparse
import sys
from pathlib import Path

from processing import convert_directory


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert top-level .srt files in a folder to UTF-8 with BOM."
    )
    parser.add_argument("input_dir", type=Path, help="Folder containing .srt files")
    parser.add_argument("output_dir", type=Path, help="Folder for converted .srt files")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_dir = args.input_dir
    output_dir = args.output_dir

    try:
        srt_files, results = convert_directory(input_dir, output_dir)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1

    if not srt_files:
        print(f"No .srt files found in {input_dir}", file=sys.stderr)
        return 1

    converted_count = 0
    failed_count = 0

    for result in results:
        if result.error is None:
            converted_count += 1
            print(f"Converted {result.file_name}")
        else:
            failed_count += 1
            print(f"Failed to convert {result.file_name}: {result.error}", file=sys.stderr)

    print(
        f"Found {len(srt_files)} .srt file(s); converted {converted_count}; failed {failed_count}; output {output_dir}"
    )
    return 0 if failed_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
