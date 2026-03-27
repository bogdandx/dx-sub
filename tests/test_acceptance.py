from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
INPUT_DIR = REPO_ROOT / "tests" / "input"
EXPECTED_DIR = REPO_ROOT / "tests" / "expected"
BOM = b"\xef\xbb\xbf"


def first_difference(actual: bytes, expected: bytes) -> str:
    for index, (actual_byte, expected_byte) in enumerate(zip(actual, expected)):
        if actual_byte != expected_byte:
            start = max(0, index - 12)
            end = index + 12
            return (
                f"first difference at byte {index}: "
                f"actual=0x{actual_byte:02x}, expected=0x{expected_byte:02x}; "
                f"actual[{start}:{end}]={actual[start:end]!r}; "
                f"expected[{start}:{end}]={expected[start:end]!r}"
            )

    if len(actual) != len(expected):
        return f"byte lengths differ: actual={len(actual)}, expected={len(expected)}"

    return "files are identical"


def test_acceptance_converts_fixture_directory(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"

    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "main.py"), str(INPUT_DIR), str(output_dir)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

    output_file = output_dir / "Django.Unchained.2012.1080p.BluRay.x264-SPARKS.srt"
    expected_file = EXPECTED_DIR / "Django.Unchained.2012.1080p.BluRay.x264-SPARKS-utf8.srt"

    assert output_file.exists()

    actual_bytes = output_file.read_bytes()
    expected_bytes = expected_file.read_bytes()

    has_bom = actual_bytes.startswith(BOM)
    assert has_bom, (
        "Output file is missing the UTF-8 BOM. "
        f"First 8 bytes were {actual_bytes[:8]!r}."
    )

    matches_expected = actual_bytes == expected_bytes
    assert matches_expected, (
        "Converted file does not match the expected fixture: "
        + first_difference(actual_bytes, expected_bytes)
    )
