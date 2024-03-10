#!/usr/bin/env python
import argparse
import logging
import pkg_resources
from karaoke_lyrics_processor import KaraokeLyricsProcessor


def main():
    logger = logging.getLogger(__name__)
    log_handler = logging.StreamHandler()
    log_formatter = logging.Formatter(fmt="%(asctime)s.%(msecs)03d - %(levelname)s - %(module)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    log_handler.setFormatter(log_formatter)
    logger.addHandler(log_handler)

    parser = argparse.ArgumentParser(
        description="Process song lyrics to prepare them for karaoke video production, e.g. by splitting long lines",
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, max_help_position=50),
    )

    package_version = pkg_resources.get_distribution("karaoke-lyrics-processor").version
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {package_version}")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode, setting log level to DEBUG.")
    parser.add_argument("-o", "--output", type=str, help="Optional: Specify the output filename for the processed lyrics.")
    parser.add_argument(
        "-l",
        "--line_length",
        type=int,
        default=36,
        help="Optional: Specify the maximum line length for the processed lyrics. Default is 36.",
    )
    parser.add_argument("filename", type=str, help="The path to the file containing the song lyrics to process.")

    args = parser.parse_args()

    if len(args.filename) < 1:
        parser.print_help()
        exit(1)

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logger.setLevel(log_level)

    logger.info(f"Karaoke Lyrics processor beginning with input file: {args.filename}")

    filename_parts = args.filename.rsplit(".", 1)
    if args.output:
        output_filename = args.output
    else:
        output_filename = f"{filename_parts[0]} (Lyrics Processed).{filename_parts[1]}"

    processor = KaraokeLyricsProcessor(
        log_level=log_level,
        log_formatter=log_formatter,
        input_filename=args.filename,
        output_filename=output_filename,
        max_line_length=args.line_length,
    )
    processor.process()
    processor.write_to_output_file()

    logger.info(f"Lyrics processing complete, lyrics written to output file: {output_filename}")


if __name__ == "__main__":
    main()
