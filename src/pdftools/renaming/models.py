"""
Data models for invoice renaming functionality.

This module provides dataclasses for representing invoice data,
configuration, and results of rename operations.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any


@dataclass
class InvoiceData:
    """
    Represents extracted invoice data.

    Attributes:
        invoice_number: Invoice/bill number
        date: Invoice date in ISO format (YYYY-MM-DD)
        vendor: Vendor/supplier name
    """

    invoice_number: Optional[str] = None
    date: Optional[str] = None
    vendor: Optional[str] = None

    @property
    def year(self) -> Optional[str]:
        """
        Extract year from date if available.

        Returns:
            Year as string (YYYY) or None
        """
        if self.date:
            try:
                return self.date.split('-')[0]
            except (IndexError, AttributeError):
                return None
        return None

    @property
    def month(self) -> Optional[str]:
        """
        Extract month from date if available.

        Returns:
            Month as string (MM) or None
        """
        if self.date:
            try:
                return self.date.split('-')[1]
            except (IndexError, AttributeError):
                return None
        return None

    @property
    def day(self) -> Optional[str]:
        """
        Extract day from date if available.

        Returns:
            Day as string (DD) or None
        """
        if self.date:
            try:
                return self.date.split('-')[2]
            except (IndexError, AttributeError):
                return None
        return None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Convert to dictionary.

        Returns:
            Dictionary with all fields including computed properties
        """
        return {
            'invoice_number': self.invoice_number,
            'date': self.date,
            'vendor': self.vendor,
            'year': self.year,
            'month': self.month,
            'day': self.day
        }


@dataclass
class RenameConfig:
    """
    Configuration for rename operations.

    Attributes:
        fallback_name: Name to use when data extraction fails
        handle_duplicates: Add numeric suffix if target file exists
        verbose: Enable verbose output
        max_filename_length: Maximum length for generated filenames
    """

    fallback_name: str = "renamed"
    handle_duplicates: bool = True
    verbose: bool = False
    max_filename_length: int = 255


@dataclass
class RenameResult:
    """
    Result of a rename operation.

    Attributes:
        status: Operation status ('success', 'error', 'skipped')
        old_name: Original filename
        new_name: New filename (None if operation failed)
        extracted_data: Invoice data extracted from PDF
        message: Status message or error description
        dry_run: Whether this was a simulation
        metadata: Additional metadata about the operation
    """

    status: str
    old_name: str
    new_name: Optional[str] = None
    extracted_data: Optional[InvoiceData] = None
    message: str = ""
    dry_run: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """
        Check if operation was successful.

        Returns:
            True if status is 'success'
        """
        return self.status == 'success'

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary.

        Returns:
            Dictionary representation of result
        """
        return {
            'status': self.status,
            'old_name': self.old_name,
            'new_name': self.new_name,
            'extracted_data': self.extracted_data.to_dict() if self.extracted_data else None,
            'message': self.message,
            'dry_run': self.dry_run,
            'success': self.success,
            'metadata': self.metadata
        }
