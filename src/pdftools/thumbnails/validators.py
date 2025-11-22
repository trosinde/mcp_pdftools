"""
Input validation for thumbnail generation
"""

import re
from pathlib import Path
from typing import Union

from pdftools.core.exceptions import ValidationError
from .models import ThumbnailSize, ThumbnailFormat


def validate_pdf_path(pdf_path: Union[str, Path]) -> Path:
    """
    Validate PDF file path.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Path: Validated Path object

    Raises:
        ValidationError: If file doesn't exist or is not a PDF
    """
    path = Path(pdf_path)

    if not path.exists():
        raise ValidationError(f"PDF file not found: {path}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    if path.suffix.lower() != '.pdf':
        raise ValidationError(f"File is not a PDF: {path}")

    return path


def validate_output_dir(output_dir: Union[str, Path]) -> Path:
    """
    Validate output directory path.

    Args:
        output_dir: Path to output directory

    Returns:
        Path: Validated Path object

    Raises:
        ValidationError: If directory is not writable
    """
    path = Path(output_dir)

    # Create directory if it doesn't exist
    try:
        path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise ValidationError(f"Cannot create output directory: {path} (Permission denied)")
    except Exception as e:
        raise ValidationError(f"Cannot create output directory: {path} ({e})")

    # Check if directory is writable
    if not path.is_dir():
        raise ValidationError(f"Output path is not a directory: {path}")

    # Try to create a test file to verify write permissions
    test_file = path / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        raise ValidationError(f"Output directory is not writable: {path}")
    except Exception as e:
        raise ValidationError(f"Cannot write to output directory: {path} ({e})")

    return path


def validate_size(size: Union[ThumbnailSize, tuple[int, int], str]) -> tuple[int, int]:
    """
    Validate and parse thumbnail size specification.

    Args:
        size: Size specification (enum, tuple, or string like "800x600")

    Returns:
        tuple[int, int]: Validated (width, height) tuple

    Raises:
        ValidationError: If size specification is invalid

    Examples:
        >>> validate_size(ThumbnailSize.MEDIUM)
        (300, 300)
        >>> validate_size((800, 600))
        (800, 600)
        >>> validate_size("800x600")
        (800, 600)
    """
    # Handle ThumbnailSize enum
    if isinstance(size, ThumbnailSize):
        return size.value

    # Handle tuple
    if isinstance(size, tuple):
        if len(size) != 2:
            raise ValidationError(f"Size tuple must have exactly 2 elements, got: {len(size)}")

        width, height = size
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValidationError(f"Size dimensions must be integers, got: {size}")

        if width <= 0 or height <= 0:
            raise ValidationError(f"Size dimensions must be positive, got: {size}")

        if width > 10000 or height > 10000:
            raise ValidationError(f"Size dimensions too large (max 10000), got: {size}")

        return (width, height)

    # Handle string format "WxH"
    if isinstance(size, str):
        match = re.match(r'^(\d+)x(\d+)$', size, re.IGNORECASE)
        if not match:
            raise ValidationError(
                f"Invalid size format: '{size}'. Expected 'WIDTHxHEIGHT' (e.g., '800x600')"
            )

        width = int(match.group(1))
        height = int(match.group(2))

        if width <= 0 or height <= 0:
            raise ValidationError(f"Size dimensions must be positive, got: {size}")

        if width > 10000 or height > 10000:
            raise ValidationError(f"Size dimensions too large (max 10000), got: {size}")

        return (width, height)

    raise ValidationError(f"Invalid size type: {type(size)}. Expected ThumbnailSize, tuple, or str")


def validate_format(format_spec: Union[ThumbnailFormat, str]) -> ThumbnailFormat:
    """
    Validate and parse image format specification.

    Args:
        format_spec: Format specification (enum or string)

    Returns:
        ThumbnailFormat: Validated format enum

    Raises:
        ValidationError: If format is invalid

    Examples:
        >>> validate_format("png")
        ThumbnailFormat.PNG
        >>> validate_format("jpg")
        ThumbnailFormat.JPG
    """
    # Handle ThumbnailFormat enum
    if isinstance(format_spec, ThumbnailFormat):
        return format_spec

    # Handle string
    if isinstance(format_spec, str):
        format_lower = format_spec.lower()

        if format_lower == "png":
            return ThumbnailFormat.PNG
        elif format_lower in ("jpg", "jpeg"):
            return ThumbnailFormat.JPG
        else:
            raise ValidationError(
                f"Invalid format: '{format_spec}'. Supported formats: png, jpg"
            )

    raise ValidationError(f"Invalid format type: {type(format_spec)}. Expected ThumbnailFormat or str")


def validate_quality(quality: int) -> int:
    """
    Validate JPEG quality setting.

    Args:
        quality: Quality factor (1-100)

    Returns:
        int: Validated quality value

    Raises:
        ValidationError: If quality is out of range

    Examples:
        >>> validate_quality(85)
        85
        >>> validate_quality(150)  # doctest: +SKIP
        ValidationError: Quality must be between 1 and 100
    """
    if not isinstance(quality, int):
        raise ValidationError(f"Quality must be an integer, got: {type(quality)}")

    if not 1 <= quality <= 100:
        raise ValidationError(f"Quality must be between 1 and 100, got: {quality}")

    return quality


def validate_pages(pages: Union[list[int], str, None], total_pages: int) -> list[int]:
    """
    Validate and parse page specification.

    Args:
        pages: Page specification (list, string like "1,3,5-10", or None for all)
        total_pages: Total number of pages in PDF

    Returns:
        list[int]: List of valid page numbers (1-indexed)

    Raises:
        ValidationError: If page specification is invalid

    Examples:
        >>> validate_pages([1, 2, 3], 10)
        [1, 2, 3]
        >>> validate_pages("1,3,5-7", 10)
        [1, 3, 5, 6, 7]
        >>> validate_pages(None, 10)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    """
    # None means all pages
    if pages is None:
        return list(range(1, total_pages + 1))

    # Handle list
    if isinstance(pages, list):
        validated = []
        for page in pages:
            if not isinstance(page, int):
                raise ValidationError(f"Page number must be integer, got: {type(page)}")

            if page < 1 or page > total_pages:
                raise ValidationError(
                    f"Page {page} out of range (PDF has {total_pages} pages)"
                )

            validated.append(page)

        return sorted(set(validated))  # Remove duplicates and sort

    # Handle string format "1,3,5-10"
    if isinstance(pages, str):
        page_list = []

        for part in pages.split(','):
            part = part.strip()

            # Range: "5-10"
            if '-' in part:
                try:
                    start, end = part.split('-', 1)
                    start = int(start.strip())
                    end = int(end.strip())

                    if start < 1 or end > total_pages:
                        raise ValidationError(
                            f"Page range {start}-{end} out of bounds (PDF has {total_pages} pages)"
                        )

                    if start > end:
                        raise ValidationError(f"Invalid page range: {start}-{end} (start > end)")

                    page_list.extend(range(start, end + 1))

                except ValueError:
                    raise ValidationError(f"Invalid page range format: '{part}'")

            # Single page: "5"
            else:
                try:
                    page = int(part)

                    if page < 1 or page > total_pages:
                        raise ValidationError(
                            f"Page {page} out of range (PDF has {total_pages} pages)"
                        )

                    page_list.append(page)

                except ValueError:
                    raise ValidationError(f"Invalid page number: '{part}'")

        if not page_list:
            raise ValidationError("No valid pages specified")

        return sorted(set(page_list))  # Remove duplicates and sort

    raise ValidationError(f"Invalid pages type: {type(pages)}. Expected list, str, or None")
