"""
Core functionality for PDF protection.

This module provides the main protect_pdf function that orchestrates
the entire PDF protection process.
"""

import logging
from pathlib import Path
from typing import Optional, List

from .models import ProtectionConfig, ProtectionResult, PermissionLevel
from .validators import (
    validate_input_file,
    validate_output_path,
    validate_passwords,
    validate_permissions,
    generate_output_path
)
from .processors import PDFProtector

logger = logging.getLogger(__name__)


def protect_pdf(
    input_path: Path,
    output_path: Optional[Path] = None,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
    permissions: Optional[List[PermissionLevel]] = None
) -> ProtectionResult:
    """
    Protect a PDF file with password encryption and permissions.

    This function encrypts a PDF file with optional user and owner passwords,
    and sets permissions for printing, copying, modifying, and annotating.

    Args:
        input_path: Path to input PDF file
        output_path: Output path for protected PDF.
                    If None, creates '{input}_protected.pdf' in same directory.
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        permissions: List of allowed permissions (optional, default: all denied)

    Returns:
        ProtectionResult: Object containing status, output path, and metadata

    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If no passwords provided or invalid parameters
        Exception: If protection fails

    Example:
        >>> result = protect_pdf(
        ...     input_path=Path("document.pdf"),
        ...     user_password="secret123",
        ...     permissions=[PermissionLevel.PRINT]
        ... )
        >>> print(result.status)
        'success'

        >>> result = protect_pdf(
        ...     input_path=Path("contract.pdf"),
        ...     output_path=Path("secure_contract.pdf"),
        ...     user_password="open123",
        ...     owner_password="admin456",
        ...     permissions=[PermissionLevel.PRINT, PermissionLevel.COPY]
        ... )
    """
    try:
        logger.info(f"Starting PDF protection: {input_path}")

        # Step 1: Validate input file
        validated_input = validate_input_file(input_path)

        # Step 2: Generate/validate output path
        output = generate_output_path(validated_input, output_path)
        validated_output = validate_output_path(output)

        # Step 3: Validate passwords
        valid_user_pwd, valid_owner_pwd = validate_passwords(
            user_password,
            owner_password
        )

        # Step 4: Validate permissions
        valid_permissions = validate_permissions(permissions)

        # Step 5: Create protector and load PDF
        protector = PDFProtector()
        protector.load_pdf(validated_input)

        # Step 6: Apply protection
        protector.apply_protection(
            user_password=valid_user_pwd,
            owner_password=valid_owner_pwd,
            permissions=valid_permissions
        )

        # Step 7: Write protected PDF
        protector.write(validated_output)

        # Step 8: Create success result
        logger.info(f"PDF protection completed successfully: {validated_output}")
        return ProtectionResult.create_success(
            output_path=validated_output,
            permissions=valid_permissions
        )

    except FileNotFoundError as e:
        error_msg = f"PDF file not found: {input_path}"
        logger.error(error_msg)
        return ProtectionResult.create_error(error_msg)

    except ValueError as e:
        error_msg = str(e)
        logger.error(f"Validation error: {error_msg}")
        return ProtectionResult.create_error(error_msg)

    except Exception as e:
        error_msg = f"Failed to protect PDF: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return ProtectionResult.create_error(error_msg)


def protect_pdf_with_config(
    input_path: Path,
    output_path: Optional[Path] = None,
    config: Optional[ProtectionConfig] = None
) -> ProtectionResult:
    """
    Protect a PDF file using a ProtectionConfig object.

    This is a convenience function that accepts a config object instead
    of individual parameters.

    Args:
        input_path: Path to input PDF file
        output_path: Output path for protected PDF (optional)
        config: Protection configuration (optional, default config if None)

    Returns:
        ProtectionResult: Object containing status, output path, and metadata

    Example:
        >>> config = ProtectionConfig(
        ...     user_password="secret",
        ...     owner_password="admin",
        ...     permissions=[PermissionLevel.PRINT]
        ... )
        >>> result = protect_pdf_with_config(
        ...     input_path=Path("document.pdf"),
        ...     config=config
        ... )
    """
    if config is None:
        config = ProtectionConfig()

    return protect_pdf(
        input_path=input_path,
        output_path=output_path,
        user_password=config.user_password,
        owner_password=config.owner_password,
        permissions=config.permissions
    )
