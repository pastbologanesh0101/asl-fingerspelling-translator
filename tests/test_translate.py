"""
Unit tests for the AI Sign Language Translator (text -> ASL fingerspelling).

Run with:  python -m pytest
       or:  python -m unittest discover
"""
import string
import unittest

import translate


class TestAlphabetData(unittest.TestCase):
    """Checks on the bundled data/asl_alphabet.json contents."""

    @classmethod
    def setUpClass(cls):
        cls.alphabet = translate.load_alphabet()

    def test_all_26_letters_present_with_content(self):
        letters = self.alphabet["letters"]
        for letter in string.ascii_uppercase:
            self.assertIn(letter, letters, f"missing letter {letter}")
            entry = letters[letter]
            self.assertTrue(entry["description"].strip(), f"{letter} has empty description")
            self.assertTrue(entry["glyph"].strip(), f"{letter} has empty glyph")

    def test_all_10_digits_present_with_content(self):
        digits = self.alphabet["digits"]
        for digit in "0123456789":
            self.assertIn(digit, digits, f"missing digit {digit}")
            entry = digits[digit]
            self.assertTrue(entry["description"].strip(), f"{digit} has empty description")
            self.assertTrue(entry["glyph"].strip(), f"{digit} has empty glyph")

    def test_special_glyphs_present(self):
        self.assertIn("space", self.alphabet["special"])
        self.assertIn("unknown", self.alphabet["special"])
        self.assertTrue(self.alphabet["special"]["space"]["glyph"].strip())
        self.assertTrue(self.alphabet["special"]["unknown"]["glyph"].strip())


class TestTranslation(unittest.TestCase):
    """Checks on the text -> sign sequence translation logic."""

    def test_simple_word_produces_correct_letter_sequence(self):
        sequence = translate.translate_to_sequence("CAB")
        chars = [item["char"] for item in sequence]
        kinds = [item["kind"] for item in sequence]
        self.assertEqual(chars, ["C", "A", "B"])
        self.assertEqual(kinds, ["letter", "letter", "letter"])

    def test_spaces_produce_pause_glyph(self):
        sequence = translate.translate_to_sequence("A B")
        kinds = [item["kind"] for item in sequence]
        self.assertEqual(kinds, ["letter", "space", "letter"])
        alphabet = translate.load_alphabet()
        expected_pause_glyph = alphabet["special"]["space"]["glyph"]
        space_item = sequence[1]
        self.assertEqual(space_item["glyph"], expected_pause_glyph)

    def test_case_insensitivity(self):
        lower_seq = translate.translate_to_sequence("hello")
        upper_seq = translate.translate_to_sequence("HELLO")
        lower_chars = [item["char"] for item in lower_seq]
        upper_chars = [item["char"] for item in upper_seq]
        self.assertEqual(lower_chars, upper_chars)
        self.assertEqual(lower_chars, ["H", "E", "L", "L", "O"])

    def test_digits_are_translated(self):
        sequence = translate.translate_to_sequence("101")
        chars = [item["char"] for item in sequence]
        kinds = [item["kind"] for item in sequence]
        self.assertEqual(chars, ["1", "0", "1"])
        self.assertEqual(kinds, ["digit", "digit", "digit"])

    def test_non_alphanumeric_characters_handled_gracefully(self):
        # Should not raise, and punctuation should be flagged as "unknown"
        # rather than silently pretending it has a sign.
        sequence = translate.translate_to_sequence("HI!")
        kinds = [item["kind"] for item in sequence]
        self.assertEqual(kinds, ["letter", "letter", "unknown"])
        self.assertEqual(sequence[-1]["char"], "!")
        self.assertTrue(sequence[-1]["description"])

    def test_empty_string_input_handled(self):
        sequence = translate.translate_to_sequence("")
        self.assertEqual(sequence, [])
        # Full translate() pipeline should also not raise on empty input.
        result = translate.translate("")
        self.assertIn("Input:", result)

    def test_multiple_consecutive_spaces_collapse_to_one_pause(self):
        sequence = translate.translate_to_sequence("A   B")
        kinds = [item["kind"] for item in sequence]
        self.assertEqual(kinds, ["letter", "space", "letter"])


class TestHorizontalRendering(unittest.TestCase):
    """Checks on the side-by-side 'signed sentence' rendering."""

    def test_horizontal_rendering_combines_glyphs_for_multi_word_sentence(self):
        sequence = translate.translate_to_sequence("HI THERE")
        rendered = translate.render_horizontal(sequence)
        self.assertIsInstance(rendered, str)
        self.assertGreater(len(rendered), 0)
        # One rendered line per glyph line, all letters laid out side by side.
        lines = rendered.split("\n")
        self.assertGreater(len(lines), 1)
        # Every rendered row should be at least as wide as a single glyph's width,
        # since multiple glyphs are placed side by side.
        self.assertGreater(len(lines[0]), 5)

    def test_horizontal_rendering_empty_sequence_returns_empty_string(self):
        self.assertEqual(translate.render_horizontal([]), "")

    def test_full_translate_pipeline_runs_end_to_end(self):
        result = translate.translate("HELLO WORLD")
        self.assertIn("Letter-by-letter", result)
        self.assertIn("Signed sentence", result)
        self.assertIn("[H]", result)
        self.assertIn("[W]", result)


if __name__ == "__main__":
    unittest.main()
