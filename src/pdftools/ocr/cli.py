#!/usr/bin/env python3
"""
CLI for OCR Processing
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List

from pdftools.ocr.core import perform_ocr
from pdftools.ocr.models import OCRLanguage, OutputMode, OCRConfig
from pdftools.core.exceptions import (
    PDFToolsError,
    TesseractNotFoundError,
    LanguageNotAvailableError,
)

logger = logging.getLogger(__name__)


def parse_pages(pages_str: str) -> List[int]:
    """
    Parse page range string into list of page numbers.

    Args:
        pages_str: Page range string (e.g., "1-5,7,9-12")

    Returns:
        List[int]: List of page numbers

    Examples:
        >>> parse_pages("1-3,5")
        [1, 2, 3, 5]
        >>> parse_pages("1,3,5-7")
        [1, 3, 5, 6, 7]
    """
    pages = []
    parts = pages_str.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            # Range (e.g., "1-5")
            start, end = part.split('-')
            pages.extend(range(int(start), int(end) + 1))
        else:
            # Single page
            pages.append(int(part))

    return sorted(set(pages))


def setup_logging(verbose: bool) -> None:
    """
    Setup logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def main():
    """Main entry point for OCR CLI"""
    parser = argparse.ArgumentParser(
        description='Perform OCR on scanned PDF documents',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (German language, TXT output)
  %(prog)s -f scan.pdf

  # Multiple languages, PDF output
  %(prog)s -f document.pdf -l deu+eng --output-mode pdf -o searchable.pdf

  # Specific pages only
  %(prog)s -f contract.pdf --pages "1-5,10"

  # JSON output for processing
  %(prog)s -f receipt.pdf --output-mode json -o result.json

Supported languages:
  deu (German), eng (English), fra (French), ita (Italian), spa (Spanish)
  Use '+' to combine multiple languages: deu+eng

Note:
  This tool requires Tesseract OCR to be installed.
  Install: apt-get install tesseract-ocr (Linux)
          brew install tesseract (macOS)
          Or use Docker: docker-compose up tesseract
        """
    )

    parser.add_argument(
        '-f', '--file',
        type=Path,
        required=True,
        help='Input PDF file path'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output file path (default: {filename}_ocr.{ext})'
    )

    parser.add_argument(
        '-l', '--language',
        type=str,
        default='deu',
        help='OCR language(s) - single or multiple with + (default: deu)'
    )

    parser.add_argument(
        '--output-mode',
        type=str,
        choices=['txt', 'pdf', 'json'],
        default='txt',
        help='Output format (default: txt)'
    )

    parser.add_argument(
        '--pages',
        type=str,
        help='Page range (e.g., "1-5,7,9-12") - default: all pages'
    )

    parser.add_argument(
        '--dpi',
        type=int,
        default=300,
        help='DPI for PDF to image conversion (default: 300)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    try:
        # Parse language(s)
        if '+' in args.language:
            languages = args.language.split('+')
        else:
            languages = args.language

        # Parse pages if specified
        pages = None
        if args.pages:
            pages = parse_pages(args.pages)
            logger.info(f"Processing pages: {pages}")

        # Parse output mode
        output_mode = OutputMode(args.output_mode)

        # Create config
        config = OCRConfig(
            pages=pages,
            dpi=args.dpi,
            verbose=args.verbose
        )

        # Perform OCR
        logger.info(f"Starting OCR processing: {args.file}")
        result = perform_ocr(
            input_path=args.file,
            output_path=args.output,
            language=languages,
            output_mode=output_mode,
            config=config
        )

        # Display result
        if result.success:
            print(f"\n{'='*60}")
            print(f"OCR Processing Completed Successfully")
            print(f"{'='*60}")
            print(f"Output file:      {result.output_path}")
            print(f"Pages processed:  {result.pages_processed}/{result.total_pages}")
            print(f"Average confidence: {result.metadata.get('avg_confidence', 0):.2%}")
            print(f"Total words:      {result.metadata.get('total_words', 0)}")
            print(f"Processing time:  {result.metadata.get('processing_time_seconds', 0):.2f}s")
            print(f"{'='*60}\n")
            sys.exit(0)
        else:
            print(f"\nERROR: {result.message}", file=sys.stderr)
            sys.exit(1)

    except TesseractNotFoundError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        print("\nTesseract OCR is not installed.", file=sys.stderr)
        print("\nInstallation instructions:", file=sys.stderr)
        print("  Linux:   sudo apt-get install tesseract-ocr", file=sys.stderr)
        print("  macOS:   brew install tesseract", file=sys.stderr)
        print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki", file=sys.stderr)
        print("\nOr use Docker: docker-compose up tesseract", file=sys.stderr)
        sys.exit(2)

    except LanguageNotAvailableError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        print(f"\nTo install language data:", file=sys.stderr)
        print(f"  Linux:   sudo apt-get install tesseract-ocr-{e.language}", file=sys.stderr)
        print(f"  macOS:   brew install tesseract-lang", file=sys.stderr)
        sys.exit(3)

    except PDFToolsError as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)

    except Exception as e:
        print(f"\nUNEXPECTED ERROR: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
