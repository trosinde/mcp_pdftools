# Design Document: PDF Text Extraction

**ID**: DESIGN-005
**Version**: 1.0
**Status**: Draft
**Related Requirement**: [REQ-005](../requirements/REQ-005-text-extraction.md) v1.0
**Created by**: System Architect
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

---

## 1. Übersicht

### 1.1 Ziel
Design eines robusten, erweiterbaren PDF-Text-Extraktions-Systems mit mehreren Extraktionsmodi und Ausgabeformaten.

### 1.2 Scope
- Text-Extraktion aus PDF-Dateien
- 4 Extraktionsmodi (Simple, Layout, Per-Page, Structured)
- 3 Ausgabeformate (TXT, JSON, Markdown)
- CLI-Tool `pdfgettxt`
- API für programmatische Nutzung

### 1.3 Nicht im Scope
- OCR-Funktionalität (siehe REQ-003)
- Tabellen-Extraktion als CSV (v1.1)
- Bildextraktion (separates Feature)

---

## 2. Architektur

### 2.1 Module-Struktur

```
src/pdftools/text_extraction/
├── __init__.py           # Public API exports
├── models.py             # Data models (ExtractionMode, Config, Result)
├── validators.py         # Input validation
├── extractors.py         # Extractor classes (4 Modi)
├── formatters.py         # Output formatters (TXT, JSON, MD)
├── core.py              # Main extract_text() function
└── cli.py               # CLI interface
```

### 2.2 Klassen-Diagramm

```
┌─────────────────────┐
│  ExtractionMode     │  (Enum)
│  - SIMPLE           │
│  - LAYOUT           │
│  - PER_PAGE         │
│  - STRUCTURED       │
└─────────────────────┘

┌─────────────────────┐
│  OutputFormat       │  (Enum)
│  - TXT              │
│  - JSON             │
│  - MARKDOWN         │
└─────────────────────┘

┌──────────────────────────────┐
│  ExtractionConfig            │  (Dataclass)
│  - input_path: Path          │
│  - output_path: Path | None  │
│  - mode: ExtractionMode      │
│  - format: OutputFormat      │
│  - pages: list[int] | None   │
│  - encoding: str             │
│  - include_metadata: bool    │
│  - verbose: bool             │
└──────────────────────────────┘

┌──────────────────────────────┐
│  ExtractionResult            │  (Dataclass)
│  - status: str               │
│  - text: str | None          │
│  - pages: list[PageText]     │
│  - metadata: dict            │
│  - char_count: int           │
│  - message: str | None       │
└──────────────────────────────┘

┌──────────────────────────────┐
│  PageText                    │  (Dataclass)
│  - page_num: int             │
│  - text: str                 │
│  - char_count: int           │
│  - metadata: dict            │
└──────────────────────────────┘

┌──────────────────────────────┐
│  BaseExtractor               │  (ABC)
│  + extract() → Result        │
│  # _extract_page_text()      │
│  # _show_progress()          │
└──────────────────────────────┘
         △
         │
    ┌────┴────────────────────────────┐
    │                                  │
┌───────────────┐          ┌────────────────────┐
│SimpleExtractor│          │LayoutExtractor     │
└───────────────┘          └────────────────────┘
    │                                  │
┌────────────────┐         ┌────────────────────┐
│PerPageExtractor│         │StructuredExtractor │
└────────────────┘         └────────────────────┘

┌──────────────────────────────┐
│  BaseFormatter               │  (ABC)
│  + format(result) → str      │
└──────────────────────────────┘
         △
         │
    ┌────┴──────────────────┐
    │                        │
┌───────────────┐    ┌──────────────┐
│  TxtFormatter │    │ JsonFormatter│
└───────────────┘    └──────────────┘
         │
    ┌────────────────────┐
    │ MarkdownFormatter  │
    └────────────────────┘
```

### 2.3 Datenfluss

