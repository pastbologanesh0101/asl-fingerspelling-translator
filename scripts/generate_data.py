"""
One-off generator for data/asl_alphabet.json.

Not part of the shipped CLI — this script is run once (by the project author)
to produce the bundled data file from a compact finger-state model, so that
all 36 ASCII glyphs stay visually consistent with each other. It is kept in
the repo for transparency/reproducibility but `translate.py` only reads the
generated JSON at runtime.

Run from the repo root: `python3 scripts/generate_data.py`

Finger-state model
-------------------
Each handshape is described as five finger states, ordered
Thumb, Index, Middle, Ring, Pinky:

    up    -> finger extended straight     -> '|'
    hook  -> finger bent at the middle    -> 'n'
    curl  -> finger curled into the palm  -> '.'
    out   -> finger extended sideways     -> '/'
    cross -> finger crosses a neighbor    -> 'x'

These are an original, simplified stick-figure abstraction of a hand and are
not derived from any photograph, video, or third-party artwork.
"""
import json

SYMBOLS = {
    "up": "|",
    "hook": "n",
    "curl": ".",
    "out": "/",
    "cross": "x",
    "side": "-",
}

# (thumb, index, middle, ring, pinky) states + short handshape description.
LETTERS = {
    "A": (("curl", "curl", "curl", "curl", "curl"),
          "Fist with the thumb resting alongside the fist, not tucked inside."),
    "B": (("curl", "up", "up", "up", "up"),
          "Flat hand, four fingers together pointing up, thumb folded across the palm."),
    "C": (("out", "hook", "hook", "hook", "hook"),
          "Fingers and thumb curved together to form the shape of the letter C."),
    "D": (("curl", "up", "curl", "curl", "curl"),
          "Index finger points up, other fingers curl to touch the thumb."),
    "E": (("curl", "curl", "curl", "curl", "curl"),
          "Fingertips curled down to touch the thumb, hand held in a tight claw."),
    "F": (("hook", "hook", "up", "up", "up"),
          "Thumb and index finger touch to form a circle, other three fingers extended up."),
    "G": (("out", "out", "curl", "curl", "curl"),
          "Index finger and thumb point sideways, parallel to each other, like a gun shape."),
    "H": (("curl", "out", "out", "curl", "curl"),
          "Index and middle fingers extended sideways together, thumb tucked."),
    "I": (("curl", "curl", "curl", "curl", "up"),
          "Fist with only the pinky finger extended upward."),
    "J": (("curl", "curl", "curl", "curl", "up"),
          "Like I, pinky extended, then traced in the air drawing the letter J (motion sign)."),
    "K": (("out", "up", "out", "curl", "curl"),
          "Index and middle fingers extended in a V, thumb placed between them."),
    "L": (("out", "up", "curl", "curl", "curl"),
          "Thumb and index finger extended to form a right angle (an L shape)."),
    "M": (("curl", "hook", "hook", "hook", "curl"),
          "Thumb tucked under three folded fingers (index, middle, ring)."),
    "N": (("curl", "hook", "hook", "curl", "curl"),
          "Thumb tucked under two folded fingers (index, middle)."),
    "O": (("out", "hook", "hook", "hook", "hook"),
          "All fingers and thumb curved to meet at the tips, forming a round O shape."),
    "P": (("out", "up", "out", "curl", "curl"),
          "Like K, but the hand is pointed downward instead of up."),
    "Q": (("out", "out", "curl", "curl", "curl"),
          "Like G, but the hand is pointed downward instead of up."),
    "R": (("curl", "cross", "up", "curl", "curl"),
          "Index and middle fingers crossed, thumb holding the ring/pinky down."),
    "S": (("cross", "curl", "curl", "curl", "curl"),
          "Closed fist with the thumb crossed in front over the fingers."),
    "T": (("hook", "hook", "curl", "curl", "curl"),
          "Fist with the thumb tucked between the index and middle fingers."),
    "U": (("curl", "up", "up", "curl", "curl"),
          "Index and middle fingers extended straight up together, side by side."),
    "V": (("curl", "up", "up", "curl", "curl"),
          "Index and middle fingers extended up and spread apart, forming a V."),
    "W": (("curl", "up", "up", "up", "curl"),
          "Index, middle, and ring fingers extended up and spread apart."),
    "X": (("curl", "hook", "curl", "curl", "curl"),
          "Index finger bent into a hook shape, other fingers curled, thumb resting alongside."),
    "Y": (("out", "curl", "curl", "curl", "up"),
          "Thumb and pinky extended outward, other fingers curled (a 'hang loose' shape)."),
    "Z": (("curl", "up", "curl", "curl", "curl"),
          "Index finger traces the letter Z in the air (motion sign)."),
}

DIGITS = {
    "0": (("out", "hook", "hook", "hook", "hook"),
          "Fingers and thumb curved together forming a round zero, like the letter O."),
    "1": (("curl", "up", "curl", "curl", "curl"),
          "Fist with only the index finger extended straight up."),
    "2": (("curl", "up", "up", "curl", "curl"),
          "Index and middle fingers extended up together, like the letter U."),
    "3": (("out", "up", "up", "curl", "curl"),
          "Thumb, index, and middle fingers extended up, other fingers curled."),
    "4": (("curl", "up", "up", "up", "up"),
          "Four fingers extended straight up together, thumb folded across the palm."),
    "5": (("out", "up", "up", "up", "up"),
          "All five fingers spread open and extended."),
    "6": (("out", "curl", "curl", "curl", "up"),
          "Thumb touches the pinky tip, other three fingers extended up."),
    "7": (("out", "curl", "curl", "up", "curl"),
          "Thumb touches the ring finger tip, other fingers extended."),
    "8": (("out", "curl", "up", "curl", "curl"),
          "Thumb touches the middle finger tip, other fingers extended."),
    "9": (("out", "up", "curl", "curl", "curl"),
          "Thumb touches the index finger tip, other fingers extended."),
}


def render_glyph(states):
    t, i, m, r, p = (SYMBOLS[s] for s in states)
    top = f" {t}   {i}   {m}   {r}   {p} "
    mid = f" |   |   |   |   | "
    base = " \\___________/ "
    wrist = "     |___|     "
    return "\n".join([top, mid, base, wrist])


def build_entry(states, description):
    t, i, m, r, p = states
    return {
        "description": description,
        "fingers": {
            "thumb": t,
            "index": i,
            "middle": m,
            "ring": r,
            "pinky": p,
        },
        "glyph": render_glyph(states),
    }


def main():
    data = {"letters": {}, "digits": {}}
    for letter, (states, desc) in LETTERS.items():
        data["letters"][letter] = build_entry(states, desc)
    for digit, (states, desc) in DIGITS.items():
        data["digits"][digit] = build_entry(states, desc)

    data["special"] = {
        "space": {
            "description": "A pause between signed words.",
            "glyph": "\n".join([
                "   . . .   ",
                "  (pause)  ",
                "  -------  ",
                "           ",
            ]),
        },
        "unknown": {
            "description": "Character has no fingerspelling sign (punctuation/symbol); shown as a placeholder.",
            "glyph": "\n".join([
                "     ?     ",
                "    ???    ",
                "  -------  ",
                "           ",
            ]),
        },
    }

    import os

    out_path = os.path.join(os.path.dirname(__file__), "..", "data", "asl_alphabet.json")
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=False)
        f.write("\n")

    print(f"Wrote {len(data['letters'])} letters, {len(data['digits'])} digits.")


if __name__ == "__main__":
    main()
