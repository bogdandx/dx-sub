from __future__ import annotations

from pathlib import Path

import main as app_main
import processing


def test_main_returns_zero_and_prints_summary_on_success(tmp_path: Path, capsys) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "sample.srt").write_bytes(b"Salut")

    exit_code = app_main.main([str(input_dir), str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "Converted sample.srt" in captured.out
    assert "converted 1; failed 0" in captured.out
    assert captured.err == ""


def test_main_returns_one_when_directory_validation_fails(capsys) -> None:
    exit_code = app_main.main(["missing-input", "output"])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Input directory does not exist" in captured.err


def test_main_returns_one_when_no_srt_files_are_found(tmp_path: Path, capsys) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    exit_code = app_main.main([str(input_dir), str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert f"No .srt files found in {input_dir}" in captured.err


def test_main_returns_one_and_reports_failed_files(tmp_path: Path, monkeypatch, capsys) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    (input_dir / "sample.srt").write_bytes(b"broken")

    def fake_convert_file(source_path: Path, destination_dir: Path) -> processing.FileResult:
        return processing.FileResult(file_name=source_path.name, error="boom")

    monkeypatch.setattr(processing, "convert_file", fake_convert_file)

    exit_code = app_main.main([str(input_dir), str(output_dir)])
    captured = capsys.readouterr()

    assert exit_code == 1
    assert "Failed to convert sample.srt: boom" in captured.err
    assert "converted 0; failed 1" in captured.out
