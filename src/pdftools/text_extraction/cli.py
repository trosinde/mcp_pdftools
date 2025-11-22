#!/usr/bin/env python3
"""CLI interface for PDF text extraction."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from pdftools.core.exceptions import PDFToolsError
from pdftools.cli.common import setup_logging

from .core import extract_text
from .models import ExtractionMode, OutputFormat


def parse_pages(pages_str: str) -> list[int]:
    """
    Parse page specification string into list of page numbers.

    Args:
        pages_str: Pages specification (e.g., "1,3,5-10")

    Returns:
        List of page numbers (1-based)

    Raises:
        ValueError: If page specification is invalid
    """
    pages = []
    for part in pages_str.split(','):
        part = part.strip()
        if '-' in part:
            # Range like "5-10"
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            # Single page
            pages.append(int(part))
    return sorted(set(pages))  # Remove duplicates and sort


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for CLI."""
    parser = argparse.ArgumentParser(
        prog='pdfgettxt',
        description='Extract text from PDF files',
        epilog='Examples:\n'
               '  pdfgettxt -i document.pdf\n'
               '  pdfgettxt -i doc.pdf -o output.txt\n'
               '  pdfgettxt -i doc.pdf -m layout -o output.txt\n'
               '  pdfgettxt -i doc.pdf -m per_page -o ./pages/\n'
               '  pdfgettxt -i doc.pdf -f json -o output.json\n'
               '  pdfgettxt -i doc.pdf -p "1,5,10-15"',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        '-i', '--input',
        required=True,
        type=Path,
        help='Input PDF file',
        metavar='PATH'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file or directory (default: stdout)',
        metavar='PATH'
    )

    parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['simple', 'layout', 'per_page', 'structured'],
        default='simple',
        help='Extraction mode (default: simple)'
    )

    parser.add_argument(
        '-f', '--format',
        type=str,
        choices=['txt', 'json', 'markdown'],
        default='txt',
        help='Output format (default: txt)'
    )

    parser.add_argument(
        '-p', '--pages',
        type=str,
        help='Specific pages to extract (e.g., "1,3,5-10")',
        metavar='PAGES'
    )

    parser.add_argument(
        '-e', '--encoding',
        type=str,
        default='utf-8',
        help='Output encoding (default: utf-8)',
        metavar='ENC'
    )

    parser.add_argument(
        '--include-metadata',
        action='store_true',
        help='Include PDF metadata in output'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed progress'
    )

    return parser


def main() -> int:
    """
    Main entry point for pdfgettxt CLI.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    try:
        # Parse pages if specified
        pages = None
        if args.pages:
            try:
                pages = parse_pages(args.pages)
            except ValueError as e:
                print(f"✗ Error: Invalid page specification: {args.pages}", file=sys.stderr)
                return 1

        # Convert mode and format to enums
        mode = ExtractionMode(args.mode)
        format = OutputFormat(args.format)

        # Extract text
        result = extract_text(
            input_path=args.input,
            output_path=args.output,
            mode=mode,
            format=format,
            pages=pages,
            encoding=args.encoding,
            include_metadata=args.include_metadata,
            verbose=args.verbose
        )

        # Output results
        if result.status == "success":
            if result.message:
                print(f"✓ {result.message}")
            elif not args.output:
                # Print to stdout if no output file specified
                if format == OutputFormat.JSON or format == OutputFormat.MARKDOWN:
                    from .formatters import get_formatter
                    formatter = get_formatter(format)
                    print(formatter.format(result))
                else:
                    print(result.text)

            if args.verbose:
                print(f"Characters extracted: {result.char_count}")
                if result.pages:
                    print(f"Pages processed: {len(result.pages)}")

            return 0
        else:
            print(f"✗ Error: {result.message}", file=sys.stderr)
            return 1

    except PDFToolsError as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
