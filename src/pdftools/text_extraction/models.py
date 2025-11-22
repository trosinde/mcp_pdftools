"""Data models for PDF text extraction."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ExtractionMode(str, Enum):
    """Text extraction modes."""
    SIMPLE = "simple"           # Simple text extraction
    LAYOUT = "layout"           # Layout-preserving extraction
    PER_PAGE = "per_page"       # One file per page
    STRUCTURED = "structured"   # JSON with metadata


class OutputFormat(str, Enum):
    """Output formats for extracted text."""
    TXT = "txt"
    JSON = "json"
    MARKDOWN = "markdown"


@dataclass
class PageText:
    """Text content from a single PDF page."""
    page_num: int
    text: str
    char_count: int
    metadata: dict = field(default_factory=dict)


@dataclass
class ExtractionConfig:
    """Configuration for text extraction operation."""
    input_path: Path
    output_path: Optional[Path] = None
    mode: ExtractionMode = ExtractionMode.SIMPLE
    format: OutputFormat = OutputFormat.TXT
    pages: Optional[list[int]] = None
    encoding: str = "utf-8"
    include_metadata: bool = False
    verbose: bool = False

    def __post_init__(self):
        """Validate configuration."""
        if isinstance(self.input_path, str):
            self.input_path = Path(self.input_path)
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)

        # Validate mode-specific requirements
        if self.mode == ExtractionMode.PER_PAGE:
            if self.output_path and self.output_path.exists() and self.output_path.is_file():
                raise ValueError(
                    "PER_PAGE mode requires output_path to be a directory"
                )


@dataclass
class ExtractionResult:
    """Result of text extraction operation."""
    status: str  # "success" or "error"
    text: Optional[str] = None  # For SIMPLE, LAYOUT modes
    pages: list[PageText] = field(default_factory=list)  # For all modes
    metadata: dict = field(default_factory=dict)  # PDF metadata
    char_count: int = 0
    message: Optional[str] = None

    def __post_init__(self):
        """Calculate total character count."""
        if self.text and not self.char_count:
            self.char_count = len(self.text)
        elif self.pages and not self.char_count:
            self.char_count = sum(p.char_count for p in self.pages)
