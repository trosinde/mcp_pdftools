"""
PDF protection processors.

This module handles the actual PDF encryption and permission setting
using PyPDF2.
"""

import logging
from pathlib import Path
from typing import Optional, List

from PyPDF2 import PdfReader, PdfWriter

from .models import PermissionLevel

logger = logging.getLogger(__name__)


# PyPDF2 permission flag mappings
# Based on PDF Reference, these are the permission bits
PERMISSION_FLAGS = {
    PermissionLevel.PRINT: 4,      # Bit 2: Print
    PermissionLevel.MODIFY: 8,     # Bit 3: Modify contents
    PermissionLevel.COPY: 16,      # Bit 4: Copy/extract text
    PermissionLevel.ANNOTATE: 32,  # Bit 5: Add/modify annotations
}


class PDFProtector:
    """
    Handles PDF encryption and permission setting.

    This class encapsulates the logic for loading a PDF, applying
    encryption with passwords, setting permissions, and writing
    the protected PDF to disk.
    """

    def __init__(self):
        """Initialize PDF protector."""
        self.writer = PdfWriter()
        self.reader: Optional[PdfReader] = None
        logger.debug("PDFProtector initialized")

    def load_pdf(self, path: Path) -> None:
        """
        Load a PDF file for protection.

        Args:
            path: Path to PDF file

        Raises:
            FileNotFoundError: If PDF file doesn't exist
            Exception: If PDF cannot be read
        """
        try:
            self.reader = PdfReader(str(path))
            logger.debug(f"Loading PDF from: {path}")

            # Copy all pages to writer
            for page_num, page in enumerate(self.reader.pages, 1):
                self.writer.add_page(page)
                logger.debug(f"Added page {page_num}")

            logger.info(f"Loaded {len(self.reader.pages)} pages from PDF")

        except FileNotFoundError:
            logger.error(f"PDF file not found: {path}")
            raise
        except Exception as e:
            logger.error(f"Failed to load PDF: {e}")
            raise Exception(f"Failed to load PDF: {e}") from e

    def apply_protection(
        self,
        user_password: Optional[str] = None,
        owner_password: Optional[str] = None,
        permissions: Optional[List[PermissionLevel]] = None
    ) -> None:
        """
        Apply encryption and permissions to loaded PDF.

        Args:
            user_password: Password to open PDF (optional)
            owner_password: Password to modify permissions (required)
            permissions: List of allowed permissions (default: all denied)

        Raises:
            ValueError: If no owner password provided
            Exception: If encryption fails
        """
        if not owner_password:
            raise ValueError("Owner password is required for encryption")

        try:
            # Calculate permission flags
            permission_flags = self._calculate_permission_flags(permissions)

            # NEVER log passwords!
            logger.info("Applying encryption and permissions to PDF")
            logger.debug(f"Permission flags: {permission_flags}")

            # Apply encryption
            # Note: PyPDF2 uses user_pwd for opening, owner_pwd for permissions
            self.writer.encrypt(
                user_password=user_password or "",
                owner_password=owner_password,
                use_128bit=True,
                permissions_flag=permission_flags
            )

            logger.info("Encryption applied successfully")

        except Exception as e:
            logger.error(f"Failed to apply protection: {e}")
            raise Exception(f"Failed to apply protection: {e}") from e

    def write(self, output_path: Path) -> None:
        """
        Write protected PDF to file.

        Args:
            output_path: Destination path

        Raises:
            Exception: If writing fails
        """
        try:
            logger.info(f"Writing protected PDF to: {output_path}")

            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)

            logger.info(f"Protected PDF written successfully: {output_path}")

        except Exception as e:
            logger.error(f"Failed to write protected PDF: {e}")
            raise Exception(f"Failed to write protected PDF: {e}") from e

    def _calculate_permission_flags(
        self,
        permissions: Optional[List[PermissionLevel]]
    ) -> int:
        """
        Calculate PyPDF2 permission flags from PermissionLevel list.

        Args:
            permissions: List of allowed permissions

        Returns:
            int: Combined permission flags
                 -1 = all permissions denied (most restrictive)
                 Positive = bitwise OR of allowed permission flags
        """
        if not permissions:
            logger.debug("No permissions specified, denying all")
            return -1  # All permissions denied

        # Calculate combined flags
        flags = 0
        for perm in permissions:
            flag = PERMISSION_FLAGS.get(perm, 0)
            flags |= flag
            logger.debug(f"Adding permission {perm.value}: flag {flag}")

        logger.debug(f"Final permission flags: {flags}")
        return flags
