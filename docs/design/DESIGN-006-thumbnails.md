# Design Document: PDF Thumbnails

**ID**: DESIGN-006
**Version**: 1.0
**Requirement**: [REQ-006](../requirements/REQ-006-thumbnails.md) v1.0
**Status**: Implemented
**Architekt**: System Architect
**Entwickler**: Python Developer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-006 v1.0
- Tested by: TEST-006 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Entwicklung eines Moduls zur Generierung von Thumbnail-Bildern aus PDF-Seiten mit konfigurierbaren Größen und Formaten.

### 1.2 Scope
**In Scope:**
- PDF-Seiten zu Bildern konvertieren
- Verschiedene Thumbnail-Größen (small, medium, large, custom)
- Ausgabeformate PNG und JPG
- Seitenauswahl (einzelne, Bereiche, alle)
- Qualitätskontrolle für JPG

**Out of Scope:**
- Video-Thumbnails
- Animierte Thumbnails
- OCR auf Thumbnails
- Wasserzeichen auf Thumbnails

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/thumbnails/
├── __init__.py           # Public API exports
├── models.py             # Data structures (Config, Result, Enums)
├── validators.py         # Input validation
├── generators.py         # PDF → Image generation
├── core.py              # Main functionality
├── exceptions.py         # Module-specific exceptions
└── cli.py               # CLI interface
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────┐
│   CLI Layer     │  (cli.py)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │  (validators.py)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Core Logic     │  (core.py)
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Generator      │  (generators.py)
│  - pdf2image    │
│  - Pillow       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Image Files    │  (PNG/JPG)
└─────────────────┘
```

### 2.3 Datenfluss
1. **Input-Validierung**: PDF-Datei, Größe, Format, Seiten
2. **PDF → Image**: pdf2image konvertiert PDF-Seiten zu PIL Images
3. **Resize**: Pillow skaliert Bilder auf gewünschte Größe
4. **Output**: Speichern als PNG/JPG mit konfigurierbarer Qualität

---

## 3. API Design

### 3.1 Öffentliche Funktionen

#### 3.1.1 Hauptfunktion
```python
def generate_thumbnails(
    input_path: str | Path,
    output_dir: str | Path | None = None,
    size: ThumbnailSize | tuple[int, int] = ThumbnailSize.MEDIUM,
    format: ThumbnailFormat = ThumbnailFormat.PNG,
    pages: list[int] | None = None,
    quality: int = 85,
    verbose: bool = False
) -> ThumbnailResult:
    """
    Generate thumbnail images from PDF pages.

    Args:
        input_path: Path to input PDF file
        output_dir: Directory for output thumbnails (default: ./thumbnails)
        size: Thumbnail size (enum or (width, height) tuple)
        format: Output format (PNG or JPG)
        pages: List of page numbers to process (1-indexed), None = all pages
        quality: JPEG quality 1-100 (ignored for PNG)
        verbose: Enable detailed logging

    Returns:
        ThumbnailResult: Object with generation results

    Raises:
        PDFNotFoundError: If input file doesn't exist
        PDFProcessingError: If PDF is corrupted or unreadable
        ValidationError: If parameters are invalid
        FileWriteError: If output directory is not writable

    Example:
        >>> result = generate_thumbnails(
        ...     "document.pdf",
        ...     size=ThumbnailSize.LARGE,
        ...     format=ThumbnailFormat.JPG
        ... )
        >>> print(f"Created {result.thumbnails_created} thumbnails")
    """
    pass
```

### 3.2 Klassen

#### 3.2.1 PDFThumbnailGenerator
```python
class PDFThumbnailGenerator:
    """
    Generator for creating thumbnails from PDF pages.

    Uses pdf2image for PDF→Image conversion and Pillow for resizing.
    """

    def __init__(self, config: ThumbnailConfig):
        """Initialize generator with configuration"""
        self.config = config

    def generate(
        self,
        pdf_path: Path,
        pages: list[int] | None = None
    ) -> list[Image.Image]:
        """
        Convert PDF pages to PIL Images.

        Args:
            pdf_path: Path to PDF file
            pages: Page numbers to convert (1-indexed)

        Returns:
            List of PIL Image objects
        """
        pass

    def resize_image(self, image: Image.Image) -> Image.Image:
        """Resize image to target size maintaining aspect ratio"""
        pass

    def save_thumbnail(
        self,
        image: Image.Image,
        output_path: Path
    ) -> None:
        """Save image to file with specified format and quality"""
        pass
