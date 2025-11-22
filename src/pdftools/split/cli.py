#!/usr/bin/env python3
"""
CLI for PDF Split - pdfsplit command.
"""

import argparse
import sys
from pathlib import Path

from pdftools.cli.common import (
    print_success,
    print_error,
    print_warning,
    setup_logging
)
from pdftools.split import split_pdf, SplitMode, parse_ranges
from pdftools.core.exceptions import PDFToolsError


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for pdfsplit CLI."""
    parser = argparse.ArgumentParser(
        prog='pdfsplit',
        description='Split PDF files into multiple parts',
        epilog='Examples:\n'
               '  pdfsplit -i document.pdf                    # Split into individual pages\n'
               '  pdfsplit -i document.pdf -o ./output/       # Specify output directory\n'
               '  pdfsplit -i doc.pdf -m ranges -r "1-5,10-15" # Split by ranges\n'
               '  pdfsplit -i doc.pdf -m parts -p 5           # Split into 5 equal parts\n'
               '  pdfsplit -i doc.pdf --pages 1,5,10,15       # Extract specific pages',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        '-i', '--input',
        type=str,
        required=True,
        help='Input PDF file path'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default='.',
        help='Output directory for split files (default: current directory)'
    )

    parser.add_argument(
        '-m', '--mode',
        type=str,
        choices=['pages', 'ranges', 'parts', 'specific'],
        default='pages',
        help='Split mode: pages (default), ranges, parts, or specific'
    )

    # Mode-specific arguments
    parser.add_argument(
        '-r', '--ranges',
        type=str,
        help='Page ranges for RANGES mode (e.g., "1-5,10-15,20-25")'
    )

    parser.add_argument(
        '-p', '--parts',
        type=int,
        help='Number of parts for PARTS mode (e.g., 5)'
    )

    parser.add_argument(
        '--pages',
        type=str,
        help='Specific pages for SPECIFIC mode (e.g., "1,5,10,15")'
    )

    parser.add_argument(
        '--prefix',
        type=str,
        help='Prefix for output files (default: input filename)'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='pdfsplit 1.0.0'
    )

    return parser


def main():
    """Main entry point for pdfsplit CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(verbose=args.verbose)

    # Convert mode string to SplitMode enum
    mode_map = {
        'pages': SplitMode.PAGES,
        'ranges': SplitMode.RANGES,
        'parts': SplitMode.PARTS,
        'specific': SplitMode.SPECIFIC_PAGES
    }
    mode = mode_map[args.mode]

    # Parse mode-specific parameters
    ranges = None
    pages = None
    num_parts = None

    try:
        if mode == SplitMode.RANGES:
            if not args.ranges:
                print_error("--ranges required for RANGES mode")
                sys.exit(1)
            ranges = parse_ranges(args.ranges)

        elif mode == SplitMode.PARTS:
            if not args.parts:
                print_error("--parts required for PARTS mode")
                sys.exit(1)
            num_parts = args.parts

        elif mode == SplitMode.SPECIFIC_PAGES:
            if not args.pages:
                print_error("--pages required for SPECIFIC mode")
                sys.exit(1)
            # Parse comma-separated page numbers
            try:
                pages = [int(p.strip()) for p in args.pages.split(',')]
            except ValueError as e:
                print_error(f"Invalid page numbers: {args.pages}")
                sys.exit(1)

    except PDFToolsError as e:
        print_error(str(e))
        sys.exit(1)

    # Perform split
    try:
        result = split_pdf(
            input_path=args.input,
            output_dir=args.output_dir,
            mode=mode,
            ranges=ranges,
            pages=pages,
            num_parts=num_parts,
            prefix=args.prefix,
            verbose=args.verbose
        )

        if result.success:
            print_success(result.message or f"Split successful: {result.num_files} files created")

            if args.verbose:
                print(f"\nOutput files:")
                for output_file in result.output_files:
                    print(f"  - {output_file}")

            sys.exit(0)
        else:
            print_error(result.message or "Split failed")
            sys.exit(1)

    except PDFToolsError as e:
        print_error(str(e))
        sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
