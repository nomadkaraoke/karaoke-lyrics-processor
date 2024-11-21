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


if __name__ == "__main__":
    unittest.main()
