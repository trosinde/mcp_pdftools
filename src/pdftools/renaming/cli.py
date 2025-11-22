#!/usr/bin/env python3
"""
CLI for Invoice PDF Renaming

This module provides a command-line interface for renaming invoice PDFs
based on extracted data (invoice number, date, vendor).
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional
import json

from .core import rename_invoice, batch_rename
from .models import RenameConfig
from .validators import InvalidTemplateError, InvalidPatternError


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Rename invoice PDFs based on extracted data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Rename single invoice with default template
  pdfrename -f invoice.pdf

  # Custom template
  pdfrename -f invoice.pdf -t "{date}_{vendor}_{invoice_nr}.pdf"

  # Batch processing with dry-run
  pdfrename -f invoices/*.pdf -d

  # Custom patterns from JSON file
  pdfrename -f invoice.pdf -p patterns.json -o renamed/

  # Verbose output
  pdfrename -f invoice.pdf --verbose

Template placeholders:
  {vendor}      - Vendor/supplier name
  {invoice_nr}  - Invoice number
  {date}        - Full date (YYYY-MM-DD)
  {year}        - Year only
  {month}       - Month only
  {day}         - Day only
        """
    )

    parser.add_argument(
        '-f', '--files',
        required=True,
        help='PDF file(s) to rename (supports wildcards)'
    )

    parser.add_argument(
        '-t', '--template',
        default='{vendor}_{invoice_nr}_{date}.pdf',
        help='Naming template (default: {vendor}_{invoice_nr}_{date}.pdf)'
    )

    parser.add_argument(
        '-p', '--patterns',
        help='Path to custom patterns JSON file'
    )

    parser.add_argument(
        '-o', '--output-dir',
        help='Output directory (default: same as input)'
    )

    parser.add_argument(
        '-d', '--dry-run',
        action='store_true',
        help='Simulate rename without actually renaming files'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--no-duplicates',
        action='store_true',
        help='Error on duplicate filenames instead of adding suffix'
    )

    return parser.parse_args(args)


def load_patterns_from_file(pattern_file: Path) -> dict:
    """
    Load custom patterns from JSON file.

    Args:
        pattern_file: Path to JSON file

    Returns:
        Dictionary of patterns

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If JSON is invalid
    """
    if not pattern_file.exists():
        raise FileNotFoundError(f"Pattern file not found: {pattern_file}")

    with open(pattern_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def expand_file_patterns(file_pattern: str) -> List[Path]:
    """
    Expand file pattern to list of paths.

    Args:
        file_pattern: File pattern (may include wildcards)

    Returns:
        List of matching file paths

    Example:
        >>> expand_file_patterns("*.pdf")
        [Path("file1.pdf"), Path("file2.pdf")]
    """
    from glob import glob

    # Expand wildcards
    expanded = glob(file_pattern, recursive=True)

    # Convert to Path objects and filter for PDFs
    paths = [Path(p) for p in expanded if p.lower().endswith('.pdf')]

    return paths


def print_summary(results: List) -> None:
    """
    Print summary of batch rename operation.

    Args:
        results: List of RenameResult objects
    """
    total = len(results)
    successful = sum(1 for r in results if r.success)
    failed = total - successful

    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  Total files:      {total}")
    print(f"  Successful:       {successful}")
    print(f"  Failed:           {failed}")
    print(f"{'='*60}\n")

    if failed > 0:
        print("Failed files:")
        for result in results:
            if not result.success:
                print(f"  {result.old_name}: {result.message}")


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for CLI.

    Args:
        argv: Optional arguments (for testing)

    Returns:
        Exit code (0 for success, 1 for error)
    """
    args = parse_args(argv)

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format='%(levelname)s: %(message)s'
    )

    # Expand file patterns
    try:
        input_paths = expand_file_patterns(args.files)

        if not input_paths:
            print(f"Error: No PDF files found matching pattern: {args.files}")
            return 1

    except Exception as e:
        print(f"Error: Failed to expand file pattern: {e}")
        return 1

    # Load custom patterns if specified
    custom_patterns = None
    if args.patterns:
        try:
            pattern_file = Path(args.patterns)
            custom_patterns = load_patterns_from_file(pattern_file)
            if args.verbose:
                print(f"Loaded custom patterns from: {pattern_file}")
        except Exception as e:
            print(f"Error: Failed to load custom patterns: {e}")
            return 1

    # Prepare config
    config = RenameConfig(
        handle_duplicates=not args.no_duplicates,
        verbose=args.verbose
    )

    # Prepare output directory
    output_dir = Path(args.output_dir) if args.output_dir else None

    # Process files
    try:
        if len(input_paths) == 1:
            # Single file
            result = rename_invoice(
                input_path=input_paths[0],
                template=args.template,
                custom_patterns=custom_patterns,
                output_dir=output_dir,
                dry_run=args.dry_run,
                config=config
            )
            results = [result]

            if not args.verbose:
                if result.success:
                    print(f"{result.old_name} -> {result.new_name}")
                else:
                    print(f"Error: {result.message}")

        else:
            # Batch processing
            print(f"Processing {len(input_paths)} files...")

            results = batch_rename(
                input_paths=input_paths,
                template=args.template,
                custom_patterns=custom_patterns,
                output_dir=output_dir,
                dry_run=args.dry_run,
                config=config
            )

            if not args.verbose:
                # Print simple list of renames
                for result in results:
                    if result.success:
                        print(f"{result.old_name} -> {result.new_name}")
                    else:
                        print(f"{result.old_name}: ERROR - {result.message}")

            print_summary(results)

        # Determine exit code
        failed = sum(1 for r in results if not r.success)
        return 1 if failed > 0 else 0

    except InvalidTemplateError as e:
        print(f"Error: Invalid template: {e}")
        return 1

    except InvalidPatternError as e:
        print(f"Error: Invalid pattern: {e}")
        return 1

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 1

    except Exception as e:
        print(f"Error: Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
