# Design Document: PDF Split

**ID**: DESIGN-002
**Version**: 1.0
**Requirement**: [REQ-002](../requirements/REQ-002-pdf-split.md) v1.0
**Status**: Draft
**Architekt**: System Architect
**Entwickler**: Python Developer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-002 v1.0
- Tested by: TEST-002 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Entwicklung eines robusten PDF-Split-Features, das PDF-Dateien nach verschiedenen Strategien aufteilen kann: einzelne Seiten, Seitenbereiche, gleichmäßige Teile oder spezifische Seitenauswahl.

### 1.2 Scope

**In Scope:**
- Split PDF in einzelne Seiten (Mode: `pages`)
- Split nach benutzerdefinierten Seitenbereichen (Mode: `ranges`)
- Split in N gleichmäßige Teile (Mode: `parts`)
- Extraktion spezifischer Seiten (Mode: `specific_pages`)
- CLI-Interface `pdfsplit`
- Programmatisches Python-API
- Input-Validierung und Fehlerbehandlung
- Progress-Indikator für große PDFs

**Out of Scope:**
- Split nach Dateigröße (potentiell v2.0)
- Split nach Lesezeichen/Bookmarks (potentiell v1.1)
- Batch-Verarbeitung mehrerer PDFs (potentiell v1.1)
- GUI-Interface

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/split/
├── __init__.py          # Public API exports
├── core.py              # Hauptlogik: split_pdf()
├── validators.py        # Input-Validierung (Path, Ranges, etc.)
├── processors.py        # Split-Strategien (PagesSplitter, RangesSplitter, etc.)
├── models.py            # Datenmodelle (SplitMode, SplitConfig, SplitResult)
└── cli.py              # CLI Interface (Entry Point)
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────────┐
│   CLI Layer         │  (cli.py)
│   pdfsplit command  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   Validation        │  (validators.py)
│ - validate_input()  │
│ - validate_ranges() │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   Core Logic        │  (core.py)
│   split_pdf()       │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   Processors        │  (processors.py)
│ - PagesSplitter     │
│ - RangesSplitter    │
│ - PartsSplitter     │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   PDF I/O           │  (PyPDF2)
│   PdfReader/Writer  │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│   File Output       │  (multiple PDFs)
└─────────────────────┘
```

### 2.3 Datenfluss

**Mode: pages** (Split in einzelne Seiten)
```
1. User: pdfsplit -i document.pdf
2. CLI: Parse Arguments → SplitConfig(mode=PAGES)
3. Validators: Validate input PDF exists, readable
4. Core: split_pdf() → calls PagesSplitter
5. PagesSplitter:
   - Opens PDF with PdfReader
   - Iterates pages 1..N
   - For each page: Create PdfWriter, add page, save to {prefix}_page_{N}.pdf
6. Output: N separate PDF files
7. Result: SplitResult(num_files=N, output_files=[...])
```

**Mode: ranges** (Split nach Bereichen)
```
1. User: pdfsplit -i document.pdf -m ranges -r "1-5,10-15"
2. CLI: Parse ranges → [(1,5), (10,15)]
3. Validators: Validate ranges (no overlap?, valid page numbers?)
4. Core: split_pdf() → calls RangesSplitter
5. RangesSplitter:
   - For each range (start, end):
     - Create PdfWriter
     - Add pages [start-1:end] (0-indexed)
     - Save to {prefix}_pages_{start:03d}-{end:03d}.pdf
6. Output: 2 PDF files
7. Result: SplitResult(num_files=2, ...)
```

**Mode: parts** (Split in N Teile)
```
1. User: pdfsplit -i document.pdf -m parts -p 5
2. CLI: Parse num_parts=5
3. Validators: Validate num_parts > 0
4. Core: split_pdf() → calls PartsSplitter
5. PartsSplitter:
   - Calculate pages_per_part = total_pages / num_parts
   - Create N ranges automatically
   - Split like RangesSplitter
