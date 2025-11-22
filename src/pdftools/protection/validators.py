"""
Validators for PDF protection operations.

This module provides validation functions for passwords, permissions,
and file paths used in PDF protection.
"""

import logging
from pathlib import Path
from typing import List, Optional

from .models import PermissionLevel

logger = logging.getLogger(__name__)


def validate_input_file(file_path: Path) -> Path:
    """
    Validate input PDF file exists and is readable.

    Args:
        file_path: Path to input PDF file

    Returns:
        Normalized absolute path

    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If path is not a file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    logger.debug(f"Input file validated: {file_path}")
    return file_path.resolve()


def validate_output_path(output_path: Path) -> Path:
    """
    Validate output path is writable.

    Args:
        output_path: Path for output PDF

    Returns:
        Normalized absolute path

    Raises:
        ValueError: If parent directory doesn't exist
        PermissionError: If directory is not writable
    """
    output_path = output_path.resolve()

    # Check parent directory exists
    parent = output_path.parent
    if not parent.exists():
        raise ValueError(f"Output directory doesn't exist: {parent}")

    # Check parent directory is writable
    if not parent.is_dir():
        raise ValueError(f"Output parent is not a directory: {parent}")

    logger.debug(f"Output path validated: {output_path}")
    return output_path


def validate_passwords(
    user_password: Optional[str],
    owner_password: Optional[str]
) -> tuple[Optional[str], Optional[str]]:
    """
    Validate passwords meet requirements.

    Args:
        user_password: Password to open PDF
        owner_password: Password to modify permissions

    Returns:
        Tuple of (user_password, owner_password)

    Raises:
        ValueError: If no passwords provided or passwords are invalid
    """
    if not user_password and not owner_password:
        raise ValueError("At least one password (user or owner) must be provided")

    # Validate user password if provided
    if user_password is not None:
        if not isinstance(user_password, str):
            raise ValueError("User password must be a string")
        if len(user_password) == 0:
            raise ValueError("User password cannot be empty")
        # NEVER log passwords!
        logger.debug("User password provided")

    # Validate owner password if provided
    if owner_password is not None:
        if not isinstance(owner_password, str):
            raise ValueError("Owner password must be a string")
        if len(owner_password) == 0:
            raise ValueError("Owner password cannot be empty")
        # NEVER log passwords!
        logger.debug("Owner password provided")

    # If only user password provided, use it as owner password too
    if user_password and not owner_password:
        logger.debug("Using user password as owner password")
        owner_password = user_password

    return user_password, owner_password


def validate_permissions(
    permissions: Optional[List[PermissionLevel]]
) -> List[PermissionLevel]:
    """
    Validate permissions list.

    Args:
        permissions: List of permission levels

    Returns:
        Validated list of permissions (empty list if None)

    Raises:
        ValueError: If permissions contain invalid values
    """
    if permissions is None:
        logger.debug("No permissions specified, all will be denied")
        return []

    if not isinstance(permissions, list):
        raise ValueError("Permissions must be a list")

    # Validate each permission
    validated = []
    for perm in permissions:
        if not isinstance(perm, PermissionLevel):
            raise ValueError(
                f"Invalid permission type: {type(perm)}. "
                f"Expected PermissionLevel"
            )
        validated.append(perm)

    logger.debug(f"Permissions validated: {[p.value for p in validated]}")
    return validated


def generate_output_path(input_path: Path, custom_output: Optional[Path]) -> Path:
    """
    Generate output path for protected PDF.

    Args:
        input_path: Input PDF path
        custom_output: Custom output path (optional)

    Returns:
        Output path (custom or generated)
    """
    if custom_output:
        return custom_output

    # Generate default output path: {input}_protected.pdf
    stem = input_path.stem
    suffix = input_path.suffix
    parent = input_path.parent

    output_name = f"{stem}_protected{suffix}"
    output_path = parent / output_name

    logger.debug(f"Generated output path: {output_path}")
    return output_path