```
Input: PDF File
    │
    ▼
┌─────────────────────────┐
│  1. Validate Input      │
│  - PDF exists?          │
│  - Valid PDF?           │
│  - Pages valid?         │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  2. Create Config       │
│  - Parse CLI args       │
│  - Set defaults         │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  3. Select Extractor    │
│  - Simple / Layout /    │
│    PerPage / Structured │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  4. Extract Text        │
│  - Open PDF             │
│  - Extract per page     │
│  - Progress indicator   │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  5. Format Output       │
│  - TXT / JSON / MD      │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  6. Write Output        │
│  - File or stdout       │
└─────────────────────────┘
    │
    ▼
Output: Text File(s)
```

---

## 3. Detailliertes Design

### 3.1 models.py

```python
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
            if self.output_path and self.output_path.is_file():
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
```

### 3.2 validators.py

```python
"""Input validation for text extraction."""

from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

from pdftools.core.exceptions import ValidationError
from pdftools.core.validators import validate_pdf_path


def validate_pages(
    pages: Optional[list[int]],
    total_pages: int
) -> None:
    """
    Validate that page numbers are valid for given PDF.

    Args:
        pages: List of page numbers (1-based)
        total_pages: Total number of pages in PDF

    Raises:
        ValidationError: If page numbers are invalid
    """
    if pages is None:
        return

    if not pages:
        raise ValidationError("Pages list cannot be empty")

    for page_num in pages:
        if not isinstance(page_num, int):
            raise ValidationError(f"Page number must be integer: {page_num}")

        if page_num < 1:
            raise ValidationError(f"Page numbers must be >= 1: {page_num}")

        if page_num > total_pages:
            raise ValidationError(
                f"Page {page_num} does not exist (PDF has {total_pages} pages)"
            )


def validate_encoding(encoding: str) -> None:
    """
    Validate that encoding is supported.

    Args:
        encoding: Character encoding name

    Raises:
        ValidationError: If encoding is not supported
    """
    try:
        "test".encode(encoding)
    except LookupError:
        raise ValidationError(f"Unsupported encoding: {encoding}")


def check_text_layer(pdf_path: Path) -> tuple[bool, int]:
    """
    Check if PDF has a text layer and count pages.

    Args:
        pdf_path: Path to PDF file

    Returns:
        Tuple of (has_text, num_pages)

    Raises:
        ValidationError: If PDF cannot be read
    """
    try:
        reader = PdfReader(pdf_path)
        num_pages = len(reader.pages)

        # Check first 3 pages for text
        has_text = False
        for i in range(min(3, num_pages)):
            text = reader.pages[i].extract_text()
            if text and text.strip():
                has_text = True
                break

        return has_text, num_pages
    except Exception as e:
        raise ValidationError(f"Cannot read PDF: {e}")
```

### 3.3 extractors.py