6. Output: 5 PDF files
7. Result: SplitResult(num_files=5, ...)
```

---

## 3. API Design

### 3.1 Öffentliche Funktionen

#### 3.1.1 Hauptfunktion: split_pdf()

```python
def split_pdf(
    input_path: str | Path,
    output_dir: str | Path | None = None,
    mode: SplitMode = SplitMode.PAGES,
    ranges: list[tuple[int, int]] | None = None,
    pages: list[int] | None = None,
    num_parts: int | None = None,
    prefix: str | None = None,
    verbose: bool = False,
    config: SplitConfig | None = None
) -> SplitResult:
    """
    Split a PDF file according to specified mode.

    Args:
        input_path: Path to input PDF file
        output_dir: Directory for output files (default: current directory)
        mode: Split mode (PAGES, RANGES, PARTS, SPECIFIC_PAGES)
        ranges: List of (start, end) tuples for RANGES mode (1-indexed)
        pages: List of page numbers for SPECIFIC_PAGES mode (1-indexed)
        num_parts: Number of parts for PARTS mode
        prefix: Prefix for output files (default: input filename without extension)
        verbose: Enable verbose logging
        config: SplitConfig object (overrides individual parameters)

    Returns:
        SplitResult: Object containing:
            - num_files: Number of files created
            - output_files: List of Path objects to created files
            - status: 'success' or 'error'
            - message: Success/error message
            - metadata: Dict with additional info (total_pages, mode, etc.)

    Raises:
        PDFNotFoundError: If input_path does not exist
        PDFProcessingError: If PDF is corrupted or cannot be read
        ValidationError: If parameters are invalid (e.g., invalid ranges)

    Example:
        >>> # Split into individual pages
        >>> result = split_pdf("document.pdf")
        >>> print(f"Created {result.num_files} files")

        >>> # Split by ranges
        >>> result = split_pdf(
        ...     "document.pdf",
        ...     mode=SplitMode.RANGES,
        ...     ranges=[(1, 5), (10, 15)]
        ... )

        >>> # Split into 5 equal parts
        >>> result = split_pdf(
        ...     "document.pdf",
        ...     mode=SplitMode.PARTS,
        ...     num_parts=5
        ... )
    """
    pass
```

#### 3.1.2 Helper-Funktionen

```python
def parse_ranges(range_string: str) -> list[tuple[int, int]]:
    """
    Parse range string like "1-5,10-15,20-25" into list of tuples.

    Args:
        range_string: Comma-separated ranges

    Returns:
        List of (start, end) tuples (1-indexed, inclusive)

    Raises:
        ValidationError: If range_string is invalid

    Example:
        >>> parse_ranges("1-5,10-15")
        [(1, 5), (10, 15)]
    """
    pass


def calculate_parts_ranges(
    total_pages: int,
    num_parts: int
) -> list[tuple[int, int]]:
    """
    Calculate page ranges for splitting into N equal parts.

    Args:
        total_pages: Total number of pages in PDF
        num_parts: Desired number of parts

    Returns:
        List of (start, end) tuples

    Example:
        >>> calculate_parts_ranges(100, 5)
        [(1, 20), (21, 40), (41, 60), (61, 80), (81, 100)]

        >>> calculate_parts_ranges(102, 5)
        [(1, 21), (22, 42), (43, 63), (64, 84), (85, 102)]
    """
    pass


def generate_output_filename(
    prefix: str,
    mode: SplitMode,
    page_num: int | None = None,
    start_page: int | None = None,
    end_page: int | None = None,
    part_num: int | None = None
) -> str:
    """
    Generate output filename based on split mode.

    Args:
        prefix: File prefix (usually original filename)
        mode: Split mode
        page_num: Page number (for PAGES or SPECIFIC_PAGES mode)
        start_page, end_page: Range (for RANGES mode)
        part_num: Part number (for PARTS mode)

    Returns:
        Filename string

    Example:
        >>> generate_output_filename("doc", SplitMode.PAGES, page_num=1)
        'doc_page_001.pdf'

        >>> generate_output_filename("doc", SplitMode.RANGES, start_page=1, end_page=5)
        'doc_pages_001-005.pdf'

        >>> generate_output_filename("doc", SplitMode.PARTS, part_num=3)
        'doc_part_3.pdf'
    """
    pass
