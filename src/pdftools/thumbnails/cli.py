#!/usr/bin/env python3
"""
CLI for PDF Thumbnail Generation

Generates thumbnail images from PDF pages with configurable sizes and formats.
"""

import sys
import argparse
import logging
from pathlib import Path

from .core import generate_thumbnails
from .models import ThumbnailSize, ThumbnailFormat

logger = logging.getLogger('pdftools.thumbnails')


def parse_args(args=None):
    """
    Parse command line arguments.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate thumbnail images from PDF pages',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage (all pages, medium size, PNG)
  pdfthumbnails -f document.pdf

  # Custom size and format
  pdfthumbnails -f report.pdf -s large -F jpg -o ./previews

  # Specific pages only
  pdfthumbnails -f manual.pdf -p "1,5,10-15" -s small

  # Custom dimensions
  pdfthumbnails -f catalog.pdf -s 800x600 -F jpg -q 95

  # Verbose output
  pdfthumbnails -f book.pdf --verbose

Thumbnail Sizes:
  small   : 150x150 pixels
  medium  : 300x300 pixels (default)
  large   : 600x600 pixels
  WxH     : Custom size (e.g., 800x600)

Formats:
  png     : PNG format, lossless (default)
  jpg     : JPEG format, lossy with quality control

Note: Aspect ratio is always preserved. Images are scaled to fit within
      the specified size without cropping.
        """
    )

    # Required arguments
    parser.add_argument(
        '-f', '--file',
        type=str,
        required=True,
        metavar='PDF',
        help='Path to input PDF file'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output-dir',
        type=str,
        default=None,
        metavar='DIR',
        help='Output directory for thumbnails (default: ./thumbnails)'
    )

    parser.add_argument(
        '-s', '--size',
        type=str,
        default='medium',
        metavar='SIZE',
        help='Thumbnail size: small|medium|large|WxH (default: medium)'
    )

    parser.add_argument(
        '-F', '--format',
        type=str,
        choices=['png', 'jpg', 'jpeg'],
        default='png',
        metavar='FMT',
        help='Output format: png|jpg (default: png)'
    )

    parser.add_argument(
        '-p', '--pages',
        type=str,
        default=None,
        metavar='PAGES',
        help='Pages to process: "1,3,5" or "1-10" or "1,3,5-10" (default: all)'
    )

    parser.add_argument(
        '-q', '--quality',
        type=int,
        default=85,
        metavar='N',
        help='JPEG quality 1-100 (default: 85, ignored for PNG)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='pdfthumbnails 1.0.0'
    )

    return parser.parse_args(args)


def main(args=None):
    """
    Main entry point for CLI.

    Args:
        args: Optional list of arguments (for testing)

    Returns:
        int: Exit code (0 = success, 1 = error)
    """
    try:
        # Parse arguments
        parsed_args = parse_args(args)

        # Setup logging
        if parsed_args.verbose:
            logging.basicConfig(
                level=logging.INFO,
                format='%(levelname)s: %(message)s'
            )
        else:
            logging.basicConfig(
                level=logging.WARNING,
                format='%(levelname)s: %(message)s'
            )

        # Parse size argument
        size_arg = parsed_args.size.lower()
        if size_arg == 'small':
            size = ThumbnailSize.SMALL
        elif size_arg == 'medium':
            size = ThumbnailSize.MEDIUM
        elif size_arg == 'large':
            size = ThumbnailSize.LARGE
        else:
            # Custom size (WxH format)
            size = size_arg

        # Parse format argument
        format_arg = parsed_args.format.lower()
        if format_arg in ('jpg', 'jpeg'):
            format_enum = ThumbnailFormat.JPG
        else:
            format_enum = ThumbnailFormat.PNG

        # Show configuration
        print(f"PDF Thumbnail Generator")
        print(f"=" * 50)
        print(f"Input PDF:     {parsed_args.file}")
        print(f"Output dir:    {parsed_args.output_dir or './thumbnails'}")
        print(f"Size:          {parsed_args.size}")
        print(f"Format:        {format_enum.value.upper()}")
        if format_enum == ThumbnailFormat.JPG:
            print(f"Quality:       {parsed_args.quality}")
        if parsed_args.pages:
            print(f"Pages:         {parsed_args.pages}")
        else:
            print(f"Pages:         All")
        print(f"=" * 50)
        print()

        # Generate thumbnails
        result = generate_thumbnails(
            input_path=parsed_args.file,
            output_dir=parsed_args.output_dir,
            size=size,
            format=format_enum,
            pages=parsed_args.pages,
            quality=parsed_args.quality,
            verbose=parsed_args.verbose
        )

        # Display results
        if result.success:
            print(f"✓ Success: {result.message}")
            print(f"\nCreated {result.thumbnails_created} thumbnails:")
            for path in result.thumbnail_paths:
                print(f"  - {path}")
            print()
            return 0

        elif result.partial_success:
            print(f"⚠ Partial Success: {result.message}")
            print(f"\nCreated {result.thumbnails_created} thumbnails:")
            for path in result.thumbnail_paths:
                print(f"  - {path}")
            if result.skipped_pages:
                print(f"\nSkipped pages: {result.skipped_pages}")
            print()
            return 0

        else:
            print(f"✗ Error: {result.message}", file=sys.stderr)
            return 1

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        if parsed_args.verbose if 'parsed_args' in locals() else False:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
