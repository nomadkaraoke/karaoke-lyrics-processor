# Karaoke Lyrics Processor 🎶 ✍️

![PyPI - Version](https://img.shields.io/pypi/v/karaoke-lyrics-processor)
![Python Version](https://img.shields.io/badge/python-3.10+-blue)
![Tests](https://github.com/nomadkaraoke/karaoke-lyrics-processor/workflows/Test%20and%20Publish/badge.svg)
![Test Coverage](https://codecov.io/gh/nomadkaraoke/karaoke-lyrics-processor/branch/main/graph/badge.svg)

Karaoke Lyrics Processor is a tool to prepare song lyrics for karaoke video production. 

It processes lyrics by intelligently splitting long lines, handling parentheses, cleaning punctuation, and ensuring that each line fits within a specified maximum length. This tool is especially useful for creating karaoke tracks where timing and line length are crucial for readability.

## ✨ Features

### Core Processing
- **Smart Line Splitting**: Automatically splits long lines using intelligent algorithms that prioritize commas, "and" conjunctions, and natural word boundaries
- **Parentheses Handling**: Properly processes lines containing parentheses, maintaining lyrical flow and handling nested parentheses
- **Punctuation Cleanup**: Removes unnecessary spaces before punctuation marks and fixes comma placement
- **Unicode Support**: Handles international characters and special Unicode spaces correctly
- **Safety Mechanisms**: Built-in infinite loop prevention and iteration limits for robust processing

### File Format Support
- **Multiple Input Formats**: Supports TXT, DOCX, DOC, and RTF files
- **Encoding Handling**: Properly handles UTF-8 and various text encodings
- **Fallback Processing**: Uses multiple libraries (docx2txt, textract) for maximum compatibility

### User Experience
- **Clipboard Integration**: Automatically copies processed lyrics to clipboard for easy pasting
- **Flexible Output**: Customizable output filenames and automatic naming conventions
- **Debug Mode**: Comprehensive logging for troubleshooting and fine-tuning
- **Command Line Interface**: Full-featured CLI with helpful options and error handling

### Quality & Reliability
- **98% Test Coverage**: Comprehensive test suite with 88 tests covering all functionality
- **Edge Case Handling**: Robust handling of empty files, very long words, malformed input, and unusual formatting
- **Performance Tested**: Memory efficient processing with performance safeguards
- **Error Recovery**: Graceful error handling with informative messages

## 🚀 Installation

To install the Karaoke Lyrics Processor, ensure you have Python 3.9 or newer in your environment. 

This package is available on PyPI and can be installed using pip:

```bash
pip install karaoke-lyrics-processor
```

## 📋 Usage

### Command Line Interface

Process a lyrics file with default settings:
```bash
karaoke-lyrics-processor path/to/your/lyrics.txt
```

**Output**: Creates `path/to/your/lyrics (Lyrics Processed).txt` with processed lyrics.

### Advanced Usage Examples

```bash
# Custom output file
karaoke-lyrics-processor -o my_processed_lyrics.txt song.txt

# Custom line length (default is 36 characters)
karaoke-lyrics-processor -l 50 song.txt

# Debug mode for detailed logging
karaoke-lyrics-processor -d song.txt

# Combine all options
karaoke-lyrics-processor -d -o output.txt -l 40 input.docx
```

### Supported Input Formats

- **`.txt`** - Plain text files (UTF-8 recommended)
- **`.docx`** - Microsoft Word documents
- **`.doc`** - Legacy Microsoft Word documents  
- **`.rtf`** - Rich Text Format files

### Command Line Options

```bash
usage: karaoke-lyrics-processor [-h] [-v] [-d] [-o OUTPUT] [-l LINE_LENGTH] filename

Process song lyrics to prepare them for karaoke video production

positional arguments:
  filename                                   Path to the lyrics file to process

options:
  -h, --help                                 Show help message and exit
  -v, --version                              Show program's version number and exit
  -d, --debug                                Enable debug mode with detailed logging
  -o OUTPUT, --output OUTPUT                 Specify the output filename
  -l LINE_LENGTH, --line_length LINE_LENGTH  Maximum line length (default: 36)
```

## 🔧 Processing Features

### Intelligent Line Splitting
The processor uses sophisticated algorithms to find optimal split points:

1. **Comma Priority**: Splits at commas near the middle of long lines
2. **Conjunction Splitting**: Uses "and" as split points when appropriate  
3. **Word Boundaries**: Respects word boundaries and avoids breaking words
4. **Parentheses Awareness**: Handles parenthetical content intelligently
5. **Fallback Mechanisms**: Forces splits when no natural break points exist

### Text Cleaning
- Removes non-printable characters while preserving essential formatting
- Normalizes various Unicode space characters to regular spaces
- Consolidates multiple consecutive newlines
- Strips unnecessary whitespace from line beginnings and ends

### Error Handling
- Graceful handling of unsupported file formats
- Recovery from encoding issues
- Protection against infinite processing loops
- Clear error messages for troubleshooting

## 🧪 Development & Testing

This package maintains high quality standards with comprehensive testing:

- **98% Test Coverage** across all modules
- **88 Total Tests** including unit, integration, and CLI tests
- **Edge Case Testing** for robustness
- **Performance Testing** to prevent regressions
- **Continuous Integration** with automated testing

### Running Tests

```bash
# Install development dependencies
pip install pytest pytest-cov

# Run the full test suite
pytest --cov=karaoke_lyrics_processor --cov-report=html

# Run with verbose output
pytest -v

# Generate coverage report
pytest --cov-report=term-missing
```

## 🤝 Contributing

Contributions are very much welcome! This project follows best practices for maintainability:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for your changes
4. **Ensure** tests pass and maintain >90% coverage
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Open** a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/nomadkaraoke/karaoke-lyrics-processor.git
cd karaoke-lyrics-processor

# Install development dependencies
pip install -e ".[dev]"

# Run tests
python run_tests.py
```

- This project is 100% open-source and free for anyone to use and modify as they wish
- All contributions are tested automatically via CI/CD
- Code quality is maintained through comprehensive testing and reviews

## 📄 License

This project is licensed under the MIT [License](LICENSE).

## 💌 Contact

For questions, feature requests, or bug reports:
- **Issues**: [GitHub Issues](https://github.com/nomadkaraoke/karaoke-lyrics-processor/issues)
- **Email**: [Andrew Beveridge](mailto:andrew@beveridge.uk) (@beveradb)
- **Discussions**: [GitHub Discussions](https://github.com/nomadkaraoke/karaoke-lyrics-processor/discussions)

---

*Built with ❤️ for the karaoke community*