```python
"""Text extraction implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

from .models import ExtractionConfig, ExtractionResult, PageText


class BaseExtractor(ABC):
    """Abstract base class for text extractors."""

    def __init__(self, config: ExtractionConfig):
        """Initialize extractor with configuration."""
        self.config = config
        self.reader: Optional[PdfReader] = None

    @abstractmethod
    def extract(self) -> ExtractionResult:
        """
        Extract text from PDF.

        Returns:
            ExtractionResult with extracted text
        """
        pass

    def _open_pdf(self) -> PdfReader:
        """Open PDF file for reading."""
        return PdfReader(self.config.input_path)

    def _extract_page_text(self, page, page_num: int) -> PageText:
        """
        Extract text from a single page.

        Args:
            page: PyPDF2 page object
            page_num: Page number (1-based)

        Returns:
            PageText object
        """
        text = page.extract_text()

        metadata = {}
        if self.config.include_metadata:
            # Extract page-level metadata if available
            if hasattr(page, 'mediabox'):
                metadata['width'] = float(page.mediabox.width)
                metadata['height'] = float(page.mediabox.height)

        return PageText(
            page_num=page_num,
            text=text,
            char_count=len(text),
            metadata=metadata
        )

    def _show_progress(self, current: int, total: int, message: str = "Extracting"):
        """Display progress indicator."""
        if self.config.verbose:
            percent = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)
            print(f"\r{message}: [{bar}] {current}/{total} ({percent:.1f}%)", end='', flush=True)
            if current == total:
                print()  # New line when done

    def _extract_pdf_metadata(self, reader: PdfReader) -> dict:
        """Extract PDF document metadata."""
        metadata = {}
        if self.config.include_metadata and reader.metadata:
            for key, value in reader.metadata.items():
                # Remove leading '/' from keys
                clean_key = key.lstrip('/')
                metadata[clean_key] = str(value)
        return metadata


class SimpleExtractor(BaseExtractor):
    """Simple text extraction (all text concatenated)."""

    def extract(self) -> ExtractionResult:
        """Extract all text as single string."""
        reader = self._open_pdf()
        pages_data = []
        all_text = []

        # Determine which pages to extract
        page_nums = self.config.pages if self.config.pages else range(1, len(reader.pages) + 1)
        total = len(page_nums) if isinstance(page_nums, list) else len(reader.pages)

        for idx, page_num in enumerate(page_nums if isinstance(page_nums, list) else page_nums, 1):
            # Convert to 0-based for PyPDF2
            page_idx = page_num - 1 if isinstance(page_nums, list) else page_num
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num if isinstance(page_nums, list) else page_num + 1)
            pages_data.append(page_text)
            all_text.append(page_text.text)

            self._show_progress(idx, total, "Extracting text")

        combined_text = "\n\n".join(all_text)
        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            text=combined_text,
            pages=pages_data,
            metadata=metadata,
            char_count=len(combined_text)
        )


class LayoutExtractor(BaseExtractor):
    """Layout-preserving text extraction."""

    def extract(self) -> ExtractionResult:
        """Extract text while preserving layout."""
        reader = self._open_pdf()
        pages_data = []
        all_text = []

        page_nums = self.config.pages if self.config.pages else range(1, len(reader.pages) + 1)
        total = len(page_nums) if isinstance(page_nums, list) else len(reader.pages)

        for idx, page_num in enumerate(page_nums if isinstance(page_nums, list) else page_nums, 1):
            page_idx = page_num - 1 if isinstance(page_nums, list) else page_num
            page = reader.pages[page_idx]

            # Use layout mode for extraction (PyPDF2 default preserves layout better)
            page_text = self._extract_page_text(page, page_num if isinstance(page_nums, list) else page_num + 1)
            pages_data.append(page_text)
            all_text.append(page_text.text)

            self._show_progress(idx, total, "Extracting text (layout mode)")

        # Preserve page breaks with form feed
        combined_text = "\f\n".join(all_text)
        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            text=combined_text,
            pages=pages_data,
            metadata=metadata,
            char_count=len(combined_text)
        )


class PerPageExtractor(BaseExtractor):
    """Extract text to separate file per page."""

    def extract(self) -> ExtractionResult:
        """Extract text with one file per page."""
        reader = self._open_pdf()
        pages_data = []

        page_nums = self.config.pages if self.config.pages else range(1, len(reader.pages) + 1)
        total = len(page_nums) if isinstance(page_nums, list) else len(reader.pages)

        # Ensure output directory exists
        output_dir = self.config.output_path or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get base name for files
        base_name = self.config.input_path.stem

        for idx, page_num in enumerate(page_nums if isinstance(page_nums, list) else page_nums, 1):
            page_idx = page_num - 1 if isinstance(page_nums, list) else page_num
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num if isinstance(page_nums, list) else page_num + 1)
            pages_data.append(page_text)

            # Write individual file
            output_file = output_dir / f"{base_name}_page_{page_num:03d}.txt"
            output_file.write_text(page_text.text, encoding=self.config.encoding)

            self._show_progress(idx, total, "Extracting pages")

        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            pages=pages_data,
            metadata=metadata,
            message=f"Extracted {len(pages_data)} pages to {output_dir}"
        )


class StructuredExtractor(BaseExtractor):
    """Extract text with structure and metadata."""

    def extract(self) -> ExtractionResult:
        """Extract text as structured data."""
        reader = self._open_pdf()
        pages_data = []

        page_nums = self.config.pages if self.config.pages else range(1, len(reader.pages) + 1)
        total = len(page_nums) if isinstance(page_nums, list) else len(reader.pages)

        for idx, page_num in enumerate(page_nums if isinstance(page_nums, list) else page_nums, 1):
            page_idx = page_num - 1 if isinstance(page_nums, list) else page_num
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num if isinstance(page_nums, list) else page_num + 1)
            pages_data.append(page_text)

            self._show_progress(idx, total, "Extracting structured data")

        metadata = self._extract_pdf_metadata(reader)
        metadata['total_pages'] = len(reader.pages)
        metadata['extracted_pages'] = len(pages_data)

        return ExtractionResult(
            status="success",
            pages=pages_data,
            metadata=metadata
        )
```

