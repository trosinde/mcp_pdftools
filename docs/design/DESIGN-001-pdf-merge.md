# Design Document: PDF Merge

**ID**: DESIGN-001
**Version**: 1.0
**Requirement**: [REQ-001](../requirements/REQ-001-pdf-merge.md) v1.0
**Status**: Approved
**Architekt**: Architecture Team
**Entwickler**: Python Development Team
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-001 v1.0
- Tested by: TEST-001 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Implementierung eines robusten, testbaren PDF-Merge-Moduls, das mehrere PDF-Dateien zu einem Dokument zusammenführt unter Berücksichtigung von Performance, Testbarkeit und Best Practices.

### 1.2 Scope
**In Scope:**
- Merge von 2-100 PDF-Dateien
- Lesezeichen-Erhaltung (optional, konfigurierbar)
- CLI und programmatisches Interface
- Vollständige Fehlerbehandlung
- Performance-Optimierung für große Dateien

**Out of Scope:**
- PDF-Bearbeitung (Rotation, Cropping, etc.)
- Formular-Zusammenführung
- Digitale Signaturen

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/merge/
├── __init__.py              # Public API exports
├── core.py                  # Hauptlogik, Orchestrierung
├── validators.py            # Input-Validierung
├── processors.py            # PDF-Merge-Logik
├── models.py                # Datenmodelle (Result, Config)
├── cli.py                   # CLI Interface
└── README.md                # Modul-Dokumentation
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────┐
│   CLI Layer     │  (cli.py)
│  pdftools-merge │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │  (validators.py)
│  - validate_    │
│    input_files  │
│  - validate_    │
│    output_path  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Core Logic     │  (core.py)
│  - merge_pdfs() │
│  - orchestrate  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Processors     │  (processors.py)
│  - PDFMerger    │
│  - PDF          │
│    ReaderAdapter│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   File Output   │
│  - Write merged │
│    PDF          │
└─────────────────┘
```

### 2.3 Datenfluss
1. **CLI**: Benutzer ruft `pdftools-merge` auf
2. **Validation**: Input-Dateien und Output-Pfad werden validiert
3. **Core**: `merge_pdfs()` orchestriert den Merge-Prozess
4. **Processor**: `PDFMerger` führt PDFs zusammen
5. **Output**: Merged PDF wird gespeichert
6. **Result**: Erfolgsmeldung oder Fehler wird zurückgegeben

---

## 3. API Design

### 3.1 Öffentliche Funktionen

#### 3.1.1 Hauptfunktion
```python
from pathlib import Path
from typing import List, Optional
from .models import MergeResult, MergeConfig

def merge_pdfs(
    files: List[Path],
    output_path: Optional[Path] = None,
    config: Optional[MergeConfig] = None
) -> MergeResult:
    """
    Merge multiple PDF files into a single document.

    Args:
        files: List of PDF file paths to merge (minimum 2)
        output_path: Output path for merged PDF.
                    If None, creates 'merged.pdf' in directory of first file.
        config: Optional configuration (bookmarks, progress callback, etc.)

    Returns:
        MergeResult: Object containing status, output path, and metadata

    Raises:
        PDFNotFoundError: If any input file doesn't exist
        InvalidParameterError: If less than 2 files provided
        PDFProcessingError: If merge fails

    Example:
        >>> result = merge_pdfs(
        ...     files=[Path("f1.pdf"), Path("f2.pdf")],
        ...     output_path=Path("merged.pdf")
        ... )
        >>> print(result.status)
        'success'
    """
    pass
```

### 3.2 Klassen

#### 3.2.1 PDFMerger (Processor)
```python
from typing import Protocol, List
from PyPDF2 import PdfReader, PdfWriter

class PDFReaderInterface(Protocol):
    """Interface for PDF readers (enables mocking)"""
    def read(self, path: Path) -> PdfReader:
        ...

class PDFMerger:
    """Handles the actual PDF merging logic"""

    def __init__(self, reader: Optional[PDFReaderInterface] = None):
        """
        Initialize merger with optional PDF reader.

        Args:
            reader: PDF reader implementation (for DI/testing)
        """
        self.reader = reader or DefaultPDFReader()
        self.writer = PdfWriter()

    def add_pdf(self, path: Path, keep_bookmarks: bool = True) -> None:
        """
        Add a PDF file to the merge queue.

        Args:
            path: Path to PDF file
            keep_bookmarks: Whether to preserve bookmarks
        """
        pdf_reader = self.reader.read(path)

        for page in pdf_reader.pages:
            self.writer.add_page(page)

        if keep_bookmarks and pdf_reader.outline:
            self._add_bookmarks(pdf_reader.outline)

    def write(self, output_path: Path) -> None:
        """
        Write merged PDF to file.

        Args:
            output_path: Destination path
        """
        with open(output_path, 'wb') as output_file:
            self.writer.write(output_file)

    def _add_bookmarks(self, outline) -> None:
        """Add bookmarks from source PDF (internal)"""
        # Implementation details
        pass
