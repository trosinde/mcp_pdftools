"""
Validation functions for OCR operations
"""

from pathlib import Path
from typing import List, Union
import logging

from pdftools.core.exceptions import (
    PDFNotFoundError,
    InvalidParameterError,
    TesseractNotFoundError,
    LanguageNotAvailableError,
)
from pdftools.ocr.models import OCRLanguage

logger = logging.getLogger(__name__)


def validate_pdf(pdf_path: Path) -> Path:
    """
    Validate that PDF file exists and is readable.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Path: Validated PDF path

    Raises:
        PDFNotFoundError: If file doesn't exist
        InvalidParameterError: If not a PDF file
    """
    if not pdf_path.exists():
        raise PDFNotFoundError(str(pdf_path))

    if not pdf_path.is_file():
        raise InvalidParameterError(
            "pdf_path",
            str(pdf_path),
            "Path is not a file"
        )

    if pdf_path.suffix.lower() != '.pdf':
        raise InvalidParameterError(
            "pdf_path",
            str(pdf_path),
            "File must be a PDF (.pdf extension)"
        )

    return pdf_path


def validate_language(
    language: Union[OCRLanguage, List[OCRLanguage], str, List[str]]
) -> List[str]:
    """
    Validate and normalize OCR language(s).

    Args:
        language: Single language or list of languages (OCRLanguage or string)

    Returns:
        List[str]: List of language codes (e.g., ['deu', 'eng'])

    Raises:
        InvalidParameterError: If language is invalid
    """
    # Convert to list if single language
    if isinstance(language, (OCRLanguage, str)):
        languages = [language]
    else:
        languages = language

    # Validate and normalize
    validated = []
    for lang in languages:
        if isinstance(lang, OCRLanguage):
            validated.append(lang.value)
        elif isinstance(lang, str):
            # Check if it's a valid OCRLanguage value
            lang_lower = lang.lower()
            valid_codes = [e.value for e in OCRLanguage]
            if lang_lower in valid_codes:
                validated.append(lang_lower)
            else:
                # Check if it's a valid OCRLanguage name
                try:
                    lang_enum = OCRLanguage[lang.upper()]
                    validated.append(lang_enum.value)
                except KeyError:
                    raise InvalidParameterError(
                        "language",
                        lang,
                        f"Unsupported language. Valid options: {', '.join(valid_codes)}"
                    )
        else:
            raise InvalidParameterError(
                "language",
                lang,
                "Language must be OCRLanguage or string"
            )

    return validated


def check_tesseract() -> bool:
    """
    Check if Tesseract OCR is available.

    Returns:
        bool: True if Tesseract is available

    Raises:
        TesseractNotFoundError: If Tesseract is not installed
    """
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        logger.debug(f"Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"Tesseract not found: {e}")
        raise TesseractNotFoundError() from e


def check_language_available(language: str) -> bool:
    """
    Check if a specific Tesseract language is available.

    Args:
        language: Language code (e.g., 'deu', 'eng')

    Returns:
        bool: True if language is available

    Raises:
        LanguageNotAvailableError: If language is not installed
    """
    try:
        import pytesseract
        available_languages = pytesseract.get_languages(config='')
        logger.debug(f"Available Tesseract languages: {available_languages}")

        if language not in available_languages:
            raise LanguageNotAvailableError(language)

        return True
    except LanguageNotAvailableError:
        raise
    except Exception as e:
        logger.error(f"Failed to check language availability: {e}")
        raise TesseractNotFoundError() from e


def validate_pages(pages: List[int], total_pages: int) -> List[int]:
    """
    Validate page numbers.

    Args:
        pages: List of page numbers (1-indexed)
        total_pages: Total number of pages in document

    Returns:
        List[int]: Validated page numbers

    Raises:
        InvalidParameterError: If page numbers are invalid
    """
    if not pages:
        return list(range(1, total_pages + 1))

    for page in pages:
        if page < 1 or page > total_pages:
            raise InvalidParameterError(
                "pages",
                pages,
                f"Page {page} out of range (1-{total_pages})"
            )

    return sorted(set(pages))  # Remove duplicates and sort