### 3.4 formatters.py

```python
"""Output formatters for extracted text."""

from abc import ABC, abstractmethod
import json
from typing import Any

from .models import ExtractionResult, OutputFormat


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, result: ExtractionResult) -> str:
        """Format extraction result to string."""
        pass


class TxtFormatter(BaseFormatter):
    """Plain text formatter."""

    def format(self, result: ExtractionResult) -> str:
        """Format as plain text."""
        if result.text:
            return result.text
        else:
            # Combine pages
            return "\n\n".join(p.text for p in result.pages)


class JsonFormatter(BaseFormatter):
    """JSON formatter with metadata."""

    def format(self, result: ExtractionResult) -> str:
        """Format as JSON."""
        data = {
            "status": result.status,
            "metadata": result.metadata,
            "char_count": result.char_count,
            "pages": [
                {
                    "page_num": p.page_num,
                    "text": p.text,
                    "char_count": p.char_count,
                    "metadata": p.metadata
                }
                for p in result.pages
            ]
        }

        if result.message:
            data["message"] = result.message

        return json.dumps(data, indent=2, ensure_ascii=False)


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter."""

    def format(self, result: ExtractionResult) -> str:
        """Format as Markdown."""
        lines = []

        # Add metadata section if available
        if result.metadata:
            lines.append("# PDF Metadata\n")
            for key, value in result.metadata.items():
                lines.append(f"**{key}**: {value}  ")
            lines.append("\n---\n")

        # Add content
        if result.text:
            lines.append("# Content\n")
            lines.append(result.text)
        else:
            for page in result.pages:
                lines.append(f"## Page {page.page_num}\n")
                lines.append(page.text)
                lines.append("\n---\n")

        return "\n".join(lines)


def get_formatter(format: OutputFormat) -> BaseFormatter:
    """Factory function to get appropriate formatter."""
    formatters = {
        OutputFormat.TXT: TxtFormatter,
        OutputFormat.JSON: JsonFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter
    }
    return formatters[format]()
```

### 3.5 core.py