```

### 3.3 Datenmodelle

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, Dict, Any

@dataclass
class MergeConfig:
    """Configuration for PDF merge operation"""
    keep_bookmarks: bool = True
    add_toc: bool = False
    skip_on_error: bool = False
    progress_callback: Optional[Callable[[int, int], None]] = None
    verbose: bool = False

@dataclass
class MergeResult:
    """Result of PDF merge operation"""
    status: str  # 'success' | 'error' | 'partial'
    output_path: Optional[Path] = None
    message: str = ""
    pages_merged: int = 0
    files_processed: int = 0
    skipped_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return self.status == 'success'
```

---

## 4. Dependencies

### 4.1 Interne Dependencies
- `pdftools.core.validators`: `validate_pdf_path`, `validate_output_path`
- `pdftools.core.exceptions`: Exception-Hierarchie
- `pdftools.core.utils`: `normalize_path`, `generate_output_path`

### 4.2 Externe Dependencies
| Library | Version | Zweck | Lizenz |
|---------|---------|-------|--------|
| PyPDF2 | >= 3.0.0 | PDF Manipulation | BSD-3-Clause |

---

## 5. Fehlerbehandlung

### 5.1 Exception-Hierarchie
```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── PDFProcessingError
│   ├── PDFCorruptedError
│   └── PDFMergeError (new)
└── ValidationError
    ├── InvalidPathError
    └── InvalidParameterError
```

### 5.2 Fehlerszenarien
| Fehler | Exception | Nachricht | Recovery |
|--------|-----------|-----------|----------|
| Datei nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch oder Skip (config) |
| Korruptes PDF | PDFCorruptedError | "PDF file is corrupted: {path}" | Abbruch oder Skip |
| < 2 Dateien | InvalidParameterError | "At least 2 PDF files required" | Abbruch |
| Output nicht schreibbar | InsufficientPermissionsError | "Cannot write to: {path}" | Abbruch |
| Merge fehlgeschlagen | PDFMergeError | "Failed to merge PDFs: {reason}" | Abbruch |

---

## 6. Konfiguration

### 6.1 Config-Struktur
```python
@dataclass
class MergeConfig:
    keep_bookmarks: bool = True
    add_toc: bool = False
    skip_on_error: bool = False
    progress_callback: Optional[Callable] = None
    verbose: bool = False
```

### 6.2 Config-Quellen (Priorität absteigend)
1. Function parameters (highest)
2. Environment variables (`PDFTOOLS_MERGE_*`)
3. Defaults

### 6.3 Environment Variables
- `PDFTOOLS_MERGE_DEFAULT_OUTPUT`: Default output directory
- `PDFTOOLS_MERGE_KEEP_BOOKMARKS`: "true" | "false"

---

## 7. Logging & Monitoring

### 7.1 Log-Levels
- **DEBUG**: "Adding page {n} from {file}"
- **INFO**: "Processing {file} ({size} MB)"
- **WARNING**: "Skipping corrupted file: {file}"
- **ERROR**: "Failed to merge {file}: {error}"

### 7.2 Log-Format
```python
import logging

logger = logging.getLogger('pdftools.merge')

logger.info(f"Merging {len(files)} PDF files")
logger.debug(f"Adding pages from: {file_path}")
logger.warning(f"Skipping file {file}: {reason}")
logger.error(f"Merge failed: {error}", exc_info=True)
```

---

## 8. Performance

### 8.1 Performance-Ziele
- **Single Operation**: < 5 seconds for 10 PDFs × 10 pages = 100 pages total
- **Memory**: < 500 MB peak usage
- **Scalability**: Handle up to 100 PDFs in one operation

### 8.2 Optimierungen
- [x] Lazy loading: Pages loaded on-demand
- [x] Streaming: Write pages incrementally (nicht alles im Memory halten)
- [ ] Optional: Parallel processing for independent PDFs (future enhancement)
- [x] Generator pattern für große Page-Collections

### 8.3 Performance Profiling Points
```python
import time

class PDFMerger:
    def __init__(self):
        self.stats = {
            'total_time': 0,
            'read_time': 0,
            'merge_time': 0,
            'write_time': 0
        }

    def merge_with_profiling(self, files):
        start = time.time()
        # ... merge logic
        self.stats['total_time'] = time.time() - start
```

---

## 9. Testbarkeit

### 9.1 Test-Strategie

