"""
Utility functions for PDF Tools
"""

import os
import logging
from pathlib import Path
from typing import Union

from .exceptions import InvalidPathError, InsufficientPermissionsError


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a file path (expand user, resolve symlinks, absolute path)

    Args:
        path: Path to normalize

    Returns:
        Normalized Path object

    Raises:
        InvalidPathError: If path cannot be normalized
    """
    if not path:
        raise InvalidPathError("", "Path cannot be empty")

    try:
        # Convert to Path object
        path_obj = Path(path)

        # Expand user directory (~)
        path_obj = path_obj.expanduser()

        # Resolve to absolute path and resolve symlinks
        path_obj = path_obj.resolve()

        return path_obj

    except (OSError, RuntimeError) as e:
        raise InvalidPathError(str(path), f"Cannot normalize path: {e}")


def ensure_directory_exists(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, create if it doesn't

    Args:
        path: Directory path

    Returns:
        Path object of the directory

    Raises:
        InsufficientPermissionsError: If directory cannot be created
        InvalidPathError: If path is not a directory
    """
    path_obj = normalize_path(path)

    if not path_obj.exists():
        try:
            path_obj.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError) as e:
            raise InsufficientPermissionsError(
                str(path_obj),
                f"create directory: {e}"
            )

    if not path_obj.is_dir():
        raise InvalidPathError(str(path_obj), "Path is not a directory")

    return path_obj


def get_file_size_mb(path: Union[str, Path]) -> float:
    """
    Get file size in megabytes

    Args:
        path: File path

    Returns:
        File size in MB (rounded to 2 decimals)
    """
    path_obj = Path(path)
    size_bytes = path_obj.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    return round(size_mb, 2)


def generate_output_path(
    input_path: Union[str, Path],
    suffix: str,
    extension: str = ".pdf",
    output_dir: Union[str, Path, None] = None
) -> Path:
    """
    Generate an output file path based on input file

    Args:
        input_path: Input file path
        suffix: Suffix to add before extension (e.g., "_merged", "_split")
        extension: File extension (default: ".pdf")
        output_dir: Optional output directory (default: same as input)

    Returns:
        Generated output path

    Example:
        >>> generate_output_path("input.pdf", "_merged")
        Path("input_merged.pdf")
        >>> generate_output_path("input.pdf", "_ocr", output_dir="/tmp")
        Path("/tmp/input_ocr.pdf")
    """
    input_path_obj = Path(input_path)

    # Get filename without extension
    stem = input_path_obj.stem

    # Determine output directory
    if output_dir:
        out_dir = Path(output_dir)
    else:
        out_dir = input_path_obj.parent

    # Generate filename
    filename = f"{stem}{suffix}{extension}"

    return out_dir / filename


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Union[str, Path, None] = None
) -> logging.Logger:
    """
    Setup a logger with consistent formatting

    Args:
        name: Logger name
        level: Logging level
        log_file: Optional log file path

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Formatter
    formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def safe_file_operation(func):
    """
    Decorator for safe file operations with proper error handling

    Example:
        @safe_file_operation
        def process_pdf(path):
            # Your code here
            pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            from .exceptions import PDFNotFoundError
            raise PDFNotFoundError(str(e.filename))
        except PermissionError as e:
            raise InsufficientPermissionsError(str(e.filename), "access")
        except Exception as e:
            from .exceptions import PDFProcessingError
            raise PDFProcessingError(f"Unexpected error: {e}")

    return wrapper