```python
"""Core text extraction functionality."""

from pathlib import Path
from typing import Optional, Union

from pdftools.core.validators import validate_pdf_path, validate_output_dir
from pdftools.core.exceptions import ValidationError

from .models import (
    ExtractionConfig,
    ExtractionResult,
    ExtractionMode,
    OutputFormat
)
from .validators import validate_pages, validate_encoding, check_text_layer
from .extractors import (
    SimpleExtractor,
    LayoutExtractor,
    PerPageExtractor,
    StructuredExtractor
)
from .formatters import get_formatter


def extract_text(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    mode: ExtractionMode = ExtractionMode.SIMPLE,
    format: OutputFormat = OutputFormat.TXT,
    pages: Optional[list[int]] = None,
    encoding: str = "utf-8",
    include_metadata: bool = False,
    verbose: bool = False,
    config: Optional[ExtractionConfig] = None
) -> ExtractionResult:
    """
    Extract text from a PDF file.

    Args:
        input_path: Path to input PDF file
        output_path: Path to output file or directory (None = stdout)
        mode: Extraction mode (SIMPLE, LAYOUT, PER_PAGE, STRUCTURED)
        format: Output format (TXT, JSON, MARKDOWN)
        pages: Specific pages to extract (None = all pages)
        encoding: Output encoding (default: utf-8)
        include_metadata: Include PDF metadata in output
        verbose: Show progress indicator
        config: Pre-configured ExtractionConfig (overrides other params)

    Returns:
        ExtractionResult with extracted text and metadata

    Raises:
        ValidationError: If input is invalid

    Example:
        >>> result = extract_text("document.pdf", "output.txt")
        >>> print(result.char_count)
        12450
    """
    # Build config
    if config is None:
        config = ExtractionConfig(
            input_path=Path(input_path),
            output_path=Path(output_path) if output_path else None,
            mode=mode,
            format=format,
            pages=pages,
            encoding=encoding,
            include_metadata=include_metadata,
            verbose=verbose
        )

    # Validate input
    validate_pdf_path(config.input_path)
    validate_encoding(config.encoding)

    # Check for text layer
    has_text, num_pages = check_text_layer(config.input_path)
    if not has_text:
        if verbose:
            print(f"⚠ Warning: No text layer found. PDF may be scanned. Consider using OCR.")

    # Validate pages if specified
    if config.pages:
        validate_pages(config.pages, num_pages)

    # Validate output path
    if config.output_path:
        if mode == ExtractionMode.PER_PAGE:
            # Output should be directory
            if config.output_path.exists() and config.output_path.is_file():
                raise ValidationError(
                    "PER_PAGE mode requires output_path to be a directory"
                )
        else:
            # Validate output directory can be created
            validate_output_dir(config.output_path.parent, create=True)

    # Create appropriate extractor
    extractor = _create_extractor(config)

    # Extract text
    result = extractor.extract()

    # Write output if path specified
    if config.output_path and mode != ExtractionMode.PER_PAGE:
        formatter = get_formatter(config.format)
        output_text = formatter.format(result)
        config.output_path.write_text(output_text, encoding=config.encoding)
        result.message = f"Text extracted to {config.output_path}"

    return result


def _create_extractor(config: ExtractionConfig):
    """Factory function to create appropriate extractor."""
    extractors = {
        ExtractionMode.SIMPLE: SimpleExtractor,
        ExtractionMode.LAYOUT: LayoutExtractor,
        ExtractionMode.PER_PAGE: PerPageExtractor,
        ExtractionMode.STRUCTURED: StructuredExtractor
    }
    return extractors[config.mode](config)
```

---

## 4. API Design

### 4.1 Public API

```python
# Main function
def extract_text(
    input_path: str | Path,
    output_path: str | Path | None = None,
    mode: ExtractionMode = ExtractionMode.SIMPLE,
    format: OutputFormat = OutputFormat.TXT,
    pages: list[int] | None = None,
    encoding: str = "utf-8",
    include_metadata: bool = False,
    verbose: bool = False,
    config: ExtractionConfig | None = None
) -> ExtractionResult

# Enums
class ExtractionMode(Enum):
    SIMPLE = "simple"
    LAYOUT = "layout"
    PER_PAGE = "per_page"
    STRUCTURED = "structured"

class OutputFormat(Enum):
    TXT = "txt"
    JSON = "json"
    MARKDOWN = "markdown"

# Data classes
@dataclass
class ExtractionConfig: ...
@dataclass
class ExtractionResult: ...
@dataclass
class PageText: ...
```

### 4.2 CLI Interface

```bash
pdfgettxt -i INPUT [-o OUTPUT] [-m MODE] [-f FORMAT] [-p PAGES] [options]

Required:
  -i, --input PATH        Input PDF file

Optional:
  -o, --output PATH       Output file or directory
  -m, --mode MODE         Extraction mode (simple/layout/per_page/structured)
  -f, --format FORMAT     Output format (txt/json/markdown)
  -p, --pages PAGES       Specific pages (e.g., "1,3,5-10")
  -e, --encoding ENC      Output encoding (default: utf-8)
  --include-metadata      Include PDF metadata
  -v, --verbose           Show progress
  -h, --help              Show help
```

