"""
Invoice PDF Renaming Module

This module provides functionality for intelligently renaming invoice PDFs
based on extracted data (invoice number, date, vendor) using configurable
templates and regex patterns.

Features:
- Extract invoice data from PDF text
- Template-based filename generation
- Batch processing
- Dry-run mode
- Custom regex patterns
- Vendor-specific patterns (Amazon, PayPal, eBay, etc.)

Example:
    >>> from pdftools.renaming import rename_invoice
    >>> from pathlib import Path
    >>> result = rename_invoice(
    ...     Path("invoice.pdf"),
    ...     template="{vendor}_{invoice_nr}_{date}.pdf"
    ... )
    >>> print(f"Renamed: {result.old_name} -> {result.new_name}")
"""

__version__ = "1.0.0"

# Core functionality
from .core import (
    rename_invoice,
    batch_rename,
    NamingTemplate
)

# Data models
from .models import (
    InvoiceData,
    RenameConfig,
    RenameResult
)

# Extractors
from .extractors import (
    InvoiceDataExtractor
)

# Patterns
from .patterns import (
    DEFAULT_PATTERNS,
    VENDOR_SPECIFIC_PATTERNS,
    get_patterns_for_vendor,
    load_custom_patterns,
    normalize_date,
    merge_patterns
)

# Validators
from .validators import (
    validate_template,
    validate_patterns,
    sanitize_filename,
    InvalidTemplateError,
    InvalidPatternError
)


__all__ = [
    # Core functions
    'rename_invoice',
    'batch_rename',
    'NamingTemplate',

    # Models
    'InvoiceData',
    'RenameConfig',
    'RenameResult',

    # Extractors
    'InvoiceDataExtractor',

    # Patterns
    'DEFAULT_PATTERNS',
    'VENDOR_SPECIFIC_PATTERNS',
    'get_patterns_for_vendor',
    'load_custom_patterns',
    'normalize_date',
    'merge_patterns',

    # Validators
    'validate_template',
    'validate_patterns',
    'sanitize_filename',
    'InvalidTemplateError',
    'InvalidPatternError',
]
