"""
Common utilities for all CLI tools
"""

import sys
import logging
from typing import Optional

# ANSI Color Codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def print_success(message: str, use_color: bool = True) -> None:
    """
    Print success message with green checkmark

    Args:
        message: Success message to print
        use_color: Whether to use ANSI colors (default: True)

    Example:
        >>> print_success("File processed successfully")
        ✓ File processed successfully
    """
    if use_color:
        print(f"{GREEN}✓{RESET} {message}")
    else:
        print(f"✓ {message}")


def print_error(message: str, use_color: bool = True) -> None:
    """
    Print error message with red cross to stderr

    Args:
        message: Error message to print
        use_color: Whether to use ANSI colors (default: True)

    Example:
        >>> print_error("File not found")
        ✗ File not found
    """
    if use_color:
        print(f"{RED}✗{RESET} {message}", file=sys.stderr)
    else:
        print(f"✗ {message}", file=sys.stderr)


def print_warning(message: str, use_color: bool = True) -> None:
    """
    Print warning message with yellow warning sign

    Args:
        message: Warning message to print
        use_color: Whether to use ANSI colors (default: True)

    Example:
        >>> print_warning("File might be corrupted")
        ⚠ File might be corrupted
    """
    if use_color:
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"⚠ {message}")


def setup_logging(verbose: bool) -> None:
    """
    Setup logging based on verbose flag

    Args:
        verbose: If True, set log level to DEBUG, otherwise WARNING
    """
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )


def handle_keyboard_interrupt() -> None:
    """
    Handle Ctrl+C gracefully and exit with code 130
    """
    print_warning("\nOperation cancelled by user")
    sys.exit(130)  # Standard exit code for SIGINT


def create_stub_message(tool_name: str, feature_name: str) -> str:
    """
    Create 'coming soon' message for stub tools

    Args:
        tool_name: Name of the CLI tool (e.g., "pdfsplit")
        feature_name: Human-readable feature name (e.g., "PDF Split")

    Returns:
        Formatted message string explaining the feature is not yet implemented

    Example:
        >>> msg = create_stub_message("pdfsplit", "PDF Split")
        >>> print(msg)
        pdfsplit - PDF Split
        ...
    """
    return f"""
{tool_name} - {feature_name}

⚠ This feature is not yet implemented.

The core functionality needs to be developed first.
Check the project roadmap for implementation status.

To contribute or track progress:
- See docs/requirements/ for feature requirements
- Check docs/TRACEABILITY_MATRIX.md for status
- Review docs/DEVELOPMENT_PROCESS.md for the development workflow

For now, you can use the Python API if the core module exists:
    from pdftools.{tool_name.replace('pdf', '').replace('util', '')} import ...

To implement this feature, follow the 9-phase development process:
1. Create requirement document (REQ-XXX)
2. Team review
3. Create design document (DESIGN-XXX)
4. Architecture review
5. Implementation
6. Code review
7. Testing
8. Test report (TEST-XXX)
9. Release decision

See docs/DEVELOPMENT_PROCESS.md for details.
"""
