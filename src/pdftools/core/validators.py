"""
Validation utilities for PDF Tools
"""

import os
from pathlib import Path
from typing import Union

from .exceptions import (
    PDFNotFoundError,
    InvalidPathError,
    InvalidParameterError,
    InsufficientPermissionsError
)


def validate_pdf_path(
    path: Union[str, Path],
    must_exist: bool = True,
    check_readable: bool = True
) -> Path:
    """
    Validate a PDF file path

    Args:
        path: Path to validate
        must_exist: If True, raises error if path doesn't exist
        check_readable: If True, checks if file is readable

    Returns:
        Normalized Path object

    Raises:
        InvalidPathError: If path is invalid
        PDFNotFoundError: If file doesn't exist (when must_exist=True)
        InsufficientPermissionsError: If file is not readable
    """
    if not path:
        raise InvalidPathError("", "Path cannot be empty")

    # Convert to Path object
    path_obj = Path(path)

    # Normalize path
    try:
        path_obj = path_obj.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(str(path), f"Cannot resolve path: {e}")

    # Check if exists
    if must_exist and not path_obj.exists():
        raise PDFNotFoundError(str(path_obj))

    # Check if it's a file (not directory)
    if must_exist and path_obj.exists() and not path_obj.is_file():
        raise InvalidPathError(str(path_obj), "Path is not a file")

    # Check extension
    if path_obj.suffix.lower() != '.pdf':
        raise InvalidPathError(
            str(path_obj),
            f"File must be a PDF (got: {path_obj.suffix})"
        )

    # Check readable
    if check_readable and must_exist and not os.access(path_obj, os.R_OK):
        raise InsufficientPermissionsError(str(path_obj), "read")

    return path_obj


def validate_output_path(
    path: Union[str, Path],
    create_dirs: bool = True,
    overwrite: bool = True
) -> Path:
    """
    Validate an output file path

    Args:
        path: Output path to validate
        create_dirs: If True, creates parent directories if they don't exist
        overwrite: If False, raises error if file already exists

    Returns:
        Normalized Path object

    Raises:
        InvalidPathError: If path is invalid
        FileExistsError: If file exists and overwrite=False
        InsufficientPermissionsError: If directory is not writable
    """
    if not path:
        raise InvalidPathError("", "Output path cannot be empty")

    # Convert to Path object
    path_obj = Path(path)

    # Normalize path
    try:
        path_obj = path_obj.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(str(path), f"Cannot resolve path: {e}")

    # Check if file exists
    if not overwrite and path_obj.exists():
        raise FileExistsError(f"Output file already exists: {path_obj}")

    # Check parent directory
    parent_dir = path_obj.parent

    if not parent_dir.exists():
        if create_dirs:
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise InsufficientPermissionsError(
                    str(parent_dir),
                    f"create directory: {e}"
                )
        else:
            raise InvalidPathError(
                str(path_obj),
                f"Parent directory does not exist: {parent_dir}"
            )

    # Check if parent directory is writable
    if not os.access(parent_dir, os.W_OK):
        raise InsufficientPermissionsError(str(parent_dir), "write")

    return path_obj


def validate_directory(
    path: Union[str, Path],
    must_exist: bool = True,
    create_if_missing: bool = False
) -> Path:
    """
    Validate a directory path

    Args:
        path: Directory path to validate
        must_exist: If True, raises error if directory doesn't exist
        create_if_missing: If True, creates directory if it doesn't exist

    Returns:
        Normalized Path object

    Raises:
        InvalidPathError: If path is invalid or not a directory
        InsufficientPermissionsError: If directory operations fail
    """
    if not path:
        raise InvalidPathError("", "Directory path cannot be empty")

    # Convert to Path object
    path_obj = Path(path)

    # Normalize path
    try:
        path_obj = path_obj.resolve()
    except (OSError, RuntimeError) as e:
        raise InvalidPathError(str(path), f"Cannot resolve path: {e}")

    # Check if exists
    if not path_obj.exists():
        if create_if_missing:
            try:
                path_obj.mkdir(parents=True, exist_ok=True)
            except (OSError, PermissionError) as e:
                raise InsufficientPermissionsError(
                    str(path_obj),
                    f"create directory: {e}"
                )
        elif must_exist:
            raise InvalidPathError(str(path_obj), "Directory does not exist")

    # Check if it's actually a directory
    if path_obj.exists() and not path_obj.is_dir():
        raise InvalidPathError(str(path_obj), "Path is not a directory")

    return path_obj


def validate_positive_int(value: int, param_name: str, min_value: int = 1) -> int:
    """
    Validate a positive integer parameter

    Args:
        value: Value to validate
        param_name: Name of parameter (for error messages)
        min_value: Minimum allowed value

    Returns:
        Validated integer

    Raises:
        InvalidParameterError: If value is invalid
    """
    if not isinstance(value, int):
        raise InvalidParameterError(
            param_name,
            value,
            f"Must be an integer, got {type(value).__name__}"
        )

    if value < min_value:
        raise InvalidParameterError(
            param_name,
            value,
            f"Must be >= {min_value}"
        )

    return value


def validate_string_not_empty(value: str, param_name: str) -> str:
    """
    Validate that a string is not empty

    Args:
        value: String to validate
        param_name: Name of parameter (for error messages)

    Returns:
        Validated string

    Raises:
        InvalidParameterError: If string is empty or not a string
    """
    if not isinstance(value, str):
        raise InvalidParameterError(
            param_name,
            value,
            f"Must be a string, got {type(value).__name__}"
        )

    if not value.strip():
        raise InvalidParameterError(
            param_name,
            value,
            "String cannot be empty"
        )

    return value
