# Karaoke Lyrics Processor 🎶 ✍️

Karaoke Lyrics Processor is a tool to prepare song lyrics for karaoke video production. 

It processes lyrics by splitting long lines, handling parentheses, and ensuring that each line fits within a specified maximum length. 
This tool is especially useful for creating karaoke tracks where timing and line length are crucial for readability.

## Features

- **Line Splitting**: Automatically splits long lines of lyrics to ensure they fit within a specified maximum length, making them more readable and suitable for karaoke display.
- **Intelligent Splitting**: Finds the best split points in lines, considering punctuation and logical breaks in the lyrics.
- **Parentheses Handling**: Processes lines containing parentheses appropriately, ensuring that the lyrical flow is maintained.
- **Clipboard Support**: Copies the processed lyrics to the clipboard for easy pasting into video production software or other applications.
- **Debug Mode**: Offers a debug mode for detailed logging, helping with troubleshooting and fine-tuning the processing.

## Installation

To install the Karaoke Lyrics Processor, ensure you have Python 3.9 or newer in your environment. 

This package is available on PyPI and can be installed using pip. Run the following command in your terminal:

```bash
pip install karaoke-lyrics-processor
```

## Usage (CLI)

To process a file containing song lyrics, use the following command:

```bash
karaoke-lyrics-processor <path_to_lyrics_file>
```

By default, this will create a new file in your current directory with `(Lyrics Processed)` in the filename containing the processed lyrics.

### Command line options

```bash
usage: karaoke-lyrics-processor [-h] [-v] [-d] [-o OUTPUT] [-l LINE_LENGTH] filename

Process song lyrics to prepare them for karaoke video production, e.g. by splitting long lines

positional arguments:
  filename                                   The path to the file containing the song lyrics to process.

options:
  -h, --help                                 show this help message and exit
  -v, --version                              show program's version number and exit
  -d, --debug                                Enable debug mode, setting log level to DEBUG.
  -o OUTPUT, --output OUTPUT                 Optional: Specify the output filename for the processed lyrics.
  -l LINE_LENGTH, --line_length LINE_LENGTH  Optional: Specify the maximum line length for the processed lyrics. Default is 36.
```

## Contributing 🤝

Contributions are very much welcome! Please fork the repository and submit a pull request with your changes, and I'll try to review, merge and publish promptly!

- This project is 100% open-source and free for anyone to use and modify as they wish. 
- If the maintenance workload for this repo somehow becomes too much for me I'll ask for volunteers to share maintainership of the repo, though I don't think that is very likely

## License 📄

This project is licensed under the MIT [License](LICENSE).

## Contact 💌

For questions or feedback, please raise an issue or reach out to @beveradb ([Andrew Beveridge](mailto:andrew@beveridge.uk)) directly.
