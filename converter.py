from __future__ import annotations

ENCODINGS = ("utf-8-sig", "utf-8", "cp1252", "latin-1")
CHARACTER_REPLACEMENTS = str.maketrans({
    "ã": "ă",
    "º": "ș",
    "þ": "ț",
    "ª": "Ș",
})


def _decode_bytes(raw_bytes: bytes) -> str:
    last_error: UnicodeDecodeError | None = None

    for encoding in ENCODINGS:
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError as exc:
            last_error = exc

    raise UnicodeError("Could not decode subtitle content") from last_error


def _normalize_characters(text: str) -> str:
    translated = text.translate(CHARACTER_REPLACEMENTS)
    normalized_chars: list[str] = []

    for index, char in enumerate(translated):
        if char == "Ã":
            next_char = translated[index + 1] if index + 1 < len(translated) else ""
            normalized_chars.append("Ă" if next_char.isupper() else "ă")
            continue
        if char == "Þ":
            next_char = translated[index + 1] if index + 1 < len(translated) else ""
            normalized_chars.append("Ț" if next_char.isupper() else "ț")
            continue
        normalized_chars.append(char)

    return "".join(normalized_chars)


def convert_to_utf8_bom(raw_bytes: bytes) -> bytes:
    return _normalize_characters(_decode_bytes(raw_bytes)).encode("utf-8-sig")
