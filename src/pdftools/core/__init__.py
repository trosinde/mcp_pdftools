"""
Core utilities and shared functionality for PDF Tools
"""

from .exceptions import PDFToolsError, PDFNotFoundError, PDFProcessingError
from .validators import validate_pdf_path, validate_output_path
from .utils import normalize_path, ensure_directory_exists

__all__ = [
    'PDFToolsError',
    'PDFNotFoundError',
    'PDFProcessingError',
    'validate_pdf_path',
    'validate_output_path',
    'normalize_path',
    'ensure_directory_exists',
]