```

### 3.3 Datenmodelle

```python
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional

class ThumbnailSize(Enum):
    """Predefined thumbnail sizes"""
    SMALL = (150, 150)
    MEDIUM = (300, 300)
    LARGE = (600, 600)

class ThumbnailFormat(Enum):
    """Output image formats"""
    PNG = "png"
    JPG = "jpg"

@dataclass
class ThumbnailConfig:
    """Configuration for thumbnail generation"""
    size: tuple[int, int]
    format: ThumbnailFormat
    quality: int = 85
    dpi: int = 200
    verbose: bool = False

@dataclass
class ThumbnailResult:
    """Result of thumbnail generation operation"""
    status: str  # 'success' | 'error' | 'partial'
    thumbnails_created: int = 0
    thumbnail_paths: list[Path] = field(default_factory=list)
    message: str = ""
    skipped_pages: list[int] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """Returns True if generation was successful"""
        return self.status == 'success'
```

---

## 4. Dependencies

### 4.1 Interne Dependencies
- `pdftools.core.validators`: Input validation
- `pdftools.core.exceptions`: Error handling

### 4.2 Externe Dependencies
| Library | Version | Zweck | Lizenz |
|---------|---------|-------|--------|
| pdf2image | >= 1.16.0 | PDF to Image conversion | MIT |
| Pillow (PIL) | >= 10.0.0 | Image processing and resizing | PIL License |
| poppler-utils | (system) | Backend for pdf2image | GPL |

**Installation:**
```bash
pip install pdf2image Pillow

# System dependency (Ubuntu/Debian)
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

---

## 5. Fehlerbehandlung

### 5.1 Exception-Hierarchie
```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── PDFProcessingError
│   ├── PDFCorruptedError
│   └── PDFConversionError
├── ValidationError
│   ├── InvalidSizeError
│   ├── InvalidFormatError
│   └── InvalidPageRangeError
└── FileWriteError
```

### 5.2 Fehlerszenarien
| Fehler | Exception | Nachricht | Recovery |
|--------|-----------|-----------|----------|
| PDF nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch |
| Korruptes PDF | PDFCorruptedError | "PDF file is corrupted" | Abbruch |
| Ungültige Größe | InvalidSizeError | "Invalid size: {size}" | Abbruch |
| Seite nicht vorhanden | InvalidPageRangeError | "Page {n} out of range" | Überspringen |
| Schreibfehler | FileWriteError | "Cannot write to {path}" | Abbruch |

---

## 6. Konfiguration

### 6.1 Config-Struktur
```python
@dataclass
class ThumbnailConfig:
    """Configuration for thumbnail generation"""
    size: tuple[int, int]
    format: ThumbnailFormat
    quality: int = 85
    dpi: int = 200  # DPI for PDF rendering
    verbose: bool = False
```

### 6.2 Config-Quellen (Priorität absteigend)
1. CLI-Argumente
2. Environment Variables
3. Defaults

---

## 7. Logging & Monitoring

### 7.1 Log-Levels
- **DEBUG**: PDF conversion details, resize operations
- **INFO**: Processing started/completed, files created
- **WARNING**: Skipped pages, missing dependencies
- **ERROR**: Conversion failures, I/O errors
- **CRITICAL**: Fatal errors

### 7.2 Log-Format
```python
import logging

logger = logging.getLogger('pdftools.thumbnails')

# Beispiele:
logger.info(f"Processing PDF: {input_path}")
logger.info(f"Generating thumbnail for page {page_num}")
logger.info(f"Saved thumbnail: {output_path}")
logger.warning(f"Skipping corrupted page: {page_num}")
logger.error(f"Failed to convert page {page_num}: {error}")
```

