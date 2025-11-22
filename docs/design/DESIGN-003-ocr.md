# Design Document: PDF OCR Processing

**ID**: DESIGN-003
**Version**: 1.0
**Requirement**: [REQ-003](../requirements/REQ-003-ocr.md) v1.0
**Status**: Released
**Architekt**: Architecture Team
**Entwickler**: Python Development Team
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-003 v1.0
- Tested by: TEST-003 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Implementierung eines robusten OCR-Moduls für PDF-Dokumente mit Tesseract-Integration, Unterstützung mehrerer Sprachen und verschiedener Output-Formate unter Berücksichtigung von Performance, Testbarkeit und Best Practices.

### 1.2 Scope
**In Scope:**
- OCR für gescannte PDFs (ohne Textebene)
- Multi-Language Support (deu, eng, fra, ita, spa)
- Output-Formate: TXT, PDF with Text Layer, JSON
- CLI und programmatisches Interface
- Tesseract Integration via pytesseract
- Docker-Support für Tesseract

**Out of Scope:**
- Automatische Spracherkennung (future enhancement)
- Layout-Analyse (future enhancement)
- Handschrifterkennung (out of scope)
- Cloud-basierte OCR-Services

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/ocr/
├── __init__.py              # Public API exports
├── models.py                # Datenmodelle (Config, Result, Enums)
├── validators.py            # Input-Validierung, Tesseract-Check
├── ocr_engine.py            # Tesseract Engine Wrapper
├── core.py                  # Hauptlogik, Orchestrierung
├── cli.py                   # CLI Interface
└── README.md                # Modul-Dokumentation
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────┐
│   CLI Layer     │  (cli.py)
│  pdftools-ocr   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │  (validators.py)
│  - validate_pdf │
│  - validate_    │
│    language     │
│  - check_       │
│    tesseract    │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Core Logic     │  (core.py)
│  - perform_ocr()│
│  - orchestrate  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  OCR Engine     │  (ocr_engine.py)
│  - Tesseract    │
│    Engine       │
│  - PDF→Image    │
│  - Image→Text   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Output Writer  │  (core.py)
│  - TXT Writer   │
│  - PDF Writer   │
│  - JSON Writer  │
└─────────────────┘
```

### 2.3 Datenfluss
1. **CLI**: Benutzer ruft `pdftools-ocr` auf
2. **Validation**: PDF, Sprache, Tesseract-Installation validiert
3. **Core**: `perform_ocr()` orchestriert OCR-Prozess
4. **Engine**: Konvertiert PDF→Images, führt OCR durch
5. **Output**: Schreibt Ergebnis im gewählten Format
6. **Result**: Erfolgsmeldung oder Fehler wird zurückgegeben

---

## 3. API Design

### 3.1 Öffentliche Funktionen

#### 3.1.1 Hauptfunktion
```python
from pathlib import Path
from typing import Optional, List
from .models import OCRResult, OCRConfig, OCRLanguage, OutputMode

def perform_ocr(
    input_path: Path,
    output_path: Optional[Path] = None,
    language: OCRLanguage | List[OCRLanguage] = OCRLanguage.GERMAN,
    output_mode: OutputMode = OutputMode.TXT,
    config: Optional[OCRConfig] = None
) -> OCRResult:
    """
    Perform OCR on a PDF document.

    Args:
        input_path: Path to input PDF file
        output_path: Output path. If None, creates '{filename}_ocr.{ext}'
        language: OCR language(s) - single or multiple
        output_mode: Output format (TXT, PDF, JSON)
        config: Optional configuration (pages, DPI, etc.)

    Returns:
        OCRResult: Object containing status, output path, and metadata

    Raises:
        PDFNotFoundError: If input file doesn't exist
        TesseractNotFoundError: If Tesseract is not installed
        LanguageNotAvailableError: If language data not found
        OCRProcessingError: If OCR fails

    Example:
        >>> result = perform_ocr(
        ...     input_path=Path("scan.pdf"),
        ...     output_path=Path("output.txt"),
        ...     language=OCRLanguage.GERMAN
        ... )
        >>> print(result.status)
        'success'
    """
    pass
