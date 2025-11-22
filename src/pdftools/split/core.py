"""
Core PDF split functionality.
"""

import logging
from pathlib import Path
from typing import Optional

from pdftools.core.exceptions import PDFNotFoundError, PDFProcessingError, ValidationError
from pdftools.core.utils import ensure_dir_exists
from pdftools.split.models import SplitMode, SplitConfig, SplitResult
from pdftools.split.validators import validate_pdf_path, validate_output_dir
from pdftools.split.processors import (
    PagesSplitter,
    RangesSplitter,
    PartsSplitter,
    SpecificPagesSplitter
)


logger = logging.getLogger('pdftools.split.core')


def split_pdf(
    input_path: str | Path,
    output_dir: str | Path | None = None,
    mode: SplitMode = SplitMode.PAGES,
    ranges: list[tuple[int, int]] | None = None,
    pages: list[int] | None = None,
    num_parts: int | None = None,
    prefix: str | None = None,
    verbose: bool = False,
    config: SplitConfig | None = None
) -> SplitResult:
    """
    Split a PDF file according to specified mode.

    Args:
        input_path: Path to input PDF file
        output_dir: Directory for output files (default: current directory)
        mode: Split mode (PAGES, RANGES, PARTS, SPECIFIC_PAGES)
        ranges: List of (start, end) tuples for RANGES mode (1-indexed)
        pages: List of page numbers for SPECIFIC_PAGES mode (1-indexed)
        num_parts: Number of parts for PARTS mode
        prefix: Prefix for output files (default: input filename without extension)
        verbose: Enable verbose logging
        config: SplitConfig object (overrides individual parameters)

    Returns:
        SplitResult: Object containing:
            - num_files: Number of files created
            - output_files: List of Path objects to created files
            - status: 'success' or 'error'
            - message: Success/error message
            - metadata: Dict with additional info (total_pages, mode, etc.)

    Raises:
        PDFNotFoundError: If input_path does not exist
        PDFProcessingError: If PDF is corrupted or cannot be read
        ValidationError: If parameters are invalid (e.g., invalid ranges)

    Example:
        >>> # Split into individual pages
        >>> result = split_pdf("document.pdf")
        >>> print(f"Created {result.num_files} files")

        >>> # Split by ranges
        >>> result = split_pdf(
        ...     "document.pdf",
        ...     mode=SplitMode.RANGES,
        ...     ranges=[(1, 5), (10, 15)]
        ... )

        >>> # Split into 5 equal parts
        >>> result = split_pdf(
        ...     "document.pdf",
        ...     mode=SplitMode.PARTS,
        ...     num_parts=5
        ... )
    """
    # Use config object if provided, otherwise create from parameters
    if config is None:
        # Convert paths
        input_path = Path(input_path) if input_path else None
        output_dir = Path(output_dir) if output_dir else Path(".")

        # Create config
        try:
            config = SplitConfig(
                input_path=input_path,
                output_dir=output_dir,
                mode=mode,
                prefix=prefix,
                verbose=verbose,
                ranges=ranges,
                pages=pages,
                num_parts=num_parts
            )
        except ValidationError as e:
            logger.error(f"Invalid configuration: {e}")
            return SplitResult(
                status='error',
                message=f"Invalid configuration: {e}"
            )

    # Validate input PDF
    try:
        validate_pdf_path(config.input_path)
    except (PDFNotFoundError, ValidationError) as e:
        logger.error(f"Input validation failed: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )

    # Validate/create output directory
    try:
        validate_output_dir(config.output_dir, create=True)
    except (ValidationError, PermissionError) as e:
        logger.error(f"Output directory validation failed: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )

    # Create appropriate splitter based on mode
    try:
        splitter = _create_splitter(config)
        result = splitter.split()
        return result

    except PDFProcessingError as e:
        logger.error(f"PDF processing failed: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}", exc_info=True)
        return SplitResult(
            status='error',
            message=f"Unexpected error: {e}"
        )


def _create_splitter(config: SplitConfig):
    """
    Create appropriate splitter instance based on config.

    Args:
        config: SplitConfig object

    Returns:
        BaseSplitter instance

    Raises:
        ValidationError: If mode-specific parameters are missing
    """
    if config.mode == SplitMode.PAGES:
        return PagesSplitter(
            config.input_path,
            config.output_dir,
            config.prefix,
            config.verbose
        )

    elif config.mode == SplitMode.RANGES:
        if not config.ranges:
            raise ValidationError("ranges required for RANGES mode")
        return RangesSplitter(
            config.input_path,
            config.output_dir,
            config.prefix,
            config.ranges,
            config.verbose
        )

    elif config.mode == SplitMode.PARTS:
        if not config.num_parts:
            raise ValidationError("num_parts required for PARTS mode")
        return PartsSplitter(
            config.input_path,
            config.output_dir,
            config.prefix,
            config.num_parts,
            config.verbose
        )

    elif config.mode == SplitMode.SPECIFIC_PAGES:
        if not config.pages:
            raise ValidationError("pages required for SPECIFIC_PAGES mode")
        return SpecificPagesSplitter(
            config.input_path,
            config.output_dir,
            config.prefix,
            config.pages,
            config.verbose
        )

    else:
        raise ValidationError(f"Unknown split mode: {config.mode}")
