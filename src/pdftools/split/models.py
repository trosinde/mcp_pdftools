"""
Data models for PDF Split module.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

from pdftools.core.exceptions import ValidationError


class SplitMode(str, Enum):
    """PDF split modes."""

    PAGES = "pages"              # One file per page
    RANGES = "ranges"            # User-defined page ranges
    PARTS = "parts"              # N equal parts
    SPECIFIC_PAGES = "specific"  # Specific page numbers


@dataclass
class SplitConfig:
    """Configuration for PDF split operation."""

    # Required
    input_path: Path

    # Optional
    output_dir: Path = Path(".")
    mode: SplitMode = SplitMode.PAGES
    prefix: Optional[str] = None
    verbose: bool = False

    # Mode-specific parameters
    ranges: Optional[list[tuple[int, int]]] = None
    pages: Optional[list[int]] = None
    num_parts: Optional[int] = None

    def __post_init__(self):
        """Validate configuration after initialization."""
        # Convert string paths to Path objects
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.output_dir, str):
            self.output_dir = Path(self.output_dir)

        # Set default prefix from input filename
        if self.prefix is None:
            self.prefix = self.input_path.stem

        # Validate mode-specific parameters
        if self.mode == SplitMode.RANGES and not self.ranges:
            raise ValidationError("ranges required for RANGES mode")

        if self.mode == SplitMode.PARTS and not self.num_parts:
            raise ValidationError("num_parts required for PARTS mode")

        if self.mode == SplitMode.SPECIFIC_PAGES and not self.pages:
            raise ValidationError("pages required for SPECIFIC_PAGES mode")

        # Validate num_parts is positive
        if self.num_parts is not None and self.num_parts < 1:
            raise ValidationError(f"num_parts must be >= 1, got {self.num_parts}")


@dataclass
class SplitResult:
    """Result of PDF split operation."""

    status: str                              # 'success' | 'error'
    num_files: int = 0
    output_files: list[Path] = field(default_factory=list)
    message: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Check if operation was successful."""
        return self.status == 'success'

    def __str__(self) -> str:
        """Human-readable summary."""
        if self.success:
            return f"Split successful: {self.num_files} files created"
        else:
            return f"Split failed: {self.message}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"SplitResult(status='{self.status}', "
            f"num_files={self.num_files}, "
            f"success={self.success})"
        )
