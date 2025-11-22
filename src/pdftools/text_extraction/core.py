"""Core text extraction functionality."""

from pathlib import Path
from typing import Optional, Union

from pdftools.core.validators import validate_pdf_path, validate_directory
from pdftools.core.exceptions import ValidationError

from .models import (
    ExtractionConfig,
    ExtractionResult,
    ExtractionMode,
    OutputFormat
)
from .validators import validate_pages, validate_encoding, check_text_layer
from .extractors import (
    SimpleExtractor,
    LayoutExtractor,
    PerPageExtractor,
    StructuredExtractor
)
from .formatters import get_formatter


def extract_text(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    mode: ExtractionMode = ExtractionMode.SIMPLE,
    format: OutputFormat = OutputFormat.TXT,
    pages: Optional[list[int]] = None,
    encoding: str = "utf-8",
    include_metadata: bool = False,
    verbose: bool = False,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Extract text from a PDF file.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output file or directory (None = stdout)
        mode: Extraction mode (SIMPLE, LAYOUT, PER_PAGE, STRUCTURED)
        format: Output format (TXT, JSON, MARKDOWN)
        pages: Specific pages to extract (None = all pages)
        encoding: Output encoding (default: utf-8)
        include_metadata: Include PDF metadata in output
        verbose: Show progress indicator
        config: Pre-configured ExtractionConfig (overrides other params)

    Returns:
        ExtractionResult with extracted text and metadata

    Raises:
        ValidationError: If input is invalid

    Example:
        >>> result = extract_text("document.pdf", "output.txt")
        >>> print(result.char_count)
        12450
    """
    # Build config
    if config is None:
        config = ExtractionConfig(
            input_path=Path(input_path),
            output_path=Path(output_path) if output_path else None,
            mode=mode,
            format=format,
            pages=pages,
            encoding=encoding,
            include_metadata=include_metadata,
            verbose=verbose
        )

    # Validate input
    validate_pdf_path(config.input_path)
    validate_encoding(config.encoding)

    # Check for text layer
    has_text, num_pages = check_text_layer(config.input_path)
    if not has_text:
        if verbose:
            print(f"⚠ Warning: No text layer found. PDF may be scanned. Consider using OCR.")

    # Validate pages if specified
    if config.pages:
        validate_pages(config.pages, num_pages)

    # Validate output path
    if config.output_path:
        if mode == ExtractionMode.PER_PAGE:
            # Output should be directory
            if config.output_path.exists() and config.output_path.is_file():
                raise ValidationError(
                    "PER_PAGE mode requires output_path to be a directory"
                )
        else:
            # Validate output directory can be created
            validate_directory(config.output_path.parent, create_if_missing=True)

    # Create appropriate extractor
    extractor = _create_extractor(config)

    # Extract text
    result = extractor.extract()

    # Write output if path specified
    if config.output_path and mode != ExtractionMode.PER_PAGE:
        formatter = get_formatter(config.format)
        output_text = formatter.format(result)
        config.output_path.write_text(output_text, encoding=config.encoding)
        result.message = f"Text extracted to {config.output_path}"

    return result


def _create_extractor(config: ExtractionConfig):
    """Factory function to create appropriate extractor."""
    extractors = {
        ExtractionMode.SIMPLE: SimpleExtractor,
        ExtractionMode.LAYOUT: LayoutExtractor,
        ExtractionMode.PER_PAGE: PerPageExtractor,
        ExtractionMode.STRUCTURED: StructuredExtractor
    }
    return extractors[config.mode](config)