```

### 3.2 Klassen

#### 3.2.1 TesseractEngine (OCR Engine)
```python
from typing import Protocol, List
from PIL import Image
import pytesseract

class OCREngineInterface(Protocol):
    """Interface for OCR engines (enables mocking)"""
    def process_image(self, image: Image.Image, language: str) -> str:
        ...

class TesseractEngine:
    """Tesseract OCR Engine implementation"""

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize Tesseract engine.

        Args:
            tesseract_cmd: Path to tesseract binary (optional)
        """
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        self._verify_tesseract()

    def _verify_tesseract(self) -> None:
        """Verify Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
        except Exception as e:
            raise TesseractNotFoundError(
                "Tesseract not found. Install tesseract-ocr or use Docker."
            ) from e

    def process_image(
        self,
        image: Image.Image,
        language: str,
        config: Optional[str] = None
    ) -> dict:
        """
        Process single image with OCR.

        Args:
            image: PIL Image object
            language: Tesseract language code (e.g., 'deu', 'eng')
            config: Optional Tesseract config string

        Returns:
            dict: {'text': str, 'confidence': float}
        """
        data = pytesseract.image_to_data(
            image,
            lang=language,
            config=config or '',
            output_type=pytesseract.Output.DICT
        )

        text = pytesseract.image_to_string(
            image,
            lang=language,
            config=config or ''
        )

        # Calculate average confidence
        confidences = [c for c in data['conf'] if c != -1]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        return {
            'text': text,
            'confidence': avg_confidence / 100.0  # Normalize to 0-1
        }

    def get_available_languages(self) -> List[str]:
        """Get list of installed Tesseract languages"""
        return pytesseract.get_languages(config='')
```

### 3.3 Datenmodelle

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

class OCRLanguage(str, Enum):
    """Supported OCR languages"""
    GERMAN = "deu"
    ENGLISH = "eng"
    FRENCH = "fra"
    ITALIAN = "ita"
    SPANISH = "spa"

class OutputMode(str, Enum):
    """Output format modes"""
    TXT = "txt"
    PDF = "pdf"
    JSON = "json"

@dataclass
class OCRConfig:
    """Configuration for OCR operation"""
    pages: Optional[List[int]] = None  # None = all pages
    dpi: int = 300
    tesseract_config: Optional[str] = None
    progress_callback: Optional[Callable[[int, int], None]] = None
    verbose: bool = False

@dataclass
class OCRResult:
    """Result of OCR operation"""
    status: str  # 'success' | 'error' | 'partial'
    output_path: Optional[Path] = None
    message: str = ""
    pages_processed: int = 0
    total_pages: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    # metadata includes: avg_confidence, processing_time, language_used, etc.

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
| pytesseract | >= 0.3.10 | Tesseract Python Wrapper | Apache 2.0 |
| pdf2image | >= 1.16.0 | PDF → Image Konvertierung | MIT |
| Pillow | >= 10.0.0 | Image Processing | HPND |
| tesseract-ocr | >= 4.0.0 | OCR Engine (System) | Apache 2.0 |

---

## 5. Fehlerbehandlung

### 5.1 Exception-Hierarchie
```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── OCRProcessingError (new)
│   ├── TesseractNotFoundError (new)
│   ├── LanguageNotAvailableError (new)
│   └── ImageConversionError (new)
└── ValidationError
    ├── InvalidPathError
    └── InvalidParameterError
```

### 5.2 Fehlerszenarien
| Fehler | Exception | Nachricht | Recovery |
|--------|-----------|-----------|----------|
| PDF nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch |
| Tesseract fehlt | TesseractNotFoundError | "Tesseract not found. Install tesseract-ocr or use Docker." | Abbruch |
| Sprache fehlt | LanguageNotAvailableError | "Language '{lang}' not available. Install tessdata-{lang}" | Abbruch |
| Image-Konvertierung | ImageConversionError | "Failed to convert page {n} to image" | Skip page (optional) |
| OCR fehlgeschlagen | OCRProcessingError | "OCR failed for page {n}: {reason}" | Skip page (optional) |

---

## 6. Konfiguration

### 6.1 Config-Struktur
```python
@dataclass
class OCRConfig:
    pages: Optional[List[int]] = None  # None = all
    dpi: int = 300
    tesseract_config: Optional[str] = None
    progress_callback: Optional[Callable] = None
    verbose: bool = False
