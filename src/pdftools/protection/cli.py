#!/usr/bin/env python3
"""
CLI for PDF Protection.

This module provides a command-line interface for protecting PDF files
with passwords and permissions.
"""

import sys
import logging
import argparse
from pathlib import Path
from typing import List, Optional

from .core import protect_pdf
from .models import PermissionLevel


def setup_logging(verbose: bool = False) -> None:
    """
    Configure logging for CLI.

    Args:
        verbose: Enable verbose (DEBUG) logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def parse_permissions(permissions_str: Optional[str]) -> Optional[List[PermissionLevel]]:
    """
    Parse comma-separated permissions string.

    Args:
        permissions_str: Comma-separated permissions (e.g., "print,copy")

    Returns:
        List of PermissionLevel objects, or None if empty

    Raises:
        ValueError: If permission is invalid
    """
    if not permissions_str:
        return None

    permissions = []
    for perm_str in permissions_str.split(','):
        perm_str = perm_str.strip()
        if perm_str:
            try:
                perm = PermissionLevel.from_string(perm_str)
                permissions.append(perm)
            except ValueError as e:
                raise ValueError(str(e)) from e

    return permissions if permissions else None


def create_parser() -> argparse.ArgumentParser:
    """
    Create argument parser for CLI.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog='pdfprotect',
        description='Protect PDF files with password encryption and permissions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Protect with user password only
  pdfprotect -i document.pdf -u secret123

  # Protect with user and owner passwords
  pdfprotect -i contract.pdf -u open123 -w admin456

  # Allow printing and copying
  pdfprotect -i report.pdf -u read123 -p print,copy

  # Custom output path
  pdfprotect -i invoice.pdf -o secure_invoice.pdf -u pass123

  # Verbose output
  pdfprotect -i document.pdf -u secret --verbose

Valid permissions: print, copy, modify, annotate
        """
    )

    # Required arguments
    parser.add_argument(
        '-i', '--input',
        type=Path,
        required=True,
        help='Input PDF file path'
    )

    # Optional arguments
    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output PDF file path (default: {input}_protected.pdf)'
    )

    parser.add_argument(
        '-u', '--user-password',
        type=str,
        help='Password required to open the PDF'
    )

    parser.add_argument(
        '-w', '--owner-password',
        type=str,
        help='Password required to change permissions'
    )

    parser.add_argument(
        '-p', '--permissions',
        type=str,
        help='Comma-separated list of allowed permissions: print,copy,modify,annotate'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser


def main() -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 = success, 1 = error)
    """
    parser = create_parser()
    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        # Parse permissions
        permissions = parse_permissions(args.permissions)

        # Validate at least one password provided
        if not args.user_password and not args.owner_password:
            logger.error("At least one password (--user-password or --owner-password) must be provided")
            return 1

        # Display info (but NEVER log passwords!)
        logger.info(f"Input PDF: {args.input}")
        if args.output:
            logger.info(f"Output PDF: {args.output}")
        if permissions:
            perm_names = [p.value for p in permissions]
            logger.info(f"Permissions: {', '.join(perm_names)}")
        else:
            logger.info("Permissions: All denied (most restrictive)")

        # Protect PDF
        result = protect_pdf(
            input_path=args.input,
            output_path=args.output,
            user_password=args.user_password,
            owner_password=args.owner_password,
            permissions=permissions
        )

        # Display result
        if result.success:
            logger.info(f"Success: {result.message}")
            logger.info(f"Protected PDF created: {result.output_path}")
            return 0
        else:
            logger.error(f"Error: {result.message}")
            return 1

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1

    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        return 130  # Standard exit code for SIGINT

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=args.verbose)
        return 1


if __name__ == '__main__':
    sys.exit(main())
