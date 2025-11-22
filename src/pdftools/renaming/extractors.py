"""
Invoice data extraction from PDF text.

This module provides functionality to extract invoice-specific data
(invoice number, date, vendor) from PDF files using regex patterns.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Optional

from .models import InvoiceData
from .patterns import DEFAULT_PATTERNS, normalize_date


logger = logging.getLogger(__name__)


class InvoiceDataExtractor:
    """
    Extracts invoice data from PDF text using regex patterns.

    This class applies configurable regex patterns to extract structured
    data like invoice numbers, dates, and vendor names from invoice PDFs.
    """

    def __init__(self, custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize extractor with patterns.

        Args:
            custom_patterns: Optional custom patterns to override defaults.
                           Keys: 'invoice_nr', 'date', 'vendor'
        """
        self.patterns = {**DEFAULT_PATTERNS}
        if custom_patterns:
            self.patterns.update(custom_patterns)

        # Compile patterns for better performance
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        for name, pattern in self.patterns.items():
            try:
                self._compiled_patterns[name] = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                logger.warning(f"Failed to compile pattern '{name}': {e}")

    def extract_from_text(self, text: str) -> InvoiceData:
        """
        Extract invoice data from text.

        Args:
            text: PDF text content

        Returns:
            InvoiceData: Extracted fields (may have None values if not found)
        """
        invoice_nr = self._extract_invoice_number(text)
        date = self._extract_date(text)
        vendor = self._extract_vendor(text)

        logger.debug(
            f"Extracted: invoice_nr={invoice_nr}, date={date}, vendor={vendor}"
        )

        return InvoiceData(
            invoice_number=invoice_nr,
            date=date,
            vendor=vendor
        )

    def extract_from_pdf(self, pdf_path: Path) -> InvoiceData:
        """
        Extract invoice data from PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            InvoiceData: Extracted invoice data

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            PDFProcessingError: If PDF cannot be read
        """
        if not pdf_path.exists():
            from pdftools.core.exceptions import PDFNotFoundError
            raise PDFNotFoundError(str(pdf_path))

        # Extract text from PDF
        text = self._extract_text_from_pdf(pdf_path)

        # Extract invoice data from text
        return self.extract_from_text(text)

    def _extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text from PDF file using PyPDF2.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text

        Raises:
            PDFProcessingError: If PDF cannot be read
        """
        try:
            from PyPDF2 import PdfReader

            reader = PdfReader(str(pdf_path))
            text_parts = []

            for page in reader.pages:
                text_parts.append(page.extract_text())

            return '\n'.join(text_parts)

        except Exception as e:
            from pdftools.core.exceptions import PDFProcessingError
            raise PDFProcessingError(f"Failed to extract text from {pdf_path}: {e}") from e

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """
        Extract invoice number using regex.

        Args:
            text: Text to search

        Returns:
            Invoice number or None if not found
        """
        pattern = self._compiled_patterns.get('invoice_nr')
        if not pattern:
            logger.warning("No invoice_nr pattern configured")
            return None

        match = pattern.search(text)
        if match:
            # Get first capturing group
            invoice_nr = match.group(1).strip()
            logger.debug(f"Found invoice number: {invoice_nr}")
            return invoice_nr

        logger.debug("Invoice number not found")
        return None

    def _extract_date(self, text: str) -> Optional[str]:
        """
        Extract and normalize date.

        Args:
            text: Text to search

        Returns:
            Date in ISO format (YYYY-MM-DD) or None if not found
        """
        pattern = self._compiled_patterns.get('date')
        if not pattern:
            logger.warning("No date pattern configured")
            return None

        match = pattern.search(text)
        if match:
            date_str = match.group(1).strip()
            # Normalize to ISO format
            normalized = normalize_date(date_str)
            logger.debug(f"Found date: {date_str} -> {normalized}")
            return normalized

        logger.debug("Date not found")
        return None

    def _extract_vendor(self, text: str) -> Optional[str]:
        """
        Extract vendor/supplier name.

        Args:
            text: Text to search

        Returns:
            Vendor name or None if not found
        """
        pattern = self._compiled_patterns.get('vendor')
        if not pattern:
            logger.warning("No vendor pattern configured")
            return None

        match = pattern.search(text)
        if match:
            vendor = match.group(1).strip()
            logger.debug(f"Found vendor: {vendor}")
            return vendor

        logger.debug("Vendor not found")
        return None

    def extract_all_matches(self, text: str, field: str) -> list:
        """
        Extract all matches for a field (not just first).

        Useful for debugging or when multiple values might be present.

        Args:
            text: Text to search
            field: Field name ('invoice_nr', 'date', 'vendor')

        Returns:
            List of all matches
        """
        pattern = self._compiled_patterns.get(field)
        if not pattern:
            return []

        matches = pattern.findall(text)
        return [m.strip() if isinstance(m, str) else m[0].strip() for m in matches]
