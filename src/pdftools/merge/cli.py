"""
CLI interface for PDF merge
"""

import argparse
import sys
from pathlib import Path
import logging

from .core import merge_pdfs
from .models import MergeConfig
from ..core.utils import setup_logger


def main():
    """
    Main entry point for pdftools-merge CLI

    Exit codes:
        0: Success
        1: Error (file not found, invalid input, etc.)
        2: Partial success (some files skipped)
    """
    parser = argparse.ArgumentParser(
        prog='pdftools-merge',
        description='Merge multiple PDF files into a single document',
        epilog='Example: pdftools-merge -f "file1.pdf,file2.pdf" -o merged.pdf'
    )

    parser.add_argument(
        '-f', '--files',
        type=str,
        required=True,
        help='Comma-separated list of PDF files to merge (minimum 2)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output path for merged PDF (default: merged.pdf in directory of first file)'
    )

    parser.add_argument(
        '--no-bookmarks',
        action='store_true',
        help='Do not preserve bookmarks from source PDFs'
    )

    parser.add_argument(
        '--skip-on-error',
        action='store_true',
        help='Skip corrupted files instead of aborting'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logger('pdftools.merge', level=log_level)
    logger = logging.getLogger('pdftools.merge')

    # Parse file list
    file_paths = [
        Path(f.strip())
        for f in args.files.split(',')
        if f.strip()
    ]

    if not file_paths:
        logger.error("No files specified")
        sys.exit(1)

    # Parse output path
    output_path = Path(args.output) if args.output else None

    # Create config
    config = MergeConfig(
        keep_bookmarks=not args.no_bookmarks,
        skip_on_error=args.skip_on_error,
        verbose=args.verbose
    )

    # Perform merge
    try:
        result = merge_pdfs(
            files=file_paths,
            output_path=output_path,
            config=config
        )

        # Print result
        if result.success:
            print(f"✓ {result.message}")
            print(f"  Output: {result.output_path}")
            print(f"  Pages: {result.pages_merged}")
            if 'elapsed_time' in result.metadata:
                print(f"  Time: {result.metadata['elapsed_time']:.2f}s")
            sys.exit(0)

        elif result.status == 'partial':
            print(f"⚠ {result.message}")
            print(f"  Output: {result.output_path}")
            print(f"  Pages: {result.pages_merged}")
            print(f"  Skipped: {len(result.skipped_files)} files")
            if args.verbose and result.skipped_files:
                for skipped in result.skipped_files:
                    print(f"    - {skipped}")
            sys.exit(2)

        else:
            print(f"✗ Error: {result.message}", file=sys.stderr)
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
