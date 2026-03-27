from __future__ import annotations

from pathlib import Path

import pytest

import processing
from processing import convert_directory, convert_file, discover_srt_files, validate_directories


def test_validate_directories_rejects_missing_input_directory(tmp_path: Path) -> None:
    missing_input_dir = tmp_path / "missing"
    output_dir = tmp_path / "output"

    with pytest.raises(ValueError, match="Input directory does not exist"):
        validate_directories(missing_input_dir, output_dir)


def test_validate_directories_rejects_input_path_that_is_not_a_directory(tmp_path: Path) -> None:
    input_file = tmp_path / "input.srt"
    output_dir = tmp_path / "output"
    input_file.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="Input path is not a directory"):
        validate_directories(input_file, output_dir)


def test_validate_directories_rejects_output_path_that_is_not_a_directory(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_file = tmp_path / "output.srt"
    input_dir.mkdir()
    output_file.write_text("x", encoding="utf-8")

    with pytest.raises(ValueError, match="Output path is not a directory"):
        validate_directories(input_dir, output_file)


def test_discover_srt_files_returns_only_top_level_srt_files(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "a.srt").write_text("one", encoding="utf-8")
    (input_dir / "b.SRT").write_text("two", encoding="utf-8")
    (input_dir / "ignore.txt").write_text("three", encoding="utf-8")
    nested_dir = input_dir / "nested"
    nested_dir.mkdir()
    (nested_dir / "nested.srt").write_text("four", encoding="utf-8")

    discovered = discover_srt_files(input_dir)

    assert discovered == [input_dir / "a.srt", input_dir / "b.SRT"]


def test_convert_file_writes_converted_output_file(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    source_path = input_dir / "sample.srt"
    source_path.write_bytes(b"Caf\xe9")

    result = convert_file(source_path, output_dir)

    assert result == type(result)(file_name="sample.srt", error=None)
    assert (output_dir / "sample.srt").read_bytes() == b"\xef\xbb\xbfCaf\xc3\xa9"


def test_convert_file_returns_error_when_conversion_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    source_path = input_dir / "sample.srt"
    source_path.write_bytes(b"broken")

    def fake_convert_to_utf8_bom(_: bytes) -> bytes:
        raise UnicodeError("boom")

    monkeypatch.setattr(processing, "convert_to_utf8_bom", fake_convert_to_utf8_bom)

    result = convert_file(source_path, output_dir)

    assert result == type(result)(file_name="sample.srt", error="boom")


def test_convert_directory_creates_output_directory_and_returns_results(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "sample.srt").write_bytes(b"Salut")

    srt_files, results = convert_directory(input_dir, output_dir)

    assert srt_files == [input_dir / "sample.srt"]
    assert results == [type(results[0])(file_name="sample.srt", error=None)]
    assert output_dir.exists()
    assert (output_dir / "sample.srt").read_bytes() == b"\xef\xbb\xbfSalut"


def test_convert_directory_continues_processing_after_one_file_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    failing_file = input_dir / "a.srt"
    succeeding_file = input_dir / "b.srt"
    failing_file.write_bytes(b"broken")
    succeeding_file.write_bytes(b"Salut")

    original_convert_file = processing.convert_file

    def fake_convert_file(source_path: Path, destination_dir: Path) -> processing.FileResult:
        if source_path.name == "a.srt":
            return processing.FileResult(file_name=source_path.name, error="boom")
        return original_convert_file(source_path, destination_dir)

    monkeypatch.setattr(processing, "convert_file", fake_convert_file)

    srt_files, results = convert_directory(input_dir, output_dir)

    assert srt_files == [failing_file, succeeding_file]
    assert results == [
        processing.FileResult(file_name="a.srt", error="boom"),
        processing.FileResult(file_name="b.srt", error=None),
    ]
    assert not (output_dir / "a.srt").exists()
    assert (output_dir / "b.srt").read_bytes() == b"\xef\xbb\xbfSalut"