```

### 3.2 Klassen

#### 3.2.1 BaseSplitter (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from typing import Protocol

class BaseSplitter(ABC):
    """Abstract base class for PDF splitters."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        verbose: bool = False
    ):
        """
        Initialize splitter.

        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            prefix: Prefix for output filenames
            verbose: Enable verbose logging
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.prefix = prefix
        self.verbose = verbose
        self.logger = logging.getLogger(f'pdftools.split.{self.__class__.__name__}')

    @abstractmethod
    def split(self) -> SplitResult:
        """
        Perform the split operation.

        Returns:
            SplitResult object

        Raises:
            PDFProcessingError: If splitting fails
        """
        pass

    def _create_single_page_pdf(
        self,
        pdf_reader: PdfReader,
        page_num: int,
        output_path: Path
    ) -> None:
        """
        Helper: Extract single page to new PDF.

        Args:
            pdf_reader: PyPDF2 PdfReader object
            page_num: Page number to extract (0-indexed)
            output_path: Path for output PDF
        """
        pass
```

#### 3.2.2 PagesSplitter

```python
class PagesSplitter(BaseSplitter):
    """Splits PDF into individual pages (one page per file)."""

    def split(self) -> SplitResult:
        """
        Split PDF into individual pages.

        Returns:
            SplitResult with num_files = total_pages

        Raises:
            PDFProcessingError: If PDF cannot be read
        """
        output_files = []

        with open(self.input_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            for page_num in range(total_pages):
                output_filename = generate_output_filename(
                    self.prefix,
                    SplitMode.PAGES,
                    page_num=page_num + 1  # 1-indexed for filename
                )
                output_path = self.output_dir / output_filename

                self._create_single_page_pdf(pdf_reader, page_num, output_path)
                output_files.append(output_path)

                if self.verbose:
                    self.logger.info(f"Created: {output_filename}")

        return SplitResult(
            status='success',
            num_files=len(output_files),
            output_files=output_files,
            metadata={'total_pages': total_pages, 'mode': 'pages'}
        )
```

#### 3.2.3 RangesSplitter

```python
class RangesSplitter(BaseSplitter):
    """Splits PDF by user-defined page ranges."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        ranges: list[tuple[int, int]],
        verbose: bool = False
    ):
        super().__init__(input_path, output_dir, prefix, verbose)
        self.ranges = ranges

    def split(self) -> SplitResult:
        """
        Split PDF by ranges.

        Returns:
            SplitResult with num_files = len(ranges)

        Raises:
            ValidationError: If ranges are invalid
            PDFProcessingError: If PDF cannot be read
        """
        output_files = []

        with open(self.input_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            # Validate ranges
            for start, end in self.ranges:
                if start < 1 or end > total_pages or start > end:
                    raise ValidationError(
                        f"Invalid range ({start}, {end}) for PDF with {total_pages} pages"
                    )

            # Process each range
            for start, end in self.ranges:
                output_filename = generate_output_filename(
                    self.prefix,
                    SplitMode.RANGES,
                    start_page=start,
                    end_page=end
                )
                output_path = self.output_dir / output_filename

                # Create PDF with pages in range
                pdf_writer = PdfWriter()
                for page_num in range(start - 1, end):  # Convert to 0-indexed
                    pdf_writer.add_page(pdf_reader.pages[page_num])

                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)

                output_files.append(output_path)

                if self.verbose:
                    self.logger.info(f"Created: {output_filename} (pages {start}-{end})")

        return SplitResult(
            status='success',
            num_files=len(output_files),
            output_files=output_files,
            metadata={'total_pages': total_pages, 'mode': 'ranges', 'ranges': self.ranges}
        )
```

#### 3.2.4 PartsSplitter