#### Unit Tests
```python
# Beispiel: Dependency Injection für Testbarkeit
def test_merge_with_mock_reader():
    mock_reader = MockPDFReader()
    merger = PDFMerger(reader=mock_reader)

    result = merger.add_pdf(Path("test.pdf"))

    assert mock_reader.read_called
    assert result.pages_merged > 0
```

#### Integration Tests
```python
def test_merge_workflow_end_to_end(pdf_simple_text, pdf_multipage, temp_dir):
    result = merge_pdfs(
        files=[pdf_simple_text, pdf_multipage],
        output_path=temp_dir / "merged.pdf"
    )

    assert result.success
    assert result.output_path.exists()
    assert result.pages_merged == 11  # 1 + 10
```

### 9.2 Test-Coverage-Ziel
- **Unit Tests**: > 90%
- **Integration Tests**: > 80%
- **E2E Tests**: Critical paths covered

### 9.3 Testbare Komponenten
```python
# validators.py - Pure functions, einfach testbar
def validate_input_files(files: List[Path]) -> List[Path]:
    # Keine Side-effects, nur Validierung
    pass

# processors.py - DI-enabled, mockbar
class PDFMerger:
    def __init__(self, reader: PDFReaderInterface = None):
        self.reader = reader or DefaultPDFReader()
```

---

## 10. Security

### 10.1 Sicherheitsüberlegungen
- [x] Path Traversal verhindert durch `validate_pdf_path()`
- [x] Input-Sanitization für Dateinamen
- [x] Keine System-Befehle (nur Python-Libraries)
- [x] Keine sensiblen Daten im Log

### 10.2 Input-Validierung
```python
# ALLE User-Inputs werden validiert:
validated_files = [
    validate_pdf_path(f, must_exist=True)
    for f in user_provided_files
]

validated_output = validate_output_path(
    user_output_path,
    create_dirs=True
)
```

---

## 11. Migration & Backwards Compatibility

### 11.1 Breaking Changes
Keine - Dies ist die initiale Implementation (v1.0)

### 11.2 Migrations-Pfad
N/A (erste Version)

---

## 12. Implementierungs-Plan

### 12.1 Phasen
1. **Phase 1**: Core Infrastructure (2-3h)
   - [x] models.py: MergeResult, MergeConfig
   - [x] validators.py: validate_input_files
   - [x] processors.py: PDFMerger class (basic)

2. **Phase 2**: Core Logic (3-4h)
   - [x] core.py: merge_pdfs() function
   - [x] Fehlerbehandlung
   - [x] Logging

3. **Phase 3**: CLI & Integration (2-3h)
   - [x] cli.py: Argparse integration
   - [x] Exit codes
   - [x] Help text

4. **Phase 4**: Advanced Features (2-3h)
   - [ ] Lesezeichen-Erhaltung (optional)
   - [ ] Progress Callback
   - [ ] Performance-Optimierung

### 12.2 Geschätzter Aufwand
- **Total**: 10-13 Stunden
- **Priorität 1** (MVP): Phasen 1-3 (7-10h)
- **Priorität 2** (Nice-to-have): Phase 4 (2-3h)

---

## 13. Review & Approval

### Architektur-Review
**Reviewer**: Architecture Team
**Datum**: 2025-11-22
**Status**: ✅ Approved

**Checkpoints**:
- [x] SOLID Principles eingehalten ✅
- [x] DRY (Don't Repeat Yourself) ✅
- [x] Klare Separation of Concerns ✅
- [x] Testbarkeit gewährleistet (DI) ✅
- [x] Type Hints verwendet ✅
- [x] Docstrings vorhanden ✅
- [x] Error Handling robust ✅
- [x] Performance-Ziele erreichbar ✅

**Comments**: Design entspricht vollständig den Architecture Guidelines. Dependency Injection korrekt implementiert, Test-Strategie klar, Performance-Optimierungen sinnvoll.

### Team-Review
- [ ] Python Entwickler: Implementation feasible?
- [ ] Tester: Test strategy clear?
- [ ] DevOps: Deployment considerations?

---

## 14. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | Architecture Team | REQ-001 v1.0 |

---

## 15. Anhang

### 15.1 Referenzen
- Requirement: [REQ-001 v1.0](../requirements/REQ-001-pdf-merge.md)
- PyPDF2 Documentation: https://pypdf2.readthedocs.io/
- Architecture Guidelines: [ARCHITECTURE_GUIDELINES.md](../architecture/ARCHITECTURE_GUIDELINES.md)

### 15.2 Offene Fragen
1. ~~Sollen Formular-Felder erhalten bleiben?~~ → Nein, out of scope
2. ~~Performance-Ziel realistisch?~~ → Ja, mit Lazy Loading
3. Progress Callback API Design? → TBD mit Entwickler
