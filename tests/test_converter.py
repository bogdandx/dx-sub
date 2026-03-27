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


def test_convert_to_utf8_bom_replaces_configured_characters_after_decoding() -> None:
    converted = convert_to_utf8_bom("ã º þ ª".encode("cp1252"))

    assert converted == b"\xef\xbb\xbf\xc4\x83 \xc8\x99 \xc8\x9b \xc8\x98"


def test_convert_to_utf8_bom_replaces_uppercase_mojibake_variants_based_on_context() -> None:
    converted = convert_to_utf8_bom("DJANGO DEZLÃNÞUIT. Ãsta.".encode("cp1252"))

    assert converted == b"\xef\xbb\xbfDJANGO DEZL\xc4\x82N\xc8\x9aUIT. \xc4\x83sta."


def test_convert_to_utf8_bom_preserves_unrelated_characters_while_replacing_targeted_ones() -> None:
    converted = convert_to_utf8_bom("Cãldurº ºi soare".encode("cp1252"))

    assert converted == b"\xef\xbb\xbfC\xc4\x83ldur\xc8\x99 \xc8\x99i soare"


def test_decode_bytes_raises_unicode_error_when_no_encoding_can_decode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(converter, "ENCODINGS", ())

    with pytest.raises(UnicodeError, match="Could not decode subtitle content"):
        _decode_bytes(b"anything")