```

### 6.2 Config-Quellen (Priorität absteigend)
1. Function parameters (highest)
2. Environment variables (`PDFTOOLS_OCR_*`, `TESSERACT_CMD`)
3. Defaults

### 6.3 Environment Variables
- `PDFTOOLS_OCR_LANGUAGE`: Default OCR language (e.g., "deu")
- `TESSERACT_CMD`: Path to tesseract binary
- `PDFTOOLS_OCR_DPI`: Default DPI for PDF→Image (default: 300)

---

## 7. Logging & Monitoring

### 7.1 Log-Levels
- **DEBUG**: "Converting page {n} to image (DPI: {dpi})"
- **INFO**: "Processing page {n}/{total} with OCR"
- **WARNING**: "Low confidence on page {n}: {conf:.2%}"
- **ERROR**: "OCR failed for page {n}: {error}"

### 7.2 Log-Format
```python
import logging

logger = logging.getLogger('pdftools.ocr')

logger.info(f"Starting OCR for {input_path} (language: {language})")
logger.debug(f"Converting page {page_num} to image")
logger.warning(f"Low OCR confidence on page {n}: {conf:.2%}")
logger.error(f"OCR failed for page {n}: {error}", exc_info=True)
```

---

## 8. Performance

### 8.1 Performance-Ziele
- **Single Page**: < 5 seconds per page (A4, 300dpi)
- **Memory**: < 1 GB peak usage
- **Scalability**: Handle 100+ page documents

### 8.2 Optimierungen
- [x] Lazy loading: Process pages one at a time
- [x] Memory cleanup: Delete images after processing
- [x] DPI optimization: Configurable DPI (lower = faster)
- [ ] Optional: Parallel processing for multi-page PDFs (future)
- [x] Generator pattern für Page-Processing

### 8.3 Performance Profiling
```python
import time

class TesseractEngine:
    def __init__(self):
        self.stats = {
            'total_time': 0,
            'conversion_time': 0,
            'ocr_time': 0,
            'pages_processed': 0
        }

    def process_page_with_profiling(self, page):
        start = time.time()
        # ... OCR logic
        self.stats['total_time'] += time.time() - start
```

---

## 9. Testbarkeit

### 9.1 Test-Strategie

#### Unit Tests
```python
# Beispiel: Dependency Injection für Testbarkeit
def test_ocr_with_mock_engine():
    mock_engine = MockTesseractEngine()
    mock_engine.set_result({'text': 'Test', 'confidence': 0.95})

    result = perform_ocr_with_engine(
        Path("test.pdf"),
        engine=mock_engine
    )

    assert result.success
    assert result.metadata['avg_confidence'] == 0.95
```

#### Integration Tests
```python
def test_ocr_workflow_end_to_end(scanned_pdf, temp_dir):
    result = perform_ocr(
        input_path=scanned_pdf,
        output_path=temp_dir / "output.txt",
        language=OCRLanguage.GERMAN
    )

    assert result.success
    assert result.output_path.exists()
    assert result.pages_processed > 0
    assert result.metadata['avg_confidence'] > 0.5
```

### 9.2 Test-Coverage-Ziel
- **Unit Tests**: > 85%
- **Integration Tests**: > 75%
- **E2E Tests**: Critical paths covered

### 9.3 Testbare Komponenten
```python
# validators.py - Pure functions, einfach testbar
def validate_language(lang: OCRLanguage) -> bool:
    # Keine Side-effects, nur Validierung
    pass

