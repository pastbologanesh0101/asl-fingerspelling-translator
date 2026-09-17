#!/usr/bin/env python3
"""
AI Sign Language Translator — text to ASL fingerspelling (reference tool).

This is a ONE-DIRECTIONAL text -> sign reference translator. It does NOT do
camera-based sign language recognition (that would require a live camera
feed and a trained hand-pose/gesture recognition model, which are not
available in this environment). Given a piece of English text, it looks up
each letter/digit's ASL fingerspelling handshape in data/asl_alphabet.json
and prints:

  1. A letter-by-letter sequence: for each character, its short handshape
     description plus a small ASCII-art glyph.
  2. A single horizontal "signed sentence" rendering, where every letter's
     glyph is laid out side by side, terminal-friendly.

Usage:
    python translate.py "HELLO WORLD"
    python translate.py "hi there, 123!"
    echo "SOS" | python translate.py
"""
from __future__ import annotations

import json
import os
import sys
from typing import Iterable, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "asl_alphabet.json")

SPACE_TOKEN = " "  # internal marker for a pause/space glyph
UNKNOWN_TOKEN = "?"  # internal marker for an unmapped character


def load_alphabet(path: str = DATA_PATH) -> dict:
    """Load the bundled ASL fingerspelling data file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _entry_for_char(ch: str, alphabet: dict) -> Optional[dict]:
    """Return the data entry for a single (already-validated) character, or None."""
    if ch.isalpha() and ch.upper() in alphabet["letters"]:
        return alphabet["letters"][ch.upper()]
    if ch.isdigit() and ch in alphabet["digits"]:
        return alphabet["digits"][ch]
    return None


def tokenize(text: str) -> list[str]:
    """
    Break input text into translation tokens:
      - letters are uppercased
      - digits are kept as-is
      - runs of whitespace collapse to a single space token
      - other characters (punctuation/symbols) are kept as single tokens
        so the translator can flag them as unmapped rather than crashing
    """
    tokens: list[str] = []
    for ch in text:
        if ch.isspace():
            if not tokens or tokens[-1] != SPACE_TOKEN:
                tokens.append(SPACE_TOKEN)
        else:
            tokens.append(ch)
    return tokens


def translate_to_sequence(text: str, alphabet: Optional[dict] = None) -> list[dict]:
    """
    Convert text into an ordered list of sign entries.

    Each item is a dict: {"char": <original char>, "kind": "letter"|"digit"|
    "space"|"unknown", "description": str, "glyph": str}
    """
    if alphabet is None:
        alphabet = load_alphabet()

    sequence: list[dict] = []
    for token in tokenize(text):
        if token == SPACE_TOKEN:
            special = alphabet["special"]["space"]
            sequence.append({
                "char": " ",
                "kind": "space",
                "description": special["description"],
                "glyph": special["glyph"],
            })
            continue

        entry = _entry_for_char(token, alphabet)
        if entry is None:
            special = alphabet["special"]["unknown"]
            sequence.append({
                "char": token,
                "kind": "unknown",
                "description": f"'{token}' has no fingerspelling sign — {special['description']}",
                "glyph": special["glyph"],
            })
            continue

        kind = "letter" if token.isalpha() else "digit"
        sequence.append({
            "char": token.upper() if kind == "letter" else token,
            "kind": kind,
            "description": entry["description"],
            "glyph": entry["glyph"],
        })

    return sequence


def render_horizontal(sequence: Iterable[dict]) -> str:
    """
    Lay every glyph in the sequence out side by side as one multi-line
    ASCII block — a terminal-friendly "signed sentence" view.
    """
    sequence = list(sequence)
    if not sequence:
        return ""

    glyph_lines = [item["glyph"].split("\n") for item in sequence]
    height = max(len(lines) for lines in glyph_lines)

    # Pad every glyph to the same number of lines and the same width.
    padded: list[list[str]] = []
    for lines in glyph_lines:
        width = max((len(line) for line in lines), default=0)
        lines = lines + [""] * (height - len(lines))
        lines = [line.ljust(width) for line in lines]
        padded.append(lines)

    rows = []
    for row_idx in range(height):
        rows.append(" ".join(glyphs[row_idx] for glyphs in padded))
    return "\n".join(rows)


def format_letter_by_letter(sequence: Iterable[dict]) -> str:
    """Human-readable letter-by-letter breakdown: description + glyph per item."""
    lines = []
    for item in sequence:
        label = {
            "letter": item["char"],
            "digit": item["char"],
            "space": "(space)",
            "unknown": item["char"],
        }[item["kind"]]
        lines.append(f"[{label}] {item['description']}")
        lines.append(item["glyph"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def translate(text: str) -> str:
    """Full CLI-facing translation: letter-by-letter view + horizontal view."""
    alphabet = load_alphabet()
    sequence = translate_to_sequence(text, alphabet)

    out = []
    out.append(f'Input: "{text}"')
    out.append("")
    out.append("=== Letter-by-letter fingerspelling ===")
    out.append(format_letter_by_letter(sequence))
    out.append("=== Signed sentence (horizontal) ===")
    out.append(render_horizontal(sequence))
    out.append("")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        text = " ".join(argv[1:])
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        print('Usage: python translate.py "TEXT TO SIGN"', file=sys.stderr)
        return 1

    print(translate(text))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
