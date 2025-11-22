"""Input validation for text extraction."""

from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

from pdftools.core.exceptions import ValidationError
from pdftools.core.validators import validate_pdf_path


def validate_pages(
    pages: Optional[list[int]],
    total_pages: int
) -> None:
    """
    Validate that page numbers are valid for given PDF.

    Args:
        pages: List of page numbers (1-based)
        total_pages: Total number of pages in PDF

    Raises:
        ValidationError: If page numbers are invalid
    """
    if pages is None:
        return

    if not pages:
        raise ValidationError("Pages list cannot be empty")

    for page_num in pages:
        if not isinstance(page_num, int):
            raise ValidationError(f"Page number must be integer: {page_num}")

        if page_num < 1:
            raise ValidationError(f"Page numbers must be >= 1: {page_num}")

        if page_num > total_pages:
            raise ValidationError(
                f"Page {page_num} does not exist (PDF has {total_pages} pages)"
            )


def validate_encoding(encoding: str) -> None:
    """
    Validate that encoding is supported.

    Args:
        encoding: Character encoding name

    Raises:
        ValidationError: If encoding is not supported
    """
    try:
        "test".encode(encoding)
    except LookupError:
        raise ValidationError(f"Unsupported encoding: {encoding}")


def check_text_layer(pdf_path: Path) -> tuple[bool, int]:
    """
    Check if PDF has a text layer and count pages.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (has_text, num_pages)

    Raises:
        ValidationError: If PDF cannot be read
    """
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        # Check first 3 pages for text
        has_text = False
        for i in range(min(3, num_pages)):
            text = reader.pages[i].extract_text()
            if text and text.strip():
                has_text = True
                break

        return has_text, num_pages
    except Exception as e:
        raise ValidationError(f"Cannot read PDF: {e}")
