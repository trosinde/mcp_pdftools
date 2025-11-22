"""
Core functionality for PDF thumbnail generation
"""

import logging
from pathlib import Path
from typing import Union, Optional

try:
    from pdf2image import pdfinfo_from_path
    from pdf2image.exceptions import PDFInfoNotInstalledError
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    pdfinfo_from_path = None
    PDFInfoNotInstalledError = Exception

from pdftools.core.exceptions import PDFProcessingError, ValidationError
from .models import ThumbnailConfig, ThumbnailResult, ThumbnailSize, ThumbnailFormat
from .validators import (
    validate_pdf_path,
    validate_output_dir,
    validate_size,
    validate_format,
    validate_quality,
    validate_pages
)
from .generators import PDFThumbnailGenerator

logger = logging.getLogger('pdftools.thumbnails')


def get_pdf_page_count(pdf_path: Path) -> int:
    """
    Get the number of pages in a PDF file.

    Args:
        pdf_path: Path to PDF file

    Returns:
        int: Number of pages in PDF

    Raises:
        PDFProcessingError: If page count cannot be determined
    """
    if not PDF2IMAGE_AVAILABLE:
        raise ImportError(
            "pdf2image is not installed. Install it with: pip install pdf2image"
        )

    try:
        info = pdfinfo_from_path(str(pdf_path))
        return info.get('Pages', 0)
    except PDFInfoNotInstalledError:
        raise PDFProcessingError(
            "poppler-utils is not installed. Please install it:\n"
            "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
            "  macOS: brew install poppler\n"
            "  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases"
        )
    except Exception as e:
        raise PDFProcessingError(f"Failed to get PDF page count: {e}")


def generate_thumbnails(
    input_path: Union[str, Path],
    output_dir: Union[str, Path, None] = None,
    size: Union[ThumbnailSize, tuple[int, int], str] = ThumbnailSize.MEDIUM,
    format: Union[ThumbnailFormat, str] = ThumbnailFormat.PNG,
    pages: Union[list[int], str, None] = None,
    quality: int = 85,
    verbose: bool = False
) -> ThumbnailResult:
    """
    Generate thumbnail images from PDF pages.

    This is the main entry point for thumbnail generation. It validates inputs,
    converts PDF pages to images, resizes them, and saves them to disk.

    Args:
        input_path: Path to input PDF file
        output_dir: Directory for output thumbnails (default: ./thumbnails)
        size: Thumbnail size - can be:
            - ThumbnailSize enum (SMALL, MEDIUM, LARGE)
            - tuple of (width, height) in pixels
            - string like "800x600"
        format: Output format - ThumbnailFormat enum or string ("png" or "jpg")
        pages: Pages to process - can be:
            - list of page numbers (1-indexed): [1, 3, 5]
            - string specification: "1,3,5-10"
            - None for all pages
        quality: JPEG quality 1-100 (ignored for PNG)
        verbose: Enable detailed logging

    Returns:
        ThumbnailResult: Object containing:
            - status: 'success', 'error', or 'partial'
            - thumbnails_created: Number of thumbnails created
            - thumbnail_paths: List of paths to created files
            - message: Status or error message
            - skipped_pages: Pages that failed to process
            - total_pages: Total pages in PDF

    Raises:
        ValidationError: If inputs are invalid
        PDFProcessingError: If PDF processing fails
        ImportError: If required dependencies are missing

    Examples:
        >>> # Basic usage with defaults
        >>> result = generate_thumbnails("document.pdf")
        >>> print(f"Created {result.thumbnails_created} thumbnails")

        >>> # Custom size and format
        >>> result = generate_thumbnails(
        ...     "report.pdf",
        ...     output_dir="./previews",
        ...     size=ThumbnailSize.LARGE,
        ...     format="jpg",
        ...     quality=90
        ... )

        >>> # Specific pages only
        >>> result = generate_thumbnails(
        ...     "manual.pdf",
        ...     pages="1,5,10-15",
        ...     size=(800, 600)
        ... )

        >>> # Check results
        >>> if result.success:
        ...     for path in result.thumbnail_paths:
        ...         print(f"Created: {path}")
        ... else:
        ...     print(f"Error: {result.message}")
    """
    # Setup logging
    if verbose:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.DEBUG)

    try:
        # Validate input PDF
        logger.info(f"Validating input PDF: {input_path}")
        pdf_path = validate_pdf_path(input_path)

        # Validate output directory
        if output_dir is None:
            output_dir = Path.cwd() / "thumbnails"
        logger.info(f"Validating output directory: {output_dir}")
        output_path = validate_output_dir(output_dir)

        # Validate and parse size
        logger.info(f"Validating size: {size}")
        size_tuple = validate_size(size)

        # Validate and parse format
        logger.info(f"Validating format: {format}")
        format_enum = validate_format(format)

        # Validate quality
        logger.info(f"Validating quality: {quality}")
        quality_value = validate_quality(quality)

        # Get total page count
        logger.info("Getting PDF page count")
        total_pages = get_pdf_page_count(pdf_path)

        if total_pages == 0:
            return ThumbnailResult(
                status='error',
                message='PDF has no pages',
                total_pages=0
            )

        logger.info(f"PDF has {total_pages} pages")

        # Validate and parse pages
        logger.info(f"Validating pages: {pages}")
        pages_list = validate_pages(pages, total_pages)

        logger.info(f"Will process {len(pages_list)} pages: {pages_list}")

        # Create configuration
        config = ThumbnailConfig(
            size=size_tuple,
            format=format_enum,
            quality=quality_value,
            verbose=verbose
        )

        # Create generator
        logger.info("Initializing thumbnail generator")
        generator = PDFThumbnailGenerator(config)

        # Generate thumbnails
        logger.info("Generating thumbnails")
        thumbnail_paths = []
        skipped_pages = []

        try:
            thumbnail_paths = generator.generate_and_save(
                pdf_path=pdf_path,
                output_dir=output_path,
                pages=pages_list
            )

        except PDFProcessingError as e:
            # If generation failed completely
            logger.error(f"Thumbnail generation failed: {e}")
            return ThumbnailResult(
                status='error',
                message=str(e),
                total_pages=total_pages,
                thumbnails_created=0
            )

        # Determine status
        if len(thumbnail_paths) == len(pages_list):
            status = 'success'
            message = f"Successfully created {len(thumbnail_paths)} thumbnails"
        elif len(thumbnail_paths) > 0:
            status = 'partial'
            message = f"Created {len(thumbnail_paths)} of {len(pages_list)} thumbnails"
        else:
            status = 'error'
            message = "Failed to create any thumbnails"

        logger.info(message)

        return ThumbnailResult(
            status=status,
            thumbnails_created=len(thumbnail_paths),
            thumbnail_paths=thumbnail_paths,
            message=message,
            skipped_pages=skipped_pages,
            total_pages=total_pages
        )

    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        return ThumbnailResult(
            status='error',
            message=f"Validation error: {e}",
            thumbnails_created=0
        )

    except PDFProcessingError as e:
        logger.error(f"Processing error: {e}")
        return ThumbnailResult(
            status='error',
            message=f"Processing error: {e}",
            thumbnails_created=0
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return ThumbnailResult(
            status='error',
            message=f"Unexpected error: {e}",
            thumbnails_created=0
        )
