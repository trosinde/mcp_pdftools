"""
OCR (Optical Character Recognition) module for PDF documents.

This module provides OCR functionality for scanned PDF documents using Tesseract OCR.

Public API:
    - perform_ocr: Main function to perform OCR on PDFs
    - OCRLanguage: Enum of supported languages
    - OutputMode: Enum of output formats
    - OCRConfig: Configuration dataclass
    - OCRResult: Result dataclass

Example:
    >>> from pdftools.ocr import perform_ocr, OCRLanguage, OutputMode
    >>> result = perform_ocr(
    ...     input_path=Path("scan.pdf"),
    ...     language=OCRLanguage.GERMAN,
    ...     output_mode=OutputMode.TXT
    ... )
"""

from pdftools.ocr.core import perform_ocr
from pdftools.ocr.models import (
    OCRLanguage,
    OutputMode,
    OCRConfig,
    OCRResult,
)

__all__ = [
    'perform_ocr',
    'OCRLanguage',
    'OutputMode',
    'OCRConfig',
    'OCRResult',
]