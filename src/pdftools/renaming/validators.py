"""
Validators for invoice renaming templates and patterns.

This module provides validation functions for naming templates
and regex patterns used in invoice data extraction.
"""

import re
from typing import Dict, Set


class InvalidTemplateError(ValueError):
    """Raised when a naming template is invalid."""
    pass


class InvalidPatternError(ValueError):
    """Raised when a regex pattern is invalid."""
    pass


# Valid placeholders for templates
VALID_PLACEHOLDERS: Set[str] = {
    'vendor',
    'invoice_nr',
    'date',
    'year',
    'month',
    'day'
}


def validate_template(template: str) -> None:
    """
    Validate a naming template.

    Args:
        template: Template string with placeholders (e.g., "{vendor}_{date}.pdf")

    Raises:
        InvalidTemplateError: If template contains invalid placeholders

    Example:
        >>> validate_template("{vendor}_{invoice_nr}.pdf")  # OK
        >>> validate_template("{invalid_field}.pdf")  # Raises InvalidTemplateError
    """
    if not template:
        raise InvalidTemplateError("Template cannot be empty")

    # Extract placeholders from template
    placeholders = re.findall(r'\{(\w+)\}', template)

    if not placeholders:
        raise InvalidTemplateError(
            "Template must contain at least one placeholder"
        )

    # Check for invalid placeholders
    invalid = set(placeholders) - VALID_PLACEHOLDERS
    if invalid:
        raise InvalidTemplateError(
            f"Invalid placeholders: {', '.join(sorted(invalid))}. "
            f"Valid placeholders are: {', '.join(sorted(VALID_PLACEHOLDERS))}"
        )


def validate_patterns(patterns: Dict[str, str]) -> None:
    """
    Validate regex patterns.

    Args:
        patterns: Dictionary mapping field names to regex patterns

    Raises:
        InvalidPatternError: If any pattern is invalid regex

    Example:
        >>> patterns = {"invoice_nr": r"Invoice\\s+(\\d+)"}
        >>> validate_patterns(patterns)  # OK
    """
    if not patterns:
        raise InvalidPatternError("Patterns dictionary cannot be empty")

    for field_name, pattern in patterns.items():
        if not pattern:
            raise InvalidPatternError(
                f"Pattern for field '{field_name}' cannot be empty"
            )

        # Try to compile the regex
        try:
            re.compile(pattern)
        except re.error as e:
            raise InvalidPatternError(
                f"Invalid regex pattern for field '{field_name}': {pattern}. "
                f"Error: {str(e)}"
            ) from e

        # Check that pattern has at least one capturing group
        if not re.search(r'\([^?]', pattern):
            raise InvalidPatternError(
                f"Pattern for field '{field_name}' must contain at least "
                f"one capturing group: {pattern}"
            )


def sanitize_filename(name: str, max_length: int = 255) -> str:
    """
    Remove invalid characters from filename.

    This function removes characters that are invalid in filenames
    across Windows, Linux, and macOS platforms.

    Args:
        name: Filename to sanitize
        max_length: Maximum filename length (default: 255)

    Returns:
        Sanitized filename

    Example:
        >>> sanitize_filename("Test/Corp")
        'Test_Corp'
        >>> sanitize_filename("Invoice: 123")
        'Invoice_ 123'
    """
    if not name:
        return "unknown"

    # Remove/replace invalid characters for cross-platform compatibility
    # Invalid chars: < > : " / \ | ? *
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)

    # Remove control characters (ASCII < 32)
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32)

    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')

    # Replace multiple spaces/underscores with single
    sanitized = re.sub(r'[\s_]+', '_', sanitized)

    # Ensure not empty
    if not sanitized:
        sanitized = "unknown"

    # Truncate if too long (reserve space for extension)
    if len(sanitized) > max_length - 10:  # Reserve 10 chars for extension + suffix
        sanitized = sanitized[:max_length - 10]

    return sanitized


def validate_output_path(path: str) -> None:
    """
    Validate output directory path.

    Args:
        path: Directory path to validate

    Raises:
        ValueError: If path is invalid or not writable

    Example:
        >>> validate_output_path("/tmp")  # OK on Unix
        >>> validate_output_path("/invalid/path")  # May raise ValueError
    """
    from pathlib import Path

    if not path:
        raise ValueError("Output path cannot be empty")

    output_dir = Path(path)

    # Check if parent directory exists (if path includes subdirs)
    if output_dir.parent != output_dir and not output_dir.parent.exists():
        raise ValueError(
            f"Parent directory does not exist: {output_dir.parent}"
        )
