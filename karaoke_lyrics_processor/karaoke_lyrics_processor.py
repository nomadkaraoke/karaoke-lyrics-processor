import re
import logging
import pyperclip
import unicodedata
import docx2txt
from striprtf.striprtf import rtf_to_text
import os
import codecs


class KaraokeLyricsProcessor:
    def __init__(
        self,
        log_level=logging.DEBUG,
        log_formatter=None,
        input_filename=None,
        input_lyrics_text=None,
        output_filename=None,
        max_line_length=36,
    ):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.log_level = log_level
        self.log_formatter = log_formatter

        self.log_handler = logging.StreamHandler()

        if self.log_formatter is None:
            self.log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")

        self.log_handler.setFormatter(self.log_formatter)
        self.logger.addHandler(self.log_handler)

        self.logger.debug(f"Karaoke Lyrics Processor instantiating with max_line_length: {max_line_length}")

        self.input_filename = input_filename
        self.output_filename = output_filename
        self.max_line_length = max_line_length

        if input_lyrics_text is not None and input_filename is None:
            self.input_lyrics_lines = input_lyrics_text.splitlines()
        elif input_filename is not None and input_lyrics_text is None:
            self.input_lyrics_lines = self.read_input_file()
        else:
            raise ValueError("Either input_lyrics or input_filename must be set, but not both.")

    def read_input_file(self):
        file_extension = os.path.splitext(self.input_filename)[1].lower()

        self.logger.debug(f"Reading input file: {self.input_filename}")

        if file_extension == ".txt":
            return self.read_txt_file()
        elif file_extension in [".docx", ".doc"]:
            return self.read_doc_file()
        elif file_extension == ".rtf":
            return self.read_rtf_file()
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    def read_txt_file(self):
        with codecs.open(self.input_filename, "r", encoding="utf-8") as infile:
            content = infile.read()
        self.logger.debug(f"Raw content read from file: {repr(content)}")
        lines = content.splitlines()
        self.logger.debug(f"Number of lines read: {len(lines)}")
        for i, line in enumerate(lines):
            self.logger.debug(f"Line {i}: {repr(line)}")
        return self.clean_text(content).splitlines()

    def read_doc_file(self):
        text = docx2txt.process(self.input_filename)
        return self.clean_text(text).splitlines()

    def read_rtf_file(self):
        with open(self.input_filename, "r", encoding="utf-8") as file:
            rtf_text = file.read()
        plain_text = rtf_to_text(rtf_text)
        return self.clean_text(plain_text).splitlines()

    def clean_text(self, text):
        self.logger.debug(f"Cleaning text: {repr(text)}")
        # Remove any non-printable characters except newlines and U+2005 (four-per-em space)
        cleaned = "".join(char for char in text if char.isprintable() or char in ["\n", "\u2005"])
        self.logger.debug(f"Text after removing non-printable characters: {repr(cleaned)}")
        # Replace multiple newlines with a single newline
        cleaned = re.sub(r"\n{2,}", "\n", cleaned)
        self.logger.debug(f"Text after replacing multiple newlines: {repr(cleaned)}")
        # Remove leading/trailing whitespace from each line
        cleaned = "\n".join(line.strip() for line in cleaned.splitlines())
        self.logger.debug(f"Final cleaned text: {repr(cleaned)}")
        return cleaned

    def find_best_split_point(self, line):
        """
        Find the best split point in a line based on the specified criteria.
        """

        self.logger.debug(f"Finding best_split_point for line: {line}")
        words = line.split()
        mid_word_index = len(words) // 2
        self.logger.debug(f"words: {words} mid_word_index: {mid_word_index}")

        # Check for a comma within one or two words of the middle word
        if "," in line:
            mid_point = len(" ".join(words[:mid_word_index]))
            comma_indices = [i for i, char in enumerate(line) if char == ","]

            for index in comma_indices:
                if abs(mid_point - index) < 20 and len(line[: index + 1].strip()) <= self.max_line_length:
                    self.logger.debug(
                        f"Found comma at index {index} which is within 20 characters of mid_point {mid_point} and results in a suitable line length, accepting as split point"
                    )
                    return index + 1  # Include the comma in the first line

        # Check for 'and'
        if " and " in line:
            mid_point = len(line) // 2
            and_indices = [m.start() for m in re.finditer(" and ", line)]
            for index in sorted(and_indices, key=lambda x: abs(x - mid_point)):
                if len(line[: index + len(" and ")].strip()) <= self.max_line_length:
                    self.logger.debug(f"Found 'and' at index {index} which results in a suitable line length, accepting as split point")
                    return index + len(" and ")

        # If no better split point is found, try splitting at the middle word
        if len(words) > 2 and mid_word_index > 0:
            split_at_middle = len(" ".join(words[:mid_word_index]))
            if split_at_middle <= self.max_line_length:
                self.logger.debug(f"Splitting at middle word index: {mid_word_index}")
                return split_at_middle

        # If the line is still too long, find the last space before max_line_length
        if len(line) > self.max_line_length:
            last_space = line.rfind(" ", 0, self.max_line_length)
            if last_space != -1:
                self.logger.debug(f"Splitting at last space before max_line_length: {last_space}")
                return last_space
            else:
                # If no space is found, split at max_line_length
                self.logger.debug(f"No space found, forcibly splitting at max_line_length: {self.max_line_length}")
                return self.max_line_length

        # If the line is shorter than max_line_length, return its length
        return len(line)

    def replace_non_printable_spaces(self, text):
        """
        Replace non-printable space-like characters, tabs, and other whitespace with regular spaces,
        excluding newline characters.
        """
        self.logger.debug(f"Replacing non-printable spaces in: {repr(text)}")

        # Log each character and its Unicode code point
        for i, char in enumerate(text):
            self.logger.debug(f"Character at position {i}: {repr(char)} (Unicode: U+{ord(char):04X})")

        # Define a pattern for space-like characters, including tabs and other whitespace, but excluding newlines
        space_pattern = r"[^\S\n\r]|\u00A0|\u1680|\u2000-\u200A|\u202F|\u205F|\u3000"

        # Replace matched characters with a regular space
        cleaned_text = re.sub(space_pattern, " ", text)

        # Log the result of the replacement
        self.logger.debug(f"Text after replacing non-printable spaces: {repr(cleaned_text)}")

        # Remove leading/trailing spaces and collapse multiple spaces into one, preserving newlines
        final_text = re.sub(r" +", " ", cleaned_text).strip()

        # Log the final result
        self.logger.debug(f"Final text after cleaning: {repr(final_text)}")

        return final_text

    def clean_punctuation_spacing(self, text):
        """
        Remove unnecessary spaces before punctuation marks.
        """
        self.logger.debug(f"Cleaning punctuation spacing in: {text}")
        # Remove space before comma, period, exclamation mark, question mark, colon, and semicolon
        cleaned_text = re.sub(r"\s+([,\.!?:;])", r"\1", text)
        self.logger.debug(f"Text after cleaning punctuation spacing: {cleaned_text}")
        return cleaned_text

    def process_line(self, line):
        """
        Process a single line to ensure it's within the maximum length,
        handle parentheses, and replace non-printable spaces.
        """
        # Replace non-printable spaces at the beginning
        line = self.replace_non_printable_spaces(line)
        # Clean up punctuation spacing
        line = self.clean_punctuation_spacing(line)

        processed_lines = []
        iteration_count = 0
        max_iterations = 100  # Failsafe limit

        while len(line) > self.max_line_length:
            if iteration_count > max_iterations:
                self.logger.error(f"Maximum iterations exceeded in process_line for line: {line}")
                break

            # Check if the line contains parentheses
            if "(" in line and ")" in line:
                start_paren = line.find("(")
                end_paren = line.find(")") + 1
                if end_paren < len(line) and line[end_paren] == ",":
                    end_paren += 1

                if start_paren > 0:
                    processed_lines.append(line[:start_paren].strip())
                processed_lines.append(line[start_paren:end_paren].strip())
                line = line[end_paren:].strip()
            else:
                split_point = self.find_best_split_point(line)
                processed_lines.append(line[:split_point].strip())
                line = line[split_point:].strip()

            iteration_count += 1

        if line:  # Add the remaining part if not empty
            processed_lines.append(line)

        return processed_lines

    def process(self):
        self.logger.info(f"Processing input lyrics from {self.input_filename}")

        lyrics_lines = self.input_lyrics_lines
        processed_lyrics_text = ""
        iteration_count = 0
        max_iterations = 100  # Failsafe limit

        all_processed = False
        while not all_processed:
            if iteration_count > max_iterations:
                self.logger.error("Maximum iterations exceeded while processing lyrics.")
                break

            all_processed = True
            new_lyrics = []
            for line in lyrics_lines:
                line = line.strip()
                processed = self.process_line(line)
                new_lyrics.extend(processed)
                if any(len(l) > self.max_line_length for l in processed):
                    all_processed = False

            lyrics_lines = new_lyrics

            iteration_count += 1

        processed_lyrics_text = "\n".join(lyrics_lines)

        # Final pass to replace any remaining non-printable spaces and clean punctuation
        processed_lyrics_text = self.replace_non_printable_spaces(processed_lyrics_text)
        processed_lyrics_text = self.clean_punctuation_spacing(processed_lyrics_text)

        self.processed_lyrics_text = processed_lyrics_text
        pyperclip.copy(processed_lyrics_text)

        self.logger.info(f"Processed lyrics copied to clipboard.")

        return processed_lyrics_text

    def write_to_output_file(self):
        # Ensure the output filename has a .txt extension
        base, _ = os.path.splitext(self.output_filename)
        self.output_filename = f"{base}.txt"

        with open(self.output_filename, "w", encoding="utf-8") as outfile:
            outfile.write(self.processed_lyrics_text)

        self.logger.info(f"Processed lyrics written to output file {self.output_filename}")