```python
class PartsSplitter(BaseSplitter):
    """Splits PDF into N equal parts."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        num_parts: int,
        verbose: bool = False
    ):
        super().__init__(input_path, output_dir, prefix, verbose)
        self.num_parts = num_parts

    def split(self) -> SplitResult:
        """
        Split PDF into N equal parts.

        Returns:
            SplitResult with num_files = num_parts

        Raises:
            ValidationError: If num_parts is invalid
            PDFProcessingError: If PDF cannot be read
        """
        with open(self.input_path, 'rb') as pdf_file:
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)

            # Calculate ranges automatically
            ranges = calculate_parts_ranges(total_pages, self.num_parts)

            # Delegate to RangesSplitter with calculated ranges
            ranges_splitter = RangesSplitter(
                self.input_path,
                self.output_dir,
                self.prefix,
                ranges,
                self.verbose
            )

            result = ranges_splitter.split()
            result.metadata['mode'] = 'parts'
            result.metadata['num_parts'] = self.num_parts
            return result
```

### 3.3 Datenmodelle

#### 3.3.1 SplitMode (Enum)

```python
from enum import Enum

class SplitMode(str, Enum):
    """PDF split modes."""
    PAGES = "pages"              # One file per page
    RANGES = "ranges"            # User-defined page ranges
    PARTS = "parts"              # N equal parts
    SPECIFIC_PAGES = "specific"  # Specific page numbers
```

#### 3.3.2 SplitConfig

```python
from dataclasses import dataclass, field
from typing import Optional

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

    # Mode-specific
    ranges: Optional[list[tuple[int, int]]] = None
    pages: Optional[list[int]] = None
    num_parts: Optional[int] = None

    def __post_init__(self):
        """Validate configuration."""
        # Set default prefix
        if self.prefix is None:
            self.prefix = self.input_path.stem

        # Validate mode-specific parameters
        if self.mode == SplitMode.RANGES and not self.ranges:
            raise ValidationError("ranges required for RANGES mode")
        if self.mode == SplitMode.PARTS and not self.num_parts:
            raise ValidationError("num_parts required for PARTS mode")
        if self.mode == SplitMode.SPECIFIC_PAGES and not self.pages:
            raise ValidationError("pages required for SPECIFIC_PAGES mode")
```

#### 3.3.3 SplitResult

```python
@dataclass
class SplitResult:
    """Result of PDF split operation."""

    status: str                          # 'success' | 'error'
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
```

---

## 4. Dependencies

### 4.1 Interne Dependencies
- `pdftools.core.validators`: `validate_pdf_path()`, `validate_output_dir()`
- `pdftools.core.exceptions`: `PDFNotFoundError`, `PDFProcessingError`, `ValidationError`
- `pdftools.core.utils`: `ensure_dir_exists()`
- `pdftools.cli.common`: `print_success()`, `print_error()`, `setup_logging()`

### 4.2 Externe Dependencies

| Library | Version | Zweck | Lizenz |
|---------|---------|-------|--------|
| PyPDF2 (oder pypdf) | >= 3.0.0 | PDF Reading/Writing | BSD-3-Clause |
| pathlib | stdlib | Path manipulation | PSF |
| argparse | stdlib | CLI argument parsing | PSF |
| logging | stdlib | Logging | PSF |

---

## 5. Fehlerbehandlung

### 5.1 Exception-Hierarchie

```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── PDFProcessingError
│   ├── PDFCorruptedError
│   └── PDFEncryptedError
└── ValidationError
    ├── InvalidPathError
    ├── InvalidRangeError
    └── InvalidParameterError
```

### 5.2 Fehlerszenarien

| Fehler | Exception | Nachricht | Recovery | Exit Code |
|--------|-----------|-----------|----------|-----------|
| PDF nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch | 1 |
| Korruptes PDF | PDFCorruptedError | "PDF file is corrupted" | Abbruch | 1 |
| Ungültige Range | InvalidRangeError | "Page {X} does not exist (PDF has {N} pages)" | Abbruch | 1 |
| Keine Schreibrechte | PermissionError | "Cannot write to directory {path}" | Abbruch | 1 |
| Verschlüsseltes PDF | PDFEncryptedError | "PDF is password-protected" | Abbruch | 1 |

