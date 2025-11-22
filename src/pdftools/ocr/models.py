"""
Data models for OCR operations
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from enum import Enum


class OCRLanguage(str, Enum):
    """
    Supported OCR languages

    Attributes:
        GERMAN: German language (deu)
        ENGLISH: English language (eng)
        FRENCH: French language (fra)
        ITALIAN: Italian language (ita)
        SPANISH: Spanish language (spa)
    """
    GERMAN = "deu"
    ENGLISH = "eng"
    FRENCH = "fra"
    ITALIAN = "ita"
    SPANISH = "spa"


class OutputMode(str, Enum):
    """
    Output format modes

    Attributes:
        TXT: Plain text output
        PDF: PDF with searchable text layer
        JSON: Structured JSON output
    """
    TXT = "txt"
    PDF = "pdf"
    JSON = "json"


@dataclass
class OCRConfig:
    """
    Configuration for OCR operation

    Attributes:
        pages: Specific pages to process (None = all pages)
        dpi: DPI for PDF to image conversion (default: 300)
        tesseract_config: Additional Tesseract configuration string
        progress_callback: Optional callback function(current, total)
        verbose: Enable verbose logging
    """
    pages: Optional[List[int]] = None
    dpi: int = 300
    tesseract_config: Optional[str] = None
    progress_callback: Optional[Callable[[int, int], None]] = None
    verbose: bool = False


@dataclass
class OCRResult:
    """
    Result of OCR operation

    Attributes:
        status: 'success', 'error', or 'partial'
        output_path: Path to the created output file
        message: Status message or error description
        pages_processed: Number of pages successfully processed
        total_pages: Total number of pages in document
        metadata: Additional metadata (avg_confidence, processing_time, etc.)
    """
    status: str  # 'success' | 'error' | 'partial'
    output_path: Optional[Path] = None
    message: str = ""
    pages_processed: int = 0
    total_pages: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Returns True if OCR was successful"""
        return self.status == 'success'
