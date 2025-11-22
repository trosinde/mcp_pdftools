"""
Core functionality for invoice PDF renaming.

This module provides the main logic for renaming invoice PDFs based
on extracted data and templates.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from .models import InvoiceData, RenameConfig, RenameResult
from .extractors import InvoiceDataExtractor
from .validators import validate_template, validate_patterns, sanitize_filename
from .patterns import DEFAULT_PATTERNS


logger = logging.getLogger(__name__)


class NamingTemplate:
    """
    Handles template rendering for file names.

    This class validates and renders naming templates with placeholders
    like {vendor}_{invoice_nr}_{date}.pdf
    """

    def __init__(self, template: str):
        """
        Initialize with template string.

        Args:
            template: Template with placeholders

        Raises:
            InvalidTemplateError: If template is invalid
        """
        self.template = template
        validate_template(template)

    def render(self, data: InvoiceData, max_length: int = 255) -> str:
        """
        Render template with invoice data.

        Args:
            data: Extracted invoice data
            max_length: Maximum filename length

        Returns:
            Rendered filename with sanitized values
        """
        # Prepare values, using 'unknown' for missing data
        values = {
            'vendor': data.vendor or 'unknown',
            'invoice_nr': data.invoice_number or 'unknown',
            'date': data.date or 'unknown',
            'year': data.year or 'unknown',
            'month': data.month or 'unknown',
            'day': data.day or 'unknown'
        }

        # Sanitize all values
        values = {
            k: sanitize_filename(v, max_length=100)
            for k, v in values.items()
        }

        # Render template
        rendered = self.template.format(**values)

        # Final sanitization of complete filename
        return sanitize_filename(rendered, max_length=max_length)


def rename_invoice(
    input_path: Path,
    template: str = "{vendor}_{invoice_nr}_{date}.pdf",
    custom_patterns: Optional[Dict[str, str]] = None,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
    config: Optional[RenameConfig] = None
) -> RenameResult:
    """
    Rename invoice PDF based on extracted data.

    Args:
        input_path: Path to invoice PDF
        template: Naming template with placeholders
        custom_patterns: Custom regex patterns for extraction
        output_dir: Target directory (default: same as input)
        dry_run: If True, only simulate rename
        config: Optional configuration

    Returns:
        RenameResult: Object containing status, old/new names, extracted data

    Raises:
        PDFNotFoundError: If input file doesn't exist
        InvalidTemplateError: If template is invalid
        PDFProcessingError: If extraction fails

    Example:
        >>> result = rename_invoice(
        ...     Path("invoice.pdf"),
        ...     template="{vendor}_{date}.pdf"
        ... )
        >>> print(f"{result.old_name} -> {result.new_name}")
    """
    # Initialize config
    if config is None:
        config = RenameConfig()

    old_name = input_path.name

    # Validate input
    if not input_path.exists():
        from pdftools.core.exceptions import PDFNotFoundError
        return RenameResult(
            status='error',
            old_name=old_name,
            message=f"PDF file not found: {input_path}",
            dry_run=dry_run
        )

    # Validate and merge patterns
    patterns = {**DEFAULT_PATTERNS}
    if custom_patterns:
        validate_patterns(custom_patterns)
        patterns.update(custom_patterns)

    # Extract invoice data
    try:
        extractor = InvoiceDataExtractor(custom_patterns=patterns)
        invoice_data = extractor.extract_from_pdf(input_path)

        if config.verbose:
            print(f"\nProcessing: {old_name}")
            print(f"  Invoice #: {invoice_data.invoice_number or 'Not found'}")
            print(f"  Date: {invoice_data.date or 'Not found'}")
            print(f"  Vendor: {invoice_data.vendor or 'Not found'}")

    except Exception as e:
        logger.error(f"Failed to extract data from {input_path}: {e}")
        return RenameResult(
            status='error',
            old_name=old_name,
            message=f"Failed to extract invoice data: {e}",
            dry_run=dry_run
        )

    # Generate new filename from template
    try:
        naming_template = NamingTemplate(template)
        new_name = naming_template.render(invoice_data, config.max_filename_length)

        # Ensure .pdf extension
        if not new_name.lower().endswith('.pdf'):
            new_name += '.pdf'

    except Exception as e:
        logger.error(f"Failed to render template: {e}")
        # Fallback name
        new_name = f"{config.fallback_name}_{old_name}"

    # Determine output path
    if output_dir is None:
        output_dir = input_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    new_path = output_dir / new_name

    # Handle duplicates
    if new_path.exists() and new_path != input_path:
        if config.handle_duplicates:
            new_path = _resolve_duplicate(new_path)
            new_name = new_path.name
        else:
            return RenameResult(
                status='error',
                old_name=old_name,
                new_name=new_name,
                extracted_data=invoice_data,
                message=f"File already exists: {new_name}",
                dry_run=dry_run
            )

    # Perform rename (or simulate)
    if dry_run:
        if config.verbose:
            print(f"  Would rename to: {new_name}")

        return RenameResult(
            status='success',
            old_name=old_name,
            new_name=new_name,
            extracted_data=invoice_data,
            message=f"Dry run: {old_name} -> {new_name}",
            dry_run=True
        )

    # Actual rename
    try:
        input_path.rename(new_path)

        if config.verbose:
            print(f"  Renamed to: {new_name}")

        logger.info(f"Renamed: {old_name} -> {new_name}")

        return RenameResult(
            status='success',
            old_name=old_name,
            new_name=new_name,
            extracted_data=invoice_data,
            message=f"Successfully renamed to {new_name}",
            dry_run=False
        )

    except Exception as e:
        logger.error(f"Failed to rename {input_path}: {e}")
        return RenameResult(
            status='error',
            old_name=old_name,
            new_name=new_name,
            extracted_data=invoice_data,
            message=f"Failed to rename file: {e}",
            dry_run=dry_run
        )


def batch_rename(
    input_paths: List[Path],
    template: str = "{vendor}_{invoice_nr}_{date}.pdf",
    custom_patterns: Optional[Dict[str, str]] = None,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
    config: Optional[RenameConfig] = None
) -> List[RenameResult]:
    """
    Rename multiple invoice PDFs.

    Args:
        input_paths: List of PDF paths
        template: Naming template
        custom_patterns: Custom patterns
        output_dir: Target directory
        dry_run: Simulation mode
        config: Optional configuration

    Returns:
        List[RenameResult]: Results for each file

    Example:
        >>> results = batch_rename(
        ...     [Path("inv1.pdf"), Path("inv2.pdf")],
        ...     template="{vendor}_{date}.pdf"
        ... )
        >>> successful = sum(1 for r in results if r.success)
    """
    if config is None:
        config = RenameConfig()

    results = []

    for input_path in input_paths:
        result = rename_invoice(
            input_path=input_path,
            template=template,
            custom_patterns=custom_patterns,
            output_dir=output_dir,
            dry_run=dry_run,
            config=config
        )
        results.append(result)

    return results


def _resolve_duplicate(path: Path) -> Path:
    """
    Resolve duplicate filename by adding numeric suffix.

    Args:
        path: Original path that conflicts

    Returns:
        New path with numeric suffix (e.g., name_1.pdf, name_2.pdf)

    Example:
        >>> _resolve_duplicate(Path("invoice.pdf"))
        Path("invoice_1.pdf")  # if invoice.pdf exists
    """
    stem = path.stem
    suffix = path.suffix
    parent = path.parent

    counter = 1
    while True:
        new_path = parent / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

        # Safety limit
        if counter > 9999:
            raise RuntimeError("Too many duplicate files")
