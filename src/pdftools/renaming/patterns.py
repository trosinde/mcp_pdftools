"""
Predefined regex patterns for invoice data extraction.

This module provides default patterns for extracting invoice numbers,
dates, and vendor names from invoice PDFs, as well as vendor-specific
patterns for common platforms.
"""

from typing import Dict
import json
from pathlib import Path


# Default patterns for generic invoice data extraction
DEFAULT_PATTERNS: Dict[str, str] = {
    # Invoice Number Patterns
    # Matches: "Invoice Number: 12345", "Rechnung Nr. ABC-123", "Bill #: 001"
    'invoice_nr': (
        r'(?:Invoice|Rechnung|Bill|Faktura)\s*'
        r'(?:Number|Nr\.?|#|ID)?\s*:?\s*'
        r'([A-Z0-9][A-Z0-9\-_/.]{2,30})'
    ),

    # Date Patterns (multiple formats)
    # Matches: "Date: 2024-03-15", "Datum: 15.03.2024", "Date: 03/15/2024"
    'date': (
        r'(?:Date|Datum|Invoice\s+Date)\s*:?\s*'
        r'(\d{4}-\d{2}-\d{2}|'  # ISO: 2024-03-15
        r'\d{2}\.\d{2}\.\d{4}|'  # DE: 15.03.2024
        r'\d{2}/\d{2}/\d{4}|'    # US: 03/15/2024
        r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})'  # 15 March 2024
    ),

    # Vendor/Supplier Patterns
    # Matches: "From: Amazon", "Vendor: PayPal Inc.", "Supplier: Acme Corp"
    'vendor': (
        r'(?:From|Von|Vendor|Supplier|Seller)\s*:?\s*'
        r'([A-Z][a-zA-Z0-9\s&\.,\-]{2,40})'
    ),
}


# Vendor-specific patterns for better accuracy with known platforms
VENDOR_SPECIFIC_PATTERNS: Dict[str, Dict[str, str]] = {
    'amazon': {
        'invoice_nr': r'(?:Order|Bestellung)\s*#?\s*:?\s*(\d{3}-\d{7}-\d{7})',
        'vendor': r'Amazon(?:\.com|\.de|\.co\.uk)?',
        'date': r'(?:Order\s+Date|Bestelldatum)\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})',
    },

    'paypal': {
        'invoice_nr': r'(?:Transaction\s+ID|Transaktions-ID)\s*:?\s*([A-Z0-9]{17})',
        'vendor': r'PayPal',
        'date': r'(?:Date|Datum)\s*:?\s*(\d{1,2}\s+\w+\s+\d{4})',
    },

    'ebay': {
        'invoice_nr': r'(?:Order\s+number|Bestellnummer)\s*:?\s*(\d{2}-\d{5}-\d{5})',
        'vendor': r'eBay',
        'date': r'(?:Order\s+date|Bestelldatum)\s*:?\s*(\d{1,2}\.\d{1,2}\.\d{4})',
    },

    'stripe': {
        'invoice_nr': r'(?:Invoice|Receipt)\s+#?\s*:?\s*([A-Z0-9\-]{10,30})',
        'vendor': r'Stripe',
        'date': r'(?:Date|Invoice\s+date)\s*:?\s*(\w+\s+\d{1,2},\s+\d{4})',
    },
}


def get_patterns_for_vendor(vendor_name: str) -> Dict[str, str]:
    """
    Get vendor-specific patterns if available, otherwise default patterns.

    Args:
        vendor_name: Name of vendor (case-insensitive)

    Returns:
        Dictionary of patterns for the vendor

    Example:
        >>> patterns = get_patterns_for_vendor('amazon')
        >>> 'invoice_nr' in patterns
        True
    """
    vendor_key = vendor_name.lower()
    if vendor_key in VENDOR_SPECIFIC_PATTERNS:
        # Merge vendor-specific with defaults (vendor-specific takes precedence)
        merged = {**DEFAULT_PATTERNS}
        merged.update(VENDOR_SPECIFIC_PATTERNS[vendor_key])
        return merged
    return DEFAULT_PATTERNS.copy()


def load_custom_patterns(pattern_file: Path) -> Dict[str, str]:
    """
    Load custom patterns from JSON file.

    Args:
        pattern_file: Path to JSON file with patterns

    Returns:
        Dictionary of pattern names to regex strings

    Raises:
        FileNotFoundError: If pattern file doesn't exist
        ValueError: If JSON is invalid

    Example JSON format:
        {
            "invoice_nr": "Invoice\\\\s*#\\\\s*(\\\\d+)",
            "vendor": "Company:\\\\s*([A-Z]+)",
            "date": "Date:\\\\s*(\\\\d{4}-\\\\d{2}-\\\\d{2})"
        }
    """
    if not pattern_file.exists():
        raise FileNotFoundError(f"Pattern file not found: {pattern_file}")

    try:
        with open(pattern_file, 'r', encoding='utf-8') as f:
            patterns = json.load(f)

        if not isinstance(patterns, dict):
            raise ValueError("Pattern file must contain a JSON object/dictionary")

        return patterns

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in pattern file: {e}") from e


def normalize_date(date_str: str) -> str:
    """
    Normalize various date formats to ISO format (YYYY-MM-DD).

    Args:
        date_str: Date string in various formats

    Returns:
        Date in ISO format (YYYY-MM-DD) or original string if parsing fails

    Example:
        >>> normalize_date("15.03.2024")
        '2024-03-15'
        >>> normalize_date("03/15/2024")
        '2024-03-15'
        >>> normalize_date("15 March 2024")
        '2024-03-15'
    """
    from datetime import datetime
    import re

    # Already in ISO format
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return date_str

    # Try multiple date formats
    date_formats = [
        '%d.%m.%Y',           # 15.03.2024
        '%m/%d/%Y',           # 03/15/2024
        '%d/%m/%Y',           # 15/03/2024
        '%d %B %Y',           # 15 March 2024
        '%d %b %Y',           # 15 Mar 2024
        '%B %d, %Y',          # March 15, 2024
        '%b %d, %Y',          # Mar 15, 2024
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue

    # If all formats fail, return original
    return date_str


def merge_patterns(*pattern_dicts: Dict[str, str]) -> Dict[str, str]:
    """
    Merge multiple pattern dictionaries (later ones override earlier).

    Args:
        *pattern_dicts: Variable number of pattern dictionaries

    Returns:
        Merged pattern dictionary

    Example:
        >>> defaults = {"invoice_nr": "pattern1"}
        >>> custom = {"invoice_nr": "pattern2", "vendor": "pattern3"}
        >>> result = merge_patterns(defaults, custom)
        >>> result["invoice_nr"]
        'pattern2'
    """
    merged = {}
    for patterns in pattern_dicts:
        if patterns:
            merged.update(patterns)
    return merged