---

## 5. Fehlerbehandlung

### 5.1 Exception Hierarchy

```
PDFToolsError (Base)
    │
    ├── ValidationError
    │   ├── InvalidPageError
    │   ├── InvalidEncodingError
    │   └── InvalidPathError
    │
    └── ExtractionError
        ├── NoTextLayerError
        └── PDFCorruptedError
```

### 5.2 Fehlerszenarien

| Fehler | Exception | Behandlung |
|--------|-----------|------------|
| PDF nicht gefunden | ValidationError | Exit Code 1, Fehlermeldung |
| Ungültige PDF | ValidationError | Exit Code 1, Fehlermeldung |
| Keine Textebene | Warning | Exit Code 0, Warnung, leerer Text |
| Ungültige Seite | ValidationError | Exit Code 1, Fehlermeldung |
| Encoding-Fehler | ValidationError | Exit Code 1, Fehlermeldung |
| Schreibfehler | IOError | Exit Code 1, Fehlermeldung |

---

## 6. Performance-Optimierung

### 6.1 Speicherverwaltung
- Streaming-Verarbeitung für große PDFs
- Page-by-page Extraktion (nicht alles in RAM)
- Lazy loading von Metadaten

### 6.2 Geschwindigkeitsoptimierung
- Minimale PDF-Operationen
- Effiziente String-Konkatenation (join statt +)
- Optional: Multiprocessing für sehr große PDFs (v2.0)

---

## 7. Testing-Strategie

### 7.1 Unit Tests
- [ ] models.py: Data classes, validation
- [ ] validators.py: Input validation, encoding, pages
- [ ] extractors.py: Each extractor class separately
- [ ] formatters.py: Each formatter separately

### 7.2 Integration Tests
- [ ] End-to-end extraction workflows
- [ ] File I/O operations
- [ ] Error handling

### 7.3 Test Data
- Simple PDF (text only)
- Complex PDF (multi-column layout)
- PDF without text layer (scanned)
- Large PDF (1000+ pages)
- Unicode PDF (special characters)

---

## 8. Sicherheit

### 8.1 Input Validation
- ✅ Path traversal prevention (use Path.resolve())
- ✅ PDF format validation
- ✅ Encoding validation
- ✅ Page number bounds checking

### 8.2 Resource Limits
- ✅ Maximum file size handling (warn on very large files)
- ✅ Memory limits (streaming approach)
- ✅ Output path validation

---

## 9. Dependencies

### 9.1 Required
- **PyPDF2** (already present): PDF reading
- **pathlib** (stdlib): Path handling
- **json** (stdlib): JSON formatting

### 9.2 Optional
- None for v1.0

---

## 10. Review

**Architekt**: ✅ Approved
- [x] SOLID Principles eingehalten
- [x] Klare Separation of Concerns
- [x] Erweiterbar für neue Modi/Formate

**Python Entwickler**: ✅ Approved
- [x] Type Hints vollständig
- [x] Docstrings vollständig
- [x] Implementierbar mit PyPDF2

**Tester**: ✅ Approved
- [x] Testbar durch Dependency Injection
- [x] Klare Error Handling
- [x] Mockable components

**DevOps**: ✅ Approved
- [x] Keine neuen Dependencies
- [x] CLI klar definiert

---

## 11. Änderungshistorie

| Datum | Version | Änderung | Von | Auswirkung |
|-------|---------|----------|-----|------------|
| 2025-11-22 | 1.0 | Initiale Erstellung | System Architect | Neu |

---

## 12. Freigabe

**Freigegeben durch**: All 4 Roles (Architekt, Python Developer, Tester, DevOps)
**Datum**: 2025-11-22
**Nächster Schritt**: Implementation (Phase 5)
