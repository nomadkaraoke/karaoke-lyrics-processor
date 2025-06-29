import re
import logging
import pyperclip
import docx2txt
from striprtf.striprtf import rtf_to_text
import os
import codecs
import textract  # Add textract import


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
        lines = content.splitlines()
        self.logger.debug(f"Read {len(lines)} lines from {self.input_filename}")
        return self.clean_text(content).splitlines()

    def read_doc_file(self):
        try:
            text = docx2txt.process(self.input_filename)
        except Exception as e:
            self.logger.debug(f"docx2txt failed to read file, trying textract: {str(e)}")
            try:
                # Use textract as fallback for .doc files
                text = textract.process(self.input_filename).decode("utf-8")
            except Exception as e2:
                raise ValueError(f"Failed to read doc file with both docx2txt and textract: {str(e2)}")
        return self.clean_text(text).splitlines()

    def read_rtf_file(self):
        with open(self.input_filename, "r", encoding="utf-8") as file:
            rtf_text = file.read()
        plain_text = rtf_to_text(rtf_text)
        return self.clean_text(plain_text).splitlines()

    def clean_text(self, text):
        # Remove any non-printable characters except newlines and U+2005
        original_len = len(text)
        cleaned = "".join(char for char in text if char.isprintable() or char in ["\n", "\u2005"])
        if len(cleaned) != original_len:
            self.logger.debug(f"Removed {original_len - len(cleaned)} non-printable characters")

        # Replace multiple newlines with a single newline
        newlines_before = cleaned.count("\n")
        cleaned = re.sub(r"\n{2,}", "\n", cleaned)
        newlines_after = cleaned.count("\n")
        if newlines_before != newlines_after:
            self.logger.debug(f"Consolidated {newlines_before - newlines_after} extra newlines")

        # Remove leading/trailing whitespace from each line
        lines_before = cleaned.splitlines()
        cleaned = "\n".join(line.strip() for line in lines_before)
        lines_after = cleaned.splitlines()

        # Count lines that changed due to stripping
        changed_lines = sum(1 for before, after in zip(lines_before, lines_after) if before != after)
        if changed_lines > 0:
            self.logger.debug(f"Stripped whitespace from {changed_lines} lines")

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
        # Log each character and its Unicode code point
        # for i, char in enumerate(text):
        #     self.logger.debug(f"Character at position {i}: {repr(char)} (Unicode: U+{ord(char):04X})")

        # Define a pattern for space-like characters, including tabs and other whitespace, but excluding newlines
        space_pattern = r"[^\S\n]|\u00A0|\u1680|\u2000-\u200A|\u202F|\u205F|\u3000"

        # Replace matched characters with a regular space
        cleaned_text = re.sub(space_pattern, " ", text)

        # Remove leading/trailing spaces and collapse multiple spaces into one, preserving newlines
        final_text = re.sub(r" +", " ", cleaned_text).strip()

        return final_text

    def clean_punctuation_spacing(self, text):
        """
        Remove unnecessary spaces before punctuation marks.
        """
        self.logger.debug(f"Cleaning punctuation spacing")
        # Remove space before comma, period, exclamation mark, question mark, colon, and semicolon
        cleaned_text = re.sub(r"\s+([,\.!?:;])", r"\1", text)

        return cleaned_text

    def fix_commas_inside_quotes(self, text):
        """
        Move commas inside quotes to after the closing quote.
        """
        self.logger.debug(f"Fixing commas inside quotes")
        # Use regex to find patterns where a comma is inside quotes and move it outside
        fixed_text = re.sub(r'(".*?)(,)(\s*")', r"\1\3\2", text)

        return fixed_text

    def process_line(self, line):
        """
        Process a single line to ensure it's within the maximum length,
        handle parentheses, and replace non-printable spaces.
        """
        line = self.replace_non_printable_spaces(line)
        line = self.clean_punctuation_spacing(line)
        line = self.fix_commas_inside_quotes(line)

        processed_lines = []
        iteration_count = 0
        max_iterations = 100  # Failsafe limit

        while len(line) > self.max_line_length and iteration_count < max_iterations:
            # Check if the line contains parentheses
            if "(" in line and ")" in line:
                start_paren = line.find("(")
                end_paren = self.find_matching_paren(line, start_paren)
                if end_paren < len(line) and line[end_paren] == ",":
                    end_paren += 1

                # Process text before parentheses if it exists
                if start_paren > 0:
                    before_paren = line[:start_paren].strip()
                    processed_lines.extend(self.split_line(before_paren))

                # Process text within parentheses
                paren_content = line[start_paren : end_paren + 1].strip()
                if len(paren_content) > self.max_line_length:
                    # Split the content within parentheses if it's too long
                    split_paren_content = self.split_line(paren_content)
                    processed_lines.extend(split_paren_content)
                else:
                    processed_lines.append(paren_content)

                line = line[end_paren + 1 :].strip()
            else:
                split_point = self.find_best_split_point(line)
                # Ensure we make progress - if split_point is 0 or too small, force a reasonable split
                if split_point <= 0:
                    split_point = min(self.max_line_length, len(line))
                processed_lines.append(line[:split_point].strip())
                line = line[split_point:].strip()

            iteration_count += 1

        if line:  # Add any remaining part
            processed_lines.extend(self.split_line(line))

        if iteration_count >= max_iterations:
            self.logger.error(f"Maximum iterations exceeded in process_line for line: {line}")

        return processed_lines

    def find_matching_paren(self, line, start_index):
        """
        Find the index of the matching closing parenthesis for the opening parenthesis at start_index.
        """
        stack = 0
        for i in range(start_index, len(line)):
            if line[i] == "(":
                stack += 1
            elif line[i] == ")":
                stack -= 1
                if stack == 0:
                    return i
        return -1  # No matching parenthesis found

    def split_line(self, line):
        """
        Split a line into multiple lines if it exceeds the maximum length.
        """
        if len(line) <= self.max_line_length:
            return [line]

        split_lines = []
        while len(line) > self.max_line_length:
            split_point = self.find_best_split_point(line)
            # Ensure we make progress - if split_point is 0 or too small, force a reasonable split
            if split_point <= 0:
                split_point = min(self.max_line_length, len(line))
            split_lines.append(line[:split_point].strip())
            line = line[split_point:].strip()

        if line:
            split_lines.append(line)

        return split_lines

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
            previous_line_count = len(lyrics_lines)

            for line in lyrics_lines:
                line = line.strip()
                processed = self.process_line(line)
                new_lyrics.extend(processed)
                if any(len(l) > self.max_line_length for l in processed):
                    all_processed = False

            lyrics_lines = new_lyrics

            # Safety check: if no progress is being made, break out of the loop
            if len(lyrics_lines) == previous_line_count and not all_processed:
                self.logger.warning("No progress made in processing, forcing completion to avoid infinite loop")
                break

            iteration_count += 1

        processed_lyrics_text = "\n".join(lyrics_lines)

        # Final pass to replace any remaining non-printable spaces and clean punctuation
        processed_lyrics_text = self.replace_non_printable_spaces(processed_lyrics_text)
        processed_lyrics_text = self.clean_punctuation_spacing(processed_lyrics_text)

        self.processed_lyrics_text = processed_lyrics_text

        # Try to copy to clipboard, but don't fail if it's not available
        try:
            pyperclip.copy(processed_lyrics_text)
            self.logger.info("Processed lyrics copied to clipboard.")
        except pyperclip.PyperclipException as e:
            self.logger.warning(f"Could not copy to clipboard: {str(e)}")

        return processed_lyrics_text

    def write_to_output_file(self):
        # Ensure the output filename has a .txt extension
        base, _ = os.path.splitext(self.output_filename)
        self.output_filename = f"{base}.txt"

        with open(self.output_filename, "w", encoding="utf-8") as outfile:
            outfile.write(self.processed_lyrics_text)

        self.logger.info(f"Processed lyrics written to output file {self.output_filename}")
