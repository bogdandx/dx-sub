from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from converter import convert_to_utf8_bom


@dataclass(frozen=True)
class FileResult:
    file_name: str
    error: str | None


def validate_directories(input_dir: Path, output_dir: Path) -> None:
    if not input_dir.exists():
        raise ValueError(f"Input directory does not exist: {input_dir}")
    if not input_dir.is_dir():
        raise ValueError(f"Input path is not a directory: {input_dir}")
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")


def discover_srt_files(input_dir: Path) -> list[Path]:
    return sorted(path for path in input_dir.iterdir() if path.is_file() and path.suffix.lower() == ".srt")


def convert_file(source_path: Path, output_dir: Path) -> FileResult:
    try:
        raw_bytes = source_path.read_bytes()
        destination_path = output_dir / source_path.name
        destination_path.write_bytes(convert_to_utf8_bom(raw_bytes))
    except (OSError, UnicodeError) as exc:
        return FileResult(file_name=source_path.name, error=str(exc))

    return FileResult(file_name=source_path.name, error=None)


def convert_directory(input_dir: Path, output_dir: Path) -> tuple[list[Path], list[FileResult]]:
    validate_directories(input_dir, output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    srt_files = discover_srt_files(input_dir)
    results = [convert_file(source_path, output_dir) for source_path in srt_files]
    return srt_files, results