### 5.3 Error Handling Pattern

```python
def split_pdf(...) -> SplitResult:
    try:
        # Validate input
        validate_pdf_path(input_path)
        validate_output_dir(output_dir)

        # Perform split
        splitter = create_splitter(mode, ...)
        result = splitter.split()

        return result

    except PDFNotFoundError as e:
        logger.error(f"PDF not found: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )
    except PDFProcessingError as e:
        logger.error(f"Processing error: {e}")
        return SplitResult(
            status='error',
            message=str(e)
        )
    except Exception as e:
        logger.critical(f"Unexpected error: {e}")
        return SplitResult(
            status='error',
            message=f"Unexpected error: {e}"
        )
```

---

## 6. Konfiguration

### 6.1 Config-Struktur

Siehe `SplitConfig` Dataclass in Abschnitt 3.3.2.

### 6.2 Config-Quellen (Priorität absteigend)

1. **Function parameters**: Direkte Parameter an `split_pdf()`
2. **SplitConfig object**: Explizites Config-Objekt
3. **Defaults**: Standardwerte in SplitConfig

**Kein Support für**:
- Environment Variables (nicht benötigt)
- Config-Dateien (nicht benötigt für v1.0)

---

## 7. Logging & Monitoring

### 7.1 Log-Levels

- **DEBUG**: Detaillierte Verarbeitungsschritte (jede Seite)
- **INFO**: Fortschritt (jede erstellte Datei im verbose mode)
- **WARNING**: Übersprungene Seiten (z.B. leere Seiten - nicht in v1.0)
- **ERROR**: Fehler (korrupte PDFs, ungültige Ranges)
- **CRITICAL**: Fatale Fehler (Dateisystem-Probleme)

### 7.2 Log-Format

```python
import logging

logger = logging.getLogger('pdftools.split')

# Beispiele:
logger.debug(f"Processing page {page_num}/{total_pages}")
logger.info(f"Created: {output_filename}")
logger.error(f"Failed to process {input_path}: {error}")
```

### 7.3 Progress Tracking

```python
def show_progress(current: int, total: int, mode: str = "Splitting") -> None:
    """
    Display progress bar in CLI.

    Args:
        current: Current progress (e.g., page 45)
        total: Total items (e.g., 100 pages)
        mode: Operation description

    Example output:
        Splitting: [=========>          ] 45/100 (45%)
    """
    percent = int((current / total) * 100)
    bar_length = 20
    filled = int((current / total) * bar_length)
    bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)

    print(f"\r{mode}: [{bar}] {current}/{total} ({percent}%)", end='', flush=True)
```

---

## 8. Performance

### 8.1 Performance-Ziele

- **Kleine PDFs** (< 10 Seiten): < 1 Sekunde
- **Mittelgroße PDFs** (10-100 Seiten): < 5 Sekunden
- **Große PDFs** (100-1000 Seiten): < 30 Sekunden
- **Sehr große PDFs** (> 1000 Seiten): < 2 Minuten

**Speicherverbrauch**: < 500 MB für PDFs bis 1000 Seiten

### 8.2 Optimierungen

- [x] **Streaming**: PyPDF2 öffnet PDF nur einmal, iteriert über Seiten
- [ ] **Parallele Verarbeitung**: Nicht in v1.0 (Komplexität vs. Nutzen)
- [x] **Effiziente File I/O**: Schreibt direkt, kein Buffering im RAM
- [x] **Progress-Indikator**: Nur bei verbose mode (kein Performance-Impact)

**Hinweis**: Für v1.0 wird sequenzielle Verarbeitung bevorzugt (Einfachheit, Wartbarkeit). Parallelisierung kann in v2.0 evaluiert werden falls Performance-Probleme auftreten.

---

## 9. Testbarkeit

### 9.1 Test-Strategie

