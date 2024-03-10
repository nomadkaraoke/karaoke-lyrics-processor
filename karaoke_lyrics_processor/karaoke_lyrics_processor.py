import re
import logging
import pyperclip


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
            self.input_lyrics_lines = self.read_input_lyrics_file()
        else:
            raise ValueError("Either input_lyrics or input_filename must be set, but not both.")

    def read_input_lyrics_file(self):
        with open(self.input_filename, "r") as infile:
            return infile.readlines()

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

        # If the line is still too long, forcibly split at the maximum length
        forced_split_point = self.max_line_length
        if len(line) > forced_split_point:
            self.logger.debug(f"Line is still too long, forcibly splitting at position {forced_split_point}")
            return forced_split_point

    def process_line(self, line):
        """
        Process a single line to ensure it's within the maximum length,
        and handle parentheses.
        """
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

        self.processed_lyrics_text = processed_lyrics_text
        pyperclip.copy(processed_lyrics_text)

        self.logger.info(f"Processed lyrics copied to clipboard.")

        return processed_lyrics_text

    def write_to_output_file(self):

        with open(self.output_filename, "w") as outfile:
            outfile.write(self.processed_lyrics_text)

        self.logger.info(f"Processed lyrics written to output file {self.output_filename}")
