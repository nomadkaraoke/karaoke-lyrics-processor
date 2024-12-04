import unittest
from karaoke_lyrics_processor.karaoke_lyrics_processor import KaraokeLyricsProcessor


class TestKaraokeLyricsProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = KaraokeLyricsProcessor(max_line_length=36, input_lyrics_text="")

    def test_simple_processing(self):
        input_lyrics = "This is a simple test line that should be split into two lines."
        expected_output = "This is a simple test line\nthat should be split into two lines."

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_non_printable_spaces(self):
        input_lyrics = "This is a test line with\u2005non-printable spaces."
        expected_output = "This is a test\nline with non-printable spaces."

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_long_line_with_commas(self):
        input_lyrics = "This line, which is quite long, should be split at a comma."
        expected_output = "This line, which is quite long,\nshould be split at a comma."

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_long_line_with_and(self):
        input_lyrics = "This line is long and should be split at 'and'."
        expected_output = "This line is long and\nshould be split at 'and'."

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_line_with_parentheses(self):
        input_lyrics = "This line (with parentheses) should be split correctly."
        expected_output = "This line\n(with parentheses)\nshould be split correctly."

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_multiple_lines(self):
        input_lyrics = "First line.\nSecond line with\u2005non-printable space."
        expected_output = "First line.\nSecond line\nwith non-printable space."

        self.processor.input_lyrics_lines = input_lyrics.splitlines()
        result = self.processor.process()

        self.assertEqual(result, expected_output)

    def test_commas_inside_quotes(self):
        input_lyrics = 'Mama told me, "Don\'t be shy," Seno said "Let\'s get this," watch how fast I switch this'
        expected_output = 'Mama told me, "Don\'t be shy",\nSeno said "Let\'s get this",\nwatch how fast I switch this'

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result.strip(), expected_output.strip())

    def test_commas_inside_quotes_with_multiple_quotes(self):
        input_lyrics = '"Hello," she said, "how are you," and smiled.'
        expected_output = '"Hello",\nshe said, "how are you", and smiled.'

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result.strip(), expected_output.strip())

    def test_commas_inside_quotes_with_no_commas(self):
        input_lyrics = 'He said "Hello there" and waved.'
        expected_output = 'He said "Hello there" and waved.'

        self.processor.input_lyrics_lines = [input_lyrics]
        result = self.processor.process()

        self.assertEqual(result.strip(), expected_output.strip())


if __name__ == "__main__":
    unittest.main()
