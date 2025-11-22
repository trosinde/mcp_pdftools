"""
PDF Thumbnails Module

Generate thumbnail images from PDF pages with configurable sizes and formats.

This module provides functionality to create preview images from PDF documents,
supporting various sizes (small, medium, large, custom) and formats (PNG, JPG).

Main Functions:
    generate_thumbnails: Generate thumbnails from PDF pages

Classes:
    ThumbnailSize: Predefined thumbnail size enums
    ThumbnailFormat: Output format enums (PNG, JPG)
    ThumbnailConfig: Configuration for thumbnail generation
    ThumbnailResult: Result object with operation details
    PDFThumbnailGenerator: Low-level generator class

Example:
    >>> from pdftools.thumbnails import generate_thumbnails, ThumbnailSize
    >>> result = generate_thumbnails(
    ...     "document.pdf",
    ...     size=ThumbnailSize.LARGE,
    ...     format="jpg"
    ... )
    >>> print(f"Created {result.thumbnails_created} thumbnails")
"""

from .core import generate_thumbnails, get_pdf_page_count
from .models import (
    ThumbnailSize,
    ThumbnailFormat,
    ThumbnailConfig,
    ThumbnailResult
)
from .generators import PDFThumbnailGenerator

__all__ = [
    # Main API
    'generate_thumbnails',
    'get_pdf_page_count',

    # Models
    'ThumbnailSize',
    'ThumbnailFormat',
    'ThumbnailConfig',
    'ThumbnailResult',

    # Advanced
    'PDFThumbnailGenerator',
]

__version__ = '1.0.0'
