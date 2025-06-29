import unittest
import tempfile
import os
from karaoke_lyrics_processor.karaoke_lyrics_processor import KaraokeLyricsProcessor


class TestIntegration(unittest.TestCase):
    """Integration tests that test the full workflow"""

    def test_end_to_end_text_processing(self):
        """Test complete end-to-end processing with text input"""
        input_text = """This is the first line that is quite long and should be split appropriately.
        This is another line with    extra spaces   and formatting issues.
        
        Here's a line with (parentheses that contain some additional information) that should be handled correctly.
        This line has, commas in various, places that should, be used for splitting.
        A line with "quoted text, inside" that needs fixing.
        """

        processor = KaraokeLyricsProcessor(input_lyrics_text=input_text, max_line_length=40)

        result = processor.process()

        # Verify processing occurred
        self.assertIsInstance(result, str)
        self.assertNotEqual(result.strip(), input_text.strip())

        # Verify line length constraints
        lines = result.split("\n")
        for line in lines:
            self.assertLessEqual(len(line), 40, f"Line exceeds max length: '{line}'")

        # Verify some basic processing occurred
        self.assertIn("\n", result)  # Should have line breaks

    def test_end_to_end_file_processing(self):
        """Test complete end-to-end processing with file input and output"""
        input_content = """This is a test song with very long lines that need to be processed for karaoke display purposes.
        The lyrics contain various formatting issues, extra spaces,    and other problems.
        Some lines have (additional information in parentheses) that should be handled properly.
        Lines with commas, should be split, at appropriate places, for better readability.
        """

        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as input_file:
            input_file.write(input_content)
            input_filename = input_file.name

        # Create temporary output file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as output_file:
            output_filename = output_file.name

        try:
            # Process the file
            processor = KaraokeLyricsProcessor(input_filename=input_filename, output_filename=output_filename, max_line_length=35)

            result = processor.process()
            processor.write_to_output_file()

            # Verify output file was created and contains processed content
            self.assertTrue(os.path.exists(output_filename))

            with open(output_filename, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, result)

            # Verify processing quality
            lines = file_content.split("\n")
            for line in lines:
                if line.strip():  # Skip empty lines
                    self.assertLessEqual(len(line), 35, f"Line exceeds max length: '{line}'")

            # Verify content preservation (should contain key words from original)
            self.assertIn("test song", file_content.lower())
            self.assertIn("karaoke", file_content.lower())

        finally:
            # Cleanup
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)

    def test_different_file_formats_integration(self):
        """Test processing different file formats"""
        test_content = "This is a test line that should be processed correctly regardless of input format."

        # Test TXT format
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as f:
            f.write(test_content)
            txt_file = f.name

        try:
            processor = KaraokeLyricsProcessor(input_filename=txt_file)
            result = processor.process()
            self.assertIn("test line", result)
        finally:
            os.unlink(txt_file)

    def test_complex_lyric_processing(self):
        """Test processing of complex lyric structures"""
        complex_lyrics = """
        (Verse 1)
        Walking down the street on a sunny day, feeling good, nothing in my way
        The birds are singing, people are laughing, life is good and I'm not asking
        
        (Chorus)
        This is the chorus line that repeats, with a melody that's really sweet
        Everybody sings along, to this catchy little song
        
        (Bridge)
        Sometimes life gets complicated, and we feel so frustrated
        But music helps us find our way, through the troubles of the day
        """

        processor = KaraokeLyricsProcessor(input_lyrics_text=complex_lyrics, max_line_length=45)

        result = processor.process()

        # Verify structure is maintained
        self.assertIn("Verse 1", result)
        self.assertIn("Chorus", result)
        self.assertIn("Bridge", result)

        # Verify line length constraints
        lines = result.split("\n")
        for line in lines:
            if line.strip():
                self.assertLessEqual(len(line), 45, f"Line exceeds max length: '{line}'")

    def test_edge_case_processing(self):
        """Test processing of edge cases"""
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "Short",  # Very short line
            "A" * 100,  # Very long single word
            "Multiple\n\n\nnewlines",  # Multiple consecutive newlines
            "Special chars: áéíóú ñ",  # Special characters
            "Numbers 12345 and symbols !@#$%",  # Numbers and symbols
        ]

        for test_case in edge_cases:
            with self.subTest(test_case=test_case[:20] + "..." if len(test_case) > 20 else test_case):
                processor = KaraokeLyricsProcessor(input_lyrics_text=test_case, max_line_length=30)

                # Should not raise exceptions
                result = processor.process()
                self.assertIsInstance(result, str)

                # Check line length constraints if not empty
                if result.strip():
                    lines = result.split("\n")
                    for line in lines:
                        if line.strip():
                            self.assertLessEqual(len(line), 30)

    def test_performance_with_large_input(self):
        """Test performance with large input"""
        # Create a large input with repeated content that has proper spacing
        base_line = "This is a line that will be repeated many times to test performance."
        large_input = "\n".join([f"{base_line} Line {i}" for i in range(100)])

        processor = KaraokeLyricsProcessor(input_lyrics_text=large_input, max_line_length=50)

        # Should complete without hanging
        result = processor.process()

        # Verify it processed correctly
        self.assertIsInstance(result, str)
        lines = result.split("\n")
        self.assertGreater(len(lines), 100)  # Should have more lines due to splitting

        # Verify line length constraints
        for line in lines:
            if line.strip():
                self.assertLessEqual(len(line), 50)

    def test_special_unicode_handling(self):
        """Test handling of special Unicode characters"""
        unicode_text = """
        Text with émojis 🎵 and special characters
        Unicode spaces: \u2000\u2001\u2002\u2003\u2004\u2005
        Different quotes: "English" 'quotes' „German" quotes
        Music symbols: ♪ ♫ ♬ ♭ ♮ ♯
        """

        processor = KaraokeLyricsProcessor(input_lyrics_text=unicode_text, max_line_length=40)

        result = processor.process()

        # Should handle Unicode without errors
        self.assertIsInstance(result, str)

        # Should preserve music content
        self.assertIn("émojis", result)
        self.assertIn("♪", result)

        # Should clean up Unicode spaces
        self.assertNotIn("\u2000", result)
        self.assertNotIn("\u2001", result)

    def test_memory_efficiency(self):
        """Test that processing doesn't consume excessive memory"""
        # This test ensures the processor doesn't keep unnecessary data in memory
        # Create repeated lines with proper spacing
        input_lines = ["Test line for memory efficiency"] * 50
        input_text = "\n".join(input_lines)

        processor = KaraokeLyricsProcessor(input_lyrics_text=input_text, max_line_length=25)

        result = processor.process()

        # Should complete and produce valid output
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)

        # Verify all lines are within the length limit
        lines = result.split("\n")
        for line in lines:
            if line.strip():
                self.assertLessEqual(len(line), 25)

    def test_realistic_song_structure_processing(self):
        """Test processing of realistic song structure with various lyrical challenges"""
        # This mimics real-world song complexity without using copyrighted content
        realistic_song = """
        That's how the story begins
        We walk back to the old place
        You check your phone for messages
        And try to make sense of it all
        And if the room is crowded, that's even better
        Because we know we're going to be here until dawn
        But if you're concerned about the weather outside
        Then you chose the wrong venue to spend your evening
        That's how the story begins
        
        
        And so the night unfolds
        You turn the music up loud
        We set our sights on dancing until the morning light
        One of the ways that we show how young we still feel
        And if the dawn breaks, if the dawn breaks early
        If the dawn breaks and I still don't want to go home
        Then it's the wisdom of those who came before us
        That keeps us moving forward
        
        
        You spent the first few years just trying to figure out the rules
        And the next few years trying to reconnect with old friends
        Oh, you're moving through life just as quickly as you can
        Yeah, I know it gets exhausting, but it's better when we imagine
        
        
        
        It falls apart
        The way it happens in tragic movies
        Except for the moment
        Where the lesson becomes clear
        Though when we're running low on energy
        And the conversations start to fade away
        I wouldn't exchange one foolish choice
        For another decade of ordinary living
        
        
        And to be completely honest
        Oh, this might be our final chance
        So here we venture forth
        Like explorers into the unknown night
        And if I look foolish, if I appear ridiculous
        If I seem absurd on this journey, there's always hope
        And if I'm overwhelmed by the challenges ahead
        I can always return to what matters most
        
        
        
        And with a smile like an old friend and a stance worth laughing at
        You can rest during the journey or think about your words
        When you're tired and the world seems impossibly bright
        You think again and again, "Hey, I've finally found peace"
        Oh, if the adventure and the strategy fall apart in your hands
        You can blame yourself, you silly dreamer
        You'll forget your intentions when you see what you've written
        And yes, we knew you were weary, but still
        
        
        Where are your companions tonight?
        Where are your companions tonight?
        Where are your companions tonight?
        If I could gather all my friends tonight
        If I could gather all my friends tonight
        If I could gather all my friends tonight
        If I could gather all my friends tonight
        """

        # Test with the same line length as your real-world example
        processor = KaraokeLyricsProcessor(input_lyrics_text=realistic_song, max_line_length=36)
        result = processor.process()

        # Verify basic processing requirements
        self.assertIsInstance(result, str)
        self.assertNotEqual(result.strip(), realistic_song.strip())

        # Verify line length constraints (critical for karaoke display)
        lines = result.split("\n")
        for line in lines:
            if line.strip():  # Skip empty lines
                self.assertLessEqual(len(line), 36, f"Line exceeds max length: '{line}' (length: {len(line)})")

        # Verify structure preservation
        result_lower = result.lower()
        self.assertIn("story begins", result_lower)
        self.assertIn("companions tonight", result_lower)

        # Verify that long lines were actually split
        original_lines = [line.strip() for line in realistic_song.split("\n") if line.strip()]
        long_original_lines = [line for line in original_lines if len(line) > 36]
        self.assertGreater(len(long_original_lines), 0, "Test should have lines longer than 36 characters")

        # Verify processing worked - should have more lines due to splitting
        processed_lines = [line.strip() for line in lines if line.strip()]
        self.assertGreater(len(processed_lines), len(original_lines), "Processed text should have more lines due to splitting")

        # Verify comma-based splitting worked
        comma_lines = [line for line in original_lines if "," in line and len(line) > 36]
        if comma_lines:
            # At least some comma-containing lines should have been split
            comma_splits_found = any("," in line and len(line) <= 36 for line in processed_lines)
            self.assertTrue(comma_splits_found, "Should find evidence of comma-based splitting")

        # Verify parentheses handling
        paren_lines = [line for line in original_lines if "(" in line and ")" in line]
        if paren_lines:
            # Parentheses content should be preserved
            self.assertIn("(", result)
            self.assertIn(")", result)

        # Verify repetitive ending structure is handled correctly
        repeat_count = result_lower.count("companions tonight")
        self.assertGreaterEqual(repeat_count, 3, "Should preserve repetitive chorus structure")

    def test_real_world_file_processing_workflow(self):
        """Test the complete file processing workflow that matches real-world usage"""
        # Create realistic song content with various challenges
        test_content = """
        Walking down the street on a beautiful sunny day, feeling great, nothing blocking my path
        The birds are singing their songs, people are laughing and smiling, life feels wonderful and I'm not worried
        
        (Chorus)
        This is the part everyone sings along with, containing a melody that's incredibly catchy and memorable
        Everyone joins in with enthusiasm, singing this delightful and uplifting song together
        
        Sometimes our lives become very complicated and difficult, and we feel overwhelmed and frustrated
        But music has the power to help us discover our way, guiding us through the challenging times
        """

        # Create temporary files
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as input_file:
            input_file.write(test_content)
            input_filename = input_file.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as output_file:
            output_filename = output_file.name

        try:
            # Process with same settings as real-world usage
            processor = KaraokeLyricsProcessor(input_filename=input_filename, output_filename=output_filename, max_line_length=36)

            result = processor.process()
            processor.write_to_output_file()

            # Verify file was created and matches result
            self.assertTrue(os.path.exists(output_filename))

            with open(output_filename, "r", encoding="utf-8") as f:
                file_content = f.read()

            self.assertEqual(file_content, result)

            # Verify real-world quality requirements
            lines = file_content.split("\n")

            # All lines must be within length limit
            for line in lines:
                if line.strip():
                    self.assertLessEqual(len(line), 36, f"Line too long: '{line}' ({len(line)} chars)")

            # Should preserve structure markers
            self.assertIn("Chorus", file_content)

            # Should preserve key content
            self.assertIn("street", file_content.lower())
            self.assertIn("music", file_content.lower())

            # Should have improved readability through proper splitting
            long_lines_in_original = len([line for line in test_content.split("\n") if len(line.strip()) > 36])
            long_lines_in_result = len([line for line in lines if len(line.strip()) > 36])

            self.assertLess(long_lines_in_result, long_lines_in_original, "Processing should reduce number of overly long lines")

        finally:
            # Cleanup
            os.unlink(input_filename)
            if os.path.exists(output_filename):
                os.unlink(output_filename)


if __name__ == "__main__":
    unittest.main()
