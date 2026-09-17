# AI Sign Language Translator (ASL Fingerspelling)

A small, self-contained Python tool that converts English text into **ASL
fingerspelling**: for every letter and digit it shows a short handshape
description plus a stylized ASCII-art "glyph," and lays the whole word or
sentence out as a horizontal, terminal-friendly "signed sentence."

## Scope — please read before filing an issue

This is a **one-directional text → sign reference tool**. It is **not**
camera-based sign language *recognition*. It does not use a camera, does not
run any computer-vision or hand-pose model, and cannot look at a video of a
person signing and tell you what they said. Doing that would require a live
camera feed and a trained hand-pose/gesture-recognition model, neither of
which is available in this environment.

What it *does* do: given text you type, it looks up each character's ASL
fingerspelling handshape in a small bundled dataset (`data/asl_alphabet.json`)
and renders it as text/ASCII output. Think of it as a fingerspelling
cheat-sheet generator, not a translator you could point a webcam at.

## How ASL fingerspelling works (briefly)

American Sign Language has its own grammar and vocabulary distinct from
English, but for proper nouns, acronyms, or words without an established
sign, signers spell the word out letter by letter using the **ASL manual
alphabet**: a fixed handshape for each letter A–Z and digit 0–9, formed with
one hand and typically held in front of the signer's dominant-side shoulder.
Consecutive letters flow into each other with brief transitional movements;
a pause (no dedicated handshape) separates one fingerspelled word from the
next. J and Z are the two "motion" letters — their handshape is traced
through a small movement rather than held static — which this tool notes in
the description text.

This project represents each letter's handshape two ways:

1. **A short text description** of the real handshape (e.g. "Index and
   middle fingers extended and spread, other fingers curled").
2. **An original ASCII glyph** built from a simple 5-finger state model
   (thumb, index, middle, ring, pinky — each drawn as extended `|`, bent
   `n`, curled `.`, splayed `/`, or crossed `x`). This is an original,
   simplified stick-figure abstraction authored for this project — it is
   *not* copied from any photograph, video, or third-party chart.

## Project layout

```
asl-fingerspelling-translator/
├── translate.py              # CLI entry point + translation logic
├── data/
│   └── asl_alphabet.json     # bundled A–Z, 0–9, space & "unknown" glyphs
├── scripts/
│   └── generate_data.py      # one-off generator that produced the JSON above
├── tests/
│   └── test_translate.py     # unit tests (unittest, no extra dependencies)
└── .github/workflows/tests.yml
```

## Requirements

Pure Python standard library — no third-party dependencies. Tested on
Python 3.11 and 3.12.

## Usage

```bash
python translate.py "HELLO WORLD"
```

You can also pipe text in:

```bash
echo "SOS" | python translate.py
```

Non-letter, non-digit characters (punctuation, symbols) are **not** silently
dropped — they're shown as an explicit "unknown / no sign" placeholder so
the output stays honest about what wasn't translated. Input is
case-insensitive; digits 0–9 use their own handshape mapping.

### Example output

```
$ python translate.py "HI"
Input: "HI"

=== Letter-by-letter fingerspelling ===
[H] Index and middle fingers extended sideways together, thumb tucked.
 .   /   /   .   .
 |   |   |   |   |
 \___________/
     |___|

[I] Fist with only the pinky finger extended upward.
 .   .   .   .   |
 |   |   |   |   |
 \___________/
     |___|

=== Signed sentence (horizontal) ===
 .   /   /   .   .   .   .   .   .   |
 |   |   |   |   |   |   |   |   |   |
 \___________/       \___________/
     |___|               |___|
```

## Running the tests

```bash
python -m unittest discover -s tests -v
# or, if pytest is installed:
python -m pytest
```

13 unit tests cover: full A–Z and 0–9 alphabet coverage (non-empty
description + glyph for every entry), the special space/"pause" and
"unknown" glyphs, correct letter sequencing for a simple word, space
handling (including collapsing repeated spaces into one pause),
case-insensitivity, graceful handling of punctuation and empty-string input,
and error-free horizontal rendering for a multi-word sentence.

Continuous integration (`.github/workflows/tests.yml`) runs the same suite
on every push and pull request against Python 3.11 and 3.12.

## Regenerating the data file

`data/asl_alphabet.json` is bundled and ready to use — you don't need to run
anything. If you want to tweak a handshape's finger states or description,
edit `scripts/generate_data.py` and re-run it from the repo root:

```bash
python3 scripts/generate_data.py
```

## License

MIT — see [LICENSE](LICENSE).
