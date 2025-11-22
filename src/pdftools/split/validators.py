"""
Input validation for PDF Split module.
"""

import re
from pathlib import Path
from typing import Optional

from pdftools.core.exceptions import (
    PDFNotFoundError,
    ValidationError,
    InvalidPathError,
    InvalidRangeError
)


def validate_pdf_path(path: Path) -> None:
    """
    Validate that PDF path exists and is readable.

    Args:
        path: Path to PDF file

    Raises:
        InvalidPathError: If path contains invalid characters or path traversal
        PDFNotFoundError: If file does not exist
        ValidationError: If file is not a PDF
    """
    # Convert to Path if string
    if isinstance(path, str):
        path = Path(path)

    # Check for path traversal attempts
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(f"Invalid path: {path}") from e

    # Check if path contains ".."
    if ".." in str(path):
        raise InvalidPathError("Path traversal not allowed")

    # Check file exists
    if not resolved.exists():
        raise PDFNotFoundError(f"PDF file not found: {path}")

    # Check it's a file (not directory)
    if not resolved.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    # Check file extension (basic check)
    if resolved.suffix.lower() != '.pdf':
        raise ValidationError(f"File is not a PDF: {path} (expected .pdf extension)")


def validate_output_dir(directory: Path, create: bool = True) -> None:
    """
    Validate output directory exists and is writable.

    Args:
        directory: Path to output directory
        create: If True, create directory if it doesn't exist

    Raises:
        InvalidPathError: If path is invalid
        PermissionError: If directory is not writable
    """
    # Convert to Path if string
    if isinstance(directory, str):
        directory = Path(directory)

    # Resolve path
    try:
        resolved = directory.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(f"Invalid directory path: {directory}") from e

    # Create directory if needed
    if not resolved.exists():
        if create:
            try:
                resolved.mkdir(parents=True, exist_ok=True)
            except PermissionError as e:
                raise PermissionError(
                    f"Cannot create directory {directory}: Permission denied"
                ) from e
            except OSError as e:
                raise ValidationError(
                    f"Cannot create directory {directory}: {e}"
                ) from e
        else:
            raise ValidationError(f"Output directory does not exist: {directory}")

    # Check it's a directory
    if not resolved.is_dir():
        raise ValidationError(f"Path is not a directory: {directory}")

    # Check it's writable
    if not os.access(resolved, os.W_OK):
        raise PermissionError(f"Directory is not writable: {directory}")


def parse_ranges(range_string: str) -> list[tuple[int, int]]:
    """
    Parse range string like "1-5,10-15,20-25" into list of tuples.

    Args:
        range_string: Comma-separated ranges (e.g., "1-5,10-15")

    Returns:
        List of (start, end) tuples (1-indexed, inclusive)

    Raises:
        InvalidRangeError: If range_string is invalid

    Example:
        >>> parse_ranges("1-5,10-15")
        [(1, 5), (10, 15)]

        >>> parse_ranges("1-3,5,7-9")
        [(1, 3), (5, 5), (7, 9)]
    """
    if not range_string or not range_string.strip():
        raise InvalidRangeError("Range string is empty")

    ranges = []
    parts = range_string.split(',')

    for part in parts:
        part = part.strip()

        # Check for range (e.g., "1-5")
        if '-' in part:
            match = re.match(r'^(\d+)-(\d+)$', part)
            if not match:
                raise InvalidRangeError(
                    f"Invalid range format: '{part}' (expected format: '1-5')"
                )

            start = int(match.group(1))
            end = int(match.group(2))

            if start < 1:
                raise InvalidRangeError(
                    f"Invalid range: {part} (page numbers must be >= 1)"
                )

            if start > end:
                raise InvalidRangeError(
                    f"Invalid range: {part} (start must be <= end)"
                )

            ranges.append((start, end))

        # Single page (e.g., "5")
        else:
            match = re.match(r'^(\d+)$', part)
            if not match:
                raise InvalidRangeError(
                    f"Invalid page number: '{part}' (expected integer)"
                )

            page = int(match.group(1))

            if page < 1:
                raise InvalidRangeError(
                    f"Invalid page number: {page} (must be >= 1)"
                )

            # Single page as range (start, end)
            ranges.append((page, page))

    return ranges


def validate_ranges(
    ranges: list[tuple[int, int]],
    total_pages: int,
    allow_overlap: bool = True
) -> None:
    """
    Validate that page ranges are valid for given PDF.

    Args:
        ranges: List of (start, end) tuples (1-indexed)
        total_pages: Total number of pages in PDF
        allow_overlap: If False, check for overlapping ranges

    Raises:
        InvalidRangeError: If ranges are invalid
    """
    if not ranges:
        raise InvalidRangeError("Ranges list is empty")

    seen_pages = set()

    for start, end in ranges:
        # Check bounds
        if start < 1 or end > total_pages:
            raise InvalidRangeError(
                f"Range ({start}, {end}) out of bounds for PDF with {total_pages} pages"
            )

        if start > end:
            raise InvalidRangeError(
                f"Invalid range ({start}, {end}): start must be <= end"
            )

        # Check for overlap if not allowed
        if not allow_overlap:
            range_pages = set(range(start, end + 1))
            overlap = seen_pages & range_pages

            if overlap:
                raise InvalidRangeError(
                    f"Overlapping ranges detected: pages {sorted(overlap)}"
                )

            seen_pages.update(range_pages)


def validate_pages(
    pages: list[int],
    total_pages: int
) -> None:
    """
    Validate that page numbers are valid for given PDF.

    Args:
        pages: List of page numbers (1-indexed)
        total_pages: Total number of pages in PDF

    Raises:
        InvalidRangeError: If page numbers are invalid
    """
    if not pages:
        raise InvalidRangeError("Pages list is empty")

    for page in pages:
        if page < 1:
            raise InvalidRangeError(
                f"Invalid page number: {page} (must be >= 1)"
            )

        if page > total_pages:
            raise InvalidRangeError(
                f"Page {page} does not exist (PDF has {total_pages} pages)"
            )


# Import os for file permission checks
import os
