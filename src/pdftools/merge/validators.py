"""
Validation functions for PDF merge operations
"""

from pathlib import Path
from typing import List

from ..core.validators import validate_pdf_path
from ..core.exceptions import InvalidParameterError


def validate_input_files(files: List[Path], must_exist: bool = True) -> List[Path]:
    """
    Validate a list of input PDF files

    Args:
        files: List of file paths to validate
        must_exist: If True, checks that all files exist

    Returns:
        List of validated Path objects

    Raises:
        InvalidParameterError: If less than 2 files provided
        PDFNotFoundError: If any file doesn't exist (when must_exist=True)
        InvalidPathError: If any path is invalid

    Example:
        >>> files = validate_input_files([Path("f1.pdf"), Path("f2.pdf")])
        >>> len(files)
        2
    """
    if not files:
        raise InvalidParameterError(
            "files",
            files,
            "File list cannot be empty"
        )

    if len(files) < 2:
        raise InvalidParameterError(
            "files",
            files,
            f"At least 2 PDF files required for merging, got {len(files)}"
        )

    # Validate each file
    validated_files = []
    for file_path in files:
        validated_path = validate_pdf_path(
            file_path,
            must_exist=must_exist,
            check_readable=True
        )
        validated_files.append(validated_path)

    return validated_files