# ocr_engine.py - DI-enabled, mockbar
class TesseractEngine:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd
```

---

## 10. Security

### 10.1 Sicherheitsüberlegungen
- [x] Path Traversal verhindert durch `validate_pdf_path()`
- [x] Input-Sanitization für Dateinamen
- [x] Keine System-Befehle via Shell (nur pytesseract)
- [x] Keine sensiblen Daten im Log (nur Dateinamen, keine Inhalte)
- [x] Temporäre Images werden nach Verarbeitung gelöscht

### 10.2 Input-Validierung
```python
# ALLE User-Inputs werden validiert:
validated_pdf = validate_pdf_path(
    user_input_path,
    must_exist=True
)

validated_language = validate_language(user_language)

if not check_tesseract():
    raise TesseractNotFoundError("Tesseract not installed")
```

---

## 11. Output-Format-Spezifikationen

### 11.1 TXT-Format
```
Page 1:
{extracted text from page 1}

\f

Page 2:
{extracted text from page 2}

\f
...
```

### 11.2 PDF-Format
- Original-PDF mit eingefügter Textebene
- Invisible text layer über Bild
- Searchable & Selectable
- Original-Layout bleibt erhalten

### 11.3 JSON-Format
```json
{
  "file": "input.pdf",
  "language": "deu",
  "total_pages": 5,
  "processed_at": "2025-11-22T10:30:00Z",
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text...",
      "confidence": 0.95,
      "word_count": 250
    },
    {
      "page_number": 2,
      "text": "More text...",
      "confidence": 0.92,
      "word_count": 180
    }
  ],
  "metadata": {
    "avg_confidence": 0.935,
    "total_words": 430,
    "processing_time_seconds": 12.5
  }
}
```

---

## 12. Implementierungs-Plan

### 12.1 Phasen
1. **Phase 1**: Core Infrastructure (2-3h)
   - [x] models.py: OCRResult, OCRConfig, OCRLanguage, OutputMode
   - [x] validators.py: validate_language, validate_pdf, check_tesseract
   - [x] ocr_engine.py: TesseractEngine class (basic)

2. **Phase 2**: OCR Logic (3-4h)
   - [x] ocr_engine.py: PDF→Image conversion, OCR processing
   - [x] core.py: perform_ocr() function
   - [x] Output writers (TXT, PDF, JSON)

3. **Phase 3**: CLI & Integration (2-3h)
   - [x] cli.py: Replace stub with full CLI
   - [x] Exit codes
   - [x] Help text

4. **Phase 4**: Testing & Refinement (2-3h)
   - [x] Unit tests
   - [x] Integration tests
   - [x] Documentation

### 12.2 Geschätzter Aufwand
- **Total**: 10-13 Stunden
- **Priorität 1** (MVP): Phasen 1-3 (7-10h)
- **Priorität 2** (Testing): Phase 4 (2-3h)

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

**Comments**: Design entspricht vollständig den Architecture Guidelines. Tesseract-Integration via pytesseract ist State-of-the-Art. Output-Formate gut definiert.

### Team-Review
- [x] Python Entwickler: ✅ Implementation feasible
- [x] Tester: ✅ Test strategy clear
- [x] DevOps: ✅ Docker integration planned

---

## 14. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | Architecture Team | REQ-003 v1.0 |

---

## 15. Anhang

### 15.1 Referenzen
- Requirement: [REQ-003 v1.0](../requirements/REQ-003-ocr.md)
- pytesseract Documentation: https://pypi.org/project/pytesseract/
- Tesseract OCR: https://github.com/tesseract-ocr/tesseract
- pdf2image: https://pypi.org/project/pdf2image/
- Architecture Guidelines: [ARCHITECTURE_GUIDELINES.md](../architecture/ARCHITECTURE_GUIDELINES.md)

### 15.2 Offene Fragen
1. ~~Output-Formate definiert?~~ → Ja, TXT/PDF/JSON
2. ~~Tesseract-Installation dokumentieren?~~ → Ja, Docker-Container vorhanden
3. ~~Mehrsprachigkeit implementieren?~~ → Ja, mehrere Sprachen gleichzeitig möglich