---

## 8. Performance

### 8.1 Performance-Ziele
- Einzelne Seite: < 1 Sekunde (medium size)
- 10 Seiten: < 10 Sekunden
- 100 Seiten: < 100 Sekunden
- Speicherverbrauch: < 200 MB

### 8.2 Optimierungen
- [x] DPI-Optimierung (200 DPI Standard)
- [x] Lazy loading (pdf2image generiert nur angeforderte Seiten)
- [x] Aspect ratio preservation (keine unnötigen Pixel)
- [ ] Parallele Verarbeitung (multiprocessing) - Future enhancement

---

## 9. Testbarkeit

### 9.1 Test-Strategie

#### Unit Tests
- Validators isoliert testen (Mock File I/O)
- Generator mit Mock PIL Images
- Size calculations
- Format conversions

#### Integration Tests
- Kompletter Flow mit echten PDFs
- File I/O
- Error handling

#### E2E Tests
- CLI mit verschiedenen Optionen
- Verschiedene PDF-Typen
- Performance-Tests

### 9.2 Test-Coverage-Ziel
- Unit Tests: > 90%
- Integration Tests: > 80%
- Gesamt: > 85%

### 9.3 Testbare Komponenten
```python
# Dependency Injection für Testbarkeit
class PDFThumbnailGenerator:
    def __init__(
        self,
        config: ThumbnailConfig,
        pdf_converter: Optional[Callable] = None
    ):
        self.config = config
        self._pdf_converter = pdf_converter or convert_from_path
```

---

## 10. Security

### 10.1 Sicherheitsüberlegungen
- [x] Input-Validierung (Path Traversal verhindern)
- [x] Sanitization von Dateinamen
- [x] Sichere Datei-Operationen
- [x] Keine sensiblen Daten im Log
- [x] Begrenzte Ressourcennutzung (DPI-Limit)

### 10.2 Permissions
- Minimale Dateisystem-Rechte: Lesen (Input), Schreiben (Output)
- Keine privilegierten Operationen

---

## 11. Implementierungs-Plan

### 11.1 Phasen
1. **Phase 1**: Datenmodelle und Validierung
   - [x] models.py (Enums, Config, Result)
   - [x] validators.py (Input validation)
   - [x] exceptions.py (Error handling)

2. **Phase 2**: Core-Logik
   - [x] generators.py (PDFThumbnailGenerator)
   - [x] core.py (generate_thumbnails)

3. **Phase 3**: CLI & Integration
   - [x] cli.py (Argparse-based CLI)
   - [x] __init__.py (Public API)

### 11.2 Geschätzter Aufwand
- Phase 1: 2 Stunden
- Phase 2: 3 Stunden
- Phase 3: 2 Stunden
- **Total**: 7 Stunden

---

## 12. Review & Approval

### Architektur-Review
**Reviewer**: System Architect
**Datum**: 2025-11-22
**Status**: ✅ Approved

**Kommentare**:
- pdf2image + Pillow ist die richtige Wahl
- Aspect ratio preservation wichtig
- DPI-Konfiguration gut gelöst

### Code-Review Checkpoints
- [x] SOLID Principles eingehalten
- [x] DRY (Don't Repeat Yourself)
- [x] Klare Separation of Concerns
- [x] Testbarkeit gewährleistet
- [x] Type Hints verwendet
- [x] Docstrings vorhanden
- [x] Error Handling robust

### Team-Review
- [x] Python Entwickler: Approved - Clean architecture
- [x] Tester: Approved - Good testability
- [x] DevOps: Approved - poppler dependency documented

---

## 13. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | System Architect | REQ-006 v1.0 |

---

## 14. Anhang

### 14.1 Referenzen
- [pdf2image Documentation](https://pdf2image.readthedocs.io/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [REQ-006](../requirements/REQ-006-thumbnails.md)

### 14.2 Offene Fragen
- Keine
