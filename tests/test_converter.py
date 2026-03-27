from __future__ import annotations

import pytest

import converter
from converter import _decode_bytes, convert_to_utf8_bom


def test_convert_to_utf8_bom_preserves_bytes_when_input_is_already_utf8_with_bom() -> None:
    converted = convert_to_utf8_bom(b"\xef\xbb\xbfSalut")

    assert converted == b"\xef\xbb\xbfSalut"


def test_convert_to_utf8_bom_converts_ansi_encoded_input() -> None:
    converted = convert_to_utf8_bom(b"Caf\xe9")

    assert converted == b"\xef\xbb\xbfCaf\xc3\xa9"


def test_convert_to_utf8_bom_adds_bom_to_utf8_input_without_bom() -> None:
    converted = convert_to_utf8_bom(b"Salut")

    assert converted == b"\xef\xbb\xbfSalut"


def test_decode_bytes_raises_unicode_error_when_no_encoding_can_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(converter, "ENCODINGS", ())

    with pytest.raises(UnicodeError, match="Could not decode subtitle content"):
        _decode_bytes(b"anything")