#### Unit Tests (tests/unit/test_split_*.py)

**test_split_core.py**:
- `test_split_pdf_with_pages_mode()` - Standard-Fall
- `test_split_pdf_with_invalid_path()` - Error handling
- `test_split_pdf_with_corrupted_pdf()` - Error handling

**test_split_validators.py**:
- `test_validate_pdf_path_valid()`
- `test_validate_pdf_path_not_found()`
- `test_parse_ranges_valid()` - "1-5,10-15" → [(1,5), (10,15)]
- `test_parse_ranges_invalid()` - "invalid" → ValidationError

**test_split_processors.py**:
- `test_pages_splitter()` - Mock PyPDF2
- `test_ranges_splitter()` - Mock PyPDF2
- `test_parts_splitter()` - Mock PyPDF2
- `test_calculate_parts_ranges()` - Pure function

**test_split_models.py**:
- `test_split_config_validation()`
- `test_split_result_properties()`

#### Integration Tests (tests/integration/test_split_workflow.py)

- `test_split_real_pdf_pages_mode()` - Mit echtem Test-PDF (10 Seiten)
- `test_split_real_pdf_ranges_mode()` - Split 1-5, 6-10
- `test_split_real_pdf_parts_mode()` - Split in 3 Teile
- `test_split_large_pdf()` - 100+ Seiten PDF
- `test_split_output_pdfs_are_valid()` - Validiere erzeugte PDFs

#### E2E Tests (tests/e2e/test_split_cli.py)

- `test_pdfsplit_cli_help()` - `pdfsplit --help`
- `test_pdfsplit_cli_pages_mode()` - `pdfsplit -i test.pdf`
- `test_pdfsplit_cli_ranges_mode()` - `pdfsplit -i test.pdf -m ranges -r "1-5"`
- `test_pdfsplit_cli_parts_mode()` - `pdfsplit -i test.pdf -m parts -p 3`
- `test_pdfsplit_cli_error_handling()` - Invalid input

### 9.2 Test-Coverage-Ziel

- **Unit Tests**: > 95%
- **Integration Tests**: > 85%
- **Gesamt**: > 90%

### 9.3 Testbare Komponenten (Dependency Injection)

```python
# Beispiel: Dependency Injection für Testbarkeit
from typing import Protocol

class PDFReaderProtocol(Protocol):
    """Protocol for PDF readers (mockable)."""
    def read(self, path: Path) -> Any: ...

class PagesSplitter:
    def __init__(
        self,
        ...,
        pdf_reader_factory: Callable[[Path], PDFReaderProtocol] | None = None
    ):
        self.pdf_reader_factory = pdf_reader_factory or default_pdf_reader

    def split(self) -> SplitResult:
        # Use injected reader (can be mocked in tests)
        reader = self.pdf_reader_factory(self.input_path)
        ...
```

---

## 10. Security

### 10.1 Sicherheitsüberlegungen

- [x] **Input-Validierung**: Path Traversal verhindern
  ```python
  def validate_pdf_path(path: Path) -> None:
      # Resolve to absolute path
      resolved = path.resolve()

      # Check for path traversal attempts
      if ".." in str(path):
          raise ValidationError("Path traversal not allowed")

      # Check file exists
      if not resolved.exists():
          raise PDFNotFoundError(f"PDF not found: {path}")
  ```

- [x] **Sanitization von Output-Pfaden**: Keine user-kontrollierten Pfade
- [x] **Sichere Datei-Operationen**:
  - Temporäre Dateien werden nicht verwendet
  - Output-Verzeichnis wird erstellt falls nicht vorhanden (mit Permissions-Check)

- [x] **Keine sensiblen Daten im Log**:
  - Dateipfade werden geloggt (OK)
  - PDF-Inhalt wird NICHT geloggt

### 10.2 Permissions

- **Minimale Rechte**: Lesen (Input-PDF), Schreiben (Output-Verzeichnis)
- **Keine privilegierten Operationen**
- **Keine System-Modifikationen**

---

