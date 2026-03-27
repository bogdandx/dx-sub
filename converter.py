from __future__ import annotations

ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")


def _decode_bytes(raw_bytes: bytes) -> str:
    last_error: UnicodeDecodeError | None = None

    for encoding in ENCODINGS:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeError("Could not decode subtitle content") from last_error


def convert_to_utf8_bom(raw_bytes: bytes) -> bytes:
    return _decode_bytes(raw_bytes).encode("utf-8-sig")
