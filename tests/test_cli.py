import unittest
import tempfile
import os
import sys
import argparse
from unittest.mock import patch, MagicMock
from io import StringIO
from karaoke_lyrics_processor.cli import main


class TestCLI(unittest.TestCase):
    def setUp(self):
        self.test_file_content = "This is a test line that should be processed by the CLI"

    def create_temp_file(self, content, suffix=".txt"):
        """Helper method to create temporary files for testing"""
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8")
        temp_file.write(content)
        temp_file.close()
        return temp_file.name

    def test_main_with_basic_arguments(self):
        """Test CLI main function with basic arguments"""
        input_file = self.create_temp_file(self.test_file_content)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    mock_processor_class.assert_called_once()
                    mock_processor.process.assert_called_once()
                    mock_processor.write_to_output_file.assert_called_once()
        finally:
            os.unlink(input_file)

    def test_main_with_debug_flag(self):
        """Test CLI main function with debug flag"""
        input_file = self.create_temp_file(self.test_file_content)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-d", input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    # Check that debug log level was passed
                    call_args = mock_processor_class.call_args
                    self.assertEqual(call_args.kwargs["log_level"], 10)  # logging.DEBUG is 10
        finally:
            os.unlink(input_file)

    def test_main_with_custom_output_file(self):
        """Test CLI main function with custom output file"""
        input_file = self.create_temp_file(self.test_file_content)
        custom_output = "custom_output.txt"

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-o", custom_output, input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = custom_output

                    main()

                    # Check that custom output filename was passed
                    call_args = mock_processor_class.call_args
                    self.assertEqual(call_args.kwargs["output_filename"], custom_output)
        finally:
            os.unlink(input_file)

    def test_main_with_custom_line_length(self):
        """Test CLI main function with custom line length"""
        input_file = self.create_temp_file(self.test_file_content)
        custom_length = 50

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-l", str(custom_length), input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    # Check that custom line length was passed
                    call_args = mock_processor_class.call_args
                    self.assertEqual(call_args.kwargs["max_line_length"], custom_length)
        finally:
            os.unlink(input_file)

    def test_main_with_all_arguments(self):
        """Test CLI main function with all arguments"""
        input_file = self.create_temp_file(self.test_file_content)
        custom_output = "custom_output.txt"
        custom_length = 50

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-d", "-o", custom_output, "-l", str(custom_length), input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = custom_output

                    main()

                    # Check all arguments were passed correctly
                    call_args = mock_processor_class.call_args
                    self.assertEqual(call_args.kwargs["log_level"], 10)  # logging.DEBUG for debug
                    self.assertEqual(call_args.kwargs["output_filename"], custom_output)
                    self.assertEqual(call_args.kwargs["max_line_length"], custom_length)
                    self.assertEqual(call_args.kwargs["input_filename"], input_file)
        finally:
            os.unlink(input_file)

    def test_main_generates_default_output_filename(self):
        """Test that main generates default output filename correctly"""
        input_file = self.create_temp_file(self.test_file_content, suffix=" (Lyrics).txt")

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    # Check that default output filename was generated
                    call_args = mock_processor_class.call_args
                    expected_output = input_file.replace(" (Lyrics).txt", " (Lyrics Processed).txt")
                    self.assertEqual(call_args.kwargs["output_filename"], expected_output)
        finally:
            os.unlink(input_file)

    def test_main_removes_lyrics_from_base_name(self):
        """Test that main removes '(Lyrics)' from base name when generating output filename"""
        input_filename = "Song Name (Lyrics).txt"
        input_file = self.create_temp_file(self.test_file_content)

        # Rename the temp file to have the desired name structure
        new_path = os.path.join(os.path.dirname(input_file), input_filename)
        os.rename(input_file, new_path)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", new_path]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    # Check that '(Lyrics)' was removed from base name
                    call_args = mock_processor_class.call_args
                    expected_output = "Song Name (Lyrics Processed).txt"
                    expected_full_path = os.path.join(os.path.dirname(new_path), expected_output)
                    self.assertEqual(call_args.kwargs["output_filename"], expected_full_path)
        finally:
            os.unlink(new_path)

    @patch("karaoke_lyrics_processor.cli.version")
    def test_version_argument(self, mock_version):
        """Test version argument displays version correctly"""
        mock_version.return_value = "1.0.0"

        with patch("sys.argv", ["karaoke-lyrics-processor", "--version"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()

                # argparse exits with code 0 for version
                self.assertEqual(cm.exception.code, 0)
                output = mock_stdout.getvalue()
                self.assertIn("1.0.0", output)

    def test_help_argument(self):
        """Test help argument displays help correctly"""
        with patch("sys.argv", ["karaoke-lyrics-processor", "--help"]):
            with patch("sys.stdout", new_callable=StringIO) as mock_stdout:
                with self.assertRaises(SystemExit) as cm:
                    main()

                # argparse exits with code 0 for help
                self.assertEqual(cm.exception.code, 0)
                output = mock_stdout.getvalue()
                self.assertIn("Process song lyrics", output)
                self.assertIn("filename", output)

    def test_missing_filename_argument(self):
        """Test behavior when filename argument is missing"""
        with patch("sys.argv", ["karaoke-lyrics-processor"]):
            with patch("sys.stderr", new_callable=StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()

                # argparse exits with code 2 for missing required argument
                self.assertEqual(cm.exception.code, 2)

    def test_invalid_line_length_argument(self):
        """Test behavior with invalid line length argument"""
        input_file = self.create_temp_file(self.test_file_content)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-l", "invalid", input_file]):
                with patch("sys.stderr", new_callable=StringIO):
                    with self.assertRaises(SystemExit) as cm:
                        main()

                    # argparse exits with code 2 for invalid argument type
                    self.assertEqual(cm.exception.code, 2)
        finally:
            os.unlink(input_file)

    def test_logging_configuration(self):
        """Test that logging is configured correctly"""
        input_file = self.create_temp_file(self.test_file_content)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    with patch("logging.getLogger") as mock_get_logger:
                        mock_logger = MagicMock()
                        mock_get_logger.return_value = mock_logger

                        main()

                        # Verify logger was configured
                        mock_get_logger.assert_called()
                        mock_logger.addHandler.assert_called()
                        mock_logger.setLevel.assert_called()
        finally:
            os.unlink(input_file)

    def test_processor_initialization_with_correct_parameters(self):
        """Test that KaraokeLyricsProcessor is initialized with correct parameters"""
        input_file = self.create_temp_file(self.test_file_content)

        try:
            with patch("sys.argv", ["karaoke-lyrics-processor", "-d", input_file]):
                with patch("karaoke_lyrics_processor.cli.KaraokeLyricsProcessor") as mock_processor_class:
                    mock_processor = MagicMock()
                    mock_processor_class.return_value = mock_processor
                    mock_processor.output_filename = "test_output.txt"

                    main()

                    # Verify processor was initialized with correct parameters
                    mock_processor_class.assert_called_once()
                    call_args = mock_processor_class.call_args

                    # Check required parameters are present
                    self.assertIn("input_filename", call_args.kwargs)
                    self.assertIn("output_filename", call_args.kwargs)
                    self.assertIn("max_line_length", call_args.kwargs)
                    self.assertIn("log_level", call_args.kwargs)
                    self.assertIn("log_formatter", call_args.kwargs)

                    # Check specific values
                    self.assertEqual(call_args.kwargs["input_filename"], input_file)
                    self.assertEqual(call_args.kwargs["max_line_length"], 36)  # default value
        finally:
            os.unlink(input_file)

    def test_empty_filename_handling(self):
        """Test handling when filename is empty string"""
        with patch("sys.argv", ["karaoke-lyrics-processor", ""]):
            with patch("sys.stderr", new_callable=StringIO):
                with self.assertRaises(SystemExit) as cm:
                    main()
                # Should exit with code 1 for empty filename
                self.assertEqual(cm.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
