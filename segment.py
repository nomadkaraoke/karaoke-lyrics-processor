import sys
import os
import re

def process_file_for_reading(input_file):
    """
    Process the input file to split long lines into multiple lines for easier reading.
    The output file is saved beside the input file with '-split' added to its filename.

    Parameters:
    input_file (str): The path of the input text file.
    """

    def find_best_split_point(line):
        """
        Find the best split point in a line based on the specified criteria.
        """
        words = line.split()
        mid_word_index = len(words) // 2

        # Check for a comma within one or two words of the middle word
        if ',' in line:
            mid_point = len(' '.join(words[:mid_word_index]))
            comma_indices = [i for i, char in enumerate(line) if char == ',']

            for index in comma_indices:
                if abs(mid_point - index) < 20:  # Roughly the length of two average words
                    return index + 1  # Include the comma in the first line

        # Check for 'and'
        if ' and ' in line:
            mid_point = len(line) // 2
            and_indices = [m.start() for m in re.finditer(' and ', line)]
            split_point = min(and_indices, key=lambda x: abs(x - mid_point))
            return split_point + len(' and ')  # Include 'and' in the first line

        # Split at the middle word
        return len(' '.join(words[:mid_word_index]))

    output_file = os.path.splitext(input_file)[0] + "-split" + os.path.splitext(input_file)[1]

    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if len(line) > 40:
                split_point = find_best_split_point(line)
                outfile.write(line[:split_point].strip() + '\n')
                outfile.write(line[split_point:].strip() + '\n')
            else:
                outfile.write(line + '\n')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_file>")
    else:
        input_file_path = sys.argv[1]
        process_file_for_reading(input_file_path)