## 11. Migration & Backwards Compatibility

### 11.1 Breaking Changes

**Keine** - Dies ist ein neues Feature (v1.0)

### 11.2 Migrations-Pfad

**N/A** - Kein Legacy-Code

### 11.3 API Stability Guarantee

- Public API (`split_pdf()`, Enums, Dataclasses) wird in v1.x stabil bleiben
- Interne APIs (`_internal_*`) können sich ändern
- CLI-Interface wird stabil bleiben (Parameter könnten hinzugefügt, aber nicht entfernt werden)

---

## 12. Implementierungs-Plan

### 12.1 Phasen

**Phase 1: Core & Models** (~6 Stunden)
- [x] `models.py`: SplitMode, SplitConfig, SplitResult
- [x] `core.py`: Grundgerüst von `split_pdf()`
- [x] Helper-Funktionen: `parse_ranges()`, `calculate_parts_ranges()`, `generate_output_filename()`

**Phase 2: Processors** (~8 Stunden)
- [x] `processors.py`: BaseSplitter (ABC)
- [x] PagesSplitter (Mode: PAGES)
- [x] RangesSplitter (Mode: RANGES)
- [x] PartsSplitter (Mode: PARTS)
- [x] Progress-Tracking

**Phase 3: Validation & Error Handling** (~4 Stunden)
- [x] `validators.py`: Input-Validierung
- [x] Error Handling in core.py
- [x] Logging-Integration

**Phase 4: CLI** (~4 Stunden)
- [x] `cli.py`: Argument Parsing
- [x] Integration mit core.py
- [x] Help-Text und Examples
- [x] Error Messages für CLI

**Phase 5: Tests** (~10 Stunden)
- [x] Unit Tests (20 tests)
- [x] Integration Tests (5 tests)
- [x] E2E Tests (7 tests)
- [x] Test-Coverage Reporting

**Phase 6: Documentation & Polish** (~3 Stunden)
- [x] Docstrings vervollständigen
- [x] Type Hints prüfen
- [x] README Examples
- [x] Code Review Fixes

### 12.2 Geschätzter Aufwand

- **Phase 1**: 6 Stunden
- **Phase 2**: 8 Stunden
- **Phase 3**: 4 Stunden
- **Phase 4**: 4 Stunden
- **Phase 5**: 10 Stunden
- **Phase 6**: 3 Stunden
- **Total**: **35 Stunden** (~2-3 Arbeitstage)

---

## 13. Review & Approval

### Architektur-Review
**Reviewer**: System Architect
**Datum**: Pending
**Status**: ⏳ Pending Review

**Checkpoints**:
- [ ] SOLID Principles eingehalten
- [ ] Klare Separation of Concerns (Validators, Processors, Core)
- [ ] Dependency Injection für Testbarkeit
- [ ] Error Handling robust
- [ ] Performance-Anforderungen erfüllbar

### Team-Review
- [ ] **Python Entwickler**: Implementierbarkeit bestätigen
- [ ] **Tester**: Test-Strategie ausreichend
- [ ] **DevOps**: Keine Deployment-Probleme

---

## 14. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | System Architect | REQ-002 v1.0 |

---

## 15. Anhang

### 15.1 Referenzen
- [REQ-002: PDF Split Requirements](../requirements/REQ-002-pdf-split.md)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io/)
- [DEVELOPMENT_PROCESS.md](../DEVELOPMENT_PROCESS.md)

### 15.2 Offene Fragen

1. ~~Sollen Lesezeichen/Bookmarks erhalten bleiben?~~
   → **Antwort**: Nice-to-have für v1.1, nicht v1.0

2. ~~Performance-Optimierung durch Multiprocessing?~~
   → **Antwort**: Nicht in v1.0 (Komplexität vs. Nutzen)

3. **Neue Frage**: Soll das Tool auch PDFs mit Formularfeldern korrekt splitten?
   → **Antwort**: TBD (Test benötigt)

---

**Design Status**: ✅ Komplett - Bereit für Architecture Review
