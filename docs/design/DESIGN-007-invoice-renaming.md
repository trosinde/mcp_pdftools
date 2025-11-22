# Design Document: Invoice Renaming

**ID**: DESIGN-007
**Version**: 1.0
**Requirement**: [REQ-007](../requirements/REQ-007-invoice-renaming.md) v1.0
**Status**: Released
**Architekt**: Architecture Team
**Entwickler**: Python Development Team
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-007 v1.0
- Tested by: TEST-007 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Implementierung eines intelligenten PDF-Renaming-Systems für Rechnungen, das Text-Extraktion, Pattern-Matching und Template-basierte Umbenennung kombiniert.

### 1.2 Scope
**In Scope:**
- Text-Extraktion aus PDFs (via `pdftools.text_extraction`)
- Regex-basierte Daten-Extraktion (Invoice Nr, Date, Vendor)
- Template-System für Dateinamen
- Batch-Processing
- Dry-Run Modus
- Custom Pattern Support

**Out of Scope:**
- OCR für gescannte Rechnungen (zukünftiges Feature)
- Datenbank-Integration
- Automatische Kategorisierung

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/renaming/
├── __init__.py              # Public API exports
├── models.py                # Datenmodelle (InvoiceData, RenameConfig, RenameResult, NamingTemplate)
├── validators.py            # Template- und Pattern-Validierung
├── patterns.py              # Vordefinierte Regex-Patterns
├── extractors.py            # Invoice-Daten-Extraktion
├── core.py                  # Hauptlogik (rename_invoice, batch_rename)
└── cli.py                   # CLI Interface
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────┐
│   CLI Layer     │  (cli.py)
│   pdfrename     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │  (validators.py)
│  - validate_    │
│    template     │
│  - validate_    │
│    patterns     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Core Logic     │  (core.py)
│  - rename_      │
│    invoice()    │
│  - batch_rename │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Extractors     │  (extractors.py)
│  - Invoice      │
│    DataExtractor│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ Text Extraction │  (pdftools.text_extraction)
│  - extract_text │
└─────────────────┘
```

### 2.3 Datenfluss
1. **Input**: PDF-Datei + Template + Optional Custom Patterns
2. **Text Extraction**: `text_extraction.extract_text()` extrahiert Text
3. **Pattern Matching**: `InvoiceDataExtractor` wendet Regex-Patterns an
4. **Template Rendering**: `NamingTemplate` generiert neuen Dateinamen
5. **Validation**: Prüfe ob Zieldatei schon existiert
6. **Rename**: Benenne Datei um (oder simuliere in Dry-Run)
7. **Result**: Rückgabe von `RenameResult` mit Status

---

## 3. API Design

### 3.1 Hauptfunktion

```python
from pathlib import Path
from typing import Optional, Dict
from .models import RenameResult, RenameConfig

def rename_invoice(
    input_path: Path,
    template: str = "{vendor}_{invoice_nr}_{date}.pdf",
    custom_patterns: Optional[Dict[str, str]] = None,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
    config: Optional[RenameConfig] = None
) -> RenameResult:
    """
    Rename invoice PDF based on extracted data.

    Args:
        input_path: Path to invoice PDF
        template: Naming template with placeholders
        custom_patterns: Custom regex patterns for extraction
        output_dir: Target directory (default: same as input)
        dry_run: If True, only simulate rename
        config: Optional configuration

    Returns:
        RenameResult: Object containing status, old/new names, extracted data

    Raises:
        PDFNotFoundError: If input file doesn't exist
        InvalidTemplateError: If template is invalid
        PDFProcessingError: If extraction fails

    Example:
        >>> result = rename_invoice(
        ...     Path("invoice.pdf"),
        ...     template="{vendor}_{date}.pdf"
        ... )
        >>> print(f"{result.old_name} -> {result.new_name}")
    """
    pass
```

### 3.2 Batch-Processing

```python
from typing import List

def batch_rename(
    input_paths: List[Path],
    template: str = "{vendor}_{invoice_nr}_{date}.pdf",
    custom_patterns: Optional[Dict[str, str]] = None,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
    config: Optional[RenameConfig] = None
) -> List[RenameResult]:
    """
    Rename multiple invoice PDFs.

    Args:
        input_paths: List of PDF paths
        template: Naming template
        custom_patterns: Custom patterns
        output_dir: Target directory
        dry_run: Simulation mode
        config: Optional configuration

    Returns:
        List[RenameResult]: Results for each file
    """
    pass
```

### 3.3 Klassen

#### 3.3.1 InvoiceDataExtractor

```python
from typing import Optional, Dict
from .models import InvoiceData
from .patterns import DEFAULT_PATTERNS

class InvoiceDataExtractor:
    """Extracts invoice data from PDF text using regex patterns"""

    def __init__(self, custom_patterns: Optional[Dict[str, str]] = None):
        """
        Initialize extractor with patterns.

        Args:
            custom_patterns: Override default patterns
        """
        self.patterns = {**DEFAULT_PATTERNS}
        if custom_patterns:
            self.patterns.update(custom_patterns)

    def extract(self, text: str) -> InvoiceData:
        """
        Extract invoice data from text.

        Args:
            text: PDF text content

        Returns:
            InvoiceData: Extracted fields (may have None values)
        """
        invoice_nr = self._extract_invoice_number(text)
        date = self._extract_date(text)
        vendor = self._extract_vendor(text)

        return InvoiceData(
            invoice_number=invoice_nr,
            date=date,
            vendor=vendor
        )

    def _extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number using regex"""
        pattern = self.patterns.get('invoice_nr')
        if not pattern:
            return None

        import re
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else None

    def _extract_date(self, text: str) -> Optional[str]:
        """Extract and normalize date"""
        # Implementation with multiple date format support
        pass

    def _extract_vendor(self, text: str) -> Optional[str]:
        """Extract vendor/supplier name"""
        pass
```

#### 3.3.2 NamingTemplate

```python
from typing import Dict, Optional
from .models import InvoiceData

class NamingTemplate:
    """Handles template rendering for file names"""

    def __init__(self, template: str):
        """
        Initialize with template string.

        Args:
            template: Template with placeholders like {vendor}_{date}.pdf

        Raises:
            InvalidTemplateError: If template is invalid
        """
        self.template = template
        self._validate()

    def _validate(self) -> None:
        """Validate template has valid placeholders"""
        import re
        placeholders = re.findall(r'\{(\w+)\}', self.template)

        valid_placeholders = {
            'vendor', 'invoice_nr', 'date',
            'year', 'month', 'day'
        }

        invalid = set(placeholders) - valid_placeholders
        if invalid:
            raise InvalidTemplateError(
                f"Invalid placeholders: {invalid}"
            )

    def render(self, data: InvoiceData) -> str:
        """
        Render template with invoice data.

        Args:
            data: Extracted invoice data

        Returns:
            Rendered filename

        Note:
            Missing data fields will be replaced with 'unknown'
        """
        values = {
            'vendor': data.vendor or 'unknown',
            'invoice_nr': data.invoice_number or 'unknown',
            'date': data.date or 'unknown',
            'year': data.year or 'unknown',
            'month': data.month or 'unknown',
            'day': data.day or 'unknown'
        }

        # Sanitize values (remove invalid filename chars)
        values = {
            k: self._sanitize_filename(v)
            for k, v in values.items()
        }

        return self.template.format(**values)

    def _sanitize_filename(self, name: str) -> str:
        """Remove invalid filename characters"""
        import re
        # Remove/replace invalid chars for Windows/Linux/macOS
        invalid_chars = r'[<>:"/\\|?*]'
        return re.sub(invalid_chars, '_', name)
```

### 3.4 Datenmodelle

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict
from datetime import date

@dataclass
class InvoiceData:
    """Extracted invoice data"""
    invoice_number: Optional[str] = None
    date: Optional[str] = None
    vendor: Optional[str] = None

    @property
    def year(self) -> Optional[str]:
        """Extract year from date if available"""
        if self.date:
            try:
                return self.date.split('-')[0]
            except:
                return None
        return None

    @property
    def month(self) -> Optional[str]:
        """Extract month from date if available"""
        if self.date:
            try:
                return self.date.split('-')[1]
            except:
                return None
        return None

    @property
    def day(self) -> Optional[str]:
        """Extract day from date if available"""
        if self.date:
            try:
                return self.date.split('-')[2]
            except:
                return None
        return None

@dataclass
class RenameConfig:
    """Configuration for rename operation"""
    fallback_name: str = "renamed"
    handle_duplicates: bool = True  # Add _1, _2, etc.
    verbose: bool = False
    max_filename_length: int = 255

@dataclass
class RenameResult:
    """Result of rename operation"""
    status: str  # 'success' | 'error' | 'skipped'
    old_name: str
    new_name: Optional[str] = None
    extracted_data: Optional[InvoiceData] = None
    message: str = ""
    dry_run: bool = False

    @property
    def success(self) -> bool:
        return self.status == 'success'

@dataclass
class NamingTemplate:
    """Template for generating filenames"""
    template: str
    # Validation happens in __post_init__
```

---

## 4. Pattern-System

### 4.1 Vordefinierte Patterns

```python
# patterns.py
DEFAULT_PATTERNS = {
    # Invoice Number Patterns
    'invoice_nr': r'(?:Invoice|Rechnung|Bill)\s*(?:Number|Nr\.?|#)?\s*:?\s*([A-Z0-9\-]+)',

    # Date Patterns (ISO format preferred)
    'date': r'(?:Date|Datum)\s*:?\s*(\d{4}-\d{2}-\d{2}|\d{2}\.\d{2}\.\d{4}|\d{2}/\d{2}/\d{4})',

    # Vendor Patterns
    'vendor': r'(?:From|Von|Vendor|Supplier)\s*:?\s*([A-Z][a-zA-Z\s&\.]{2,30})',
}

# Vendor-specific patterns (more precise)
VENDOR_SPECIFIC_PATTERNS = {
    'amazon': {
        'invoice_nr': r'Order\s*#?\s*(\d{3}-\d{7}-\d{7})',
        'vendor': r'Amazon',
    },
    'paypal': {
        'invoice_nr': r'Transaction\s*ID\s*:?\s*([A-Z0-9]{17})',
        'vendor': r'PayPal',
    },
}
```

### 4.2 Custom Pattern Loading

```python
import json
from pathlib import Path
from typing import Dict

def load_custom_patterns(pattern_file: Path) -> Dict[str, str]:
    """
    Load custom patterns from JSON file.

    Args:
        pattern_file: Path to JSON file with patterns

    Returns:
        Dictionary of pattern names to regex strings

    Example JSON:
        {
            "invoice_nr": "Invoice\\s*#\\s*(\\d+)",
            "vendor": "Company:\\s*([A-Z]+)"
        }
    """
    with open(pattern_file, 'r', encoding='utf-8') as f:
        return json.load(f)
```

---

## 5. Dependencies

### 5.1 Interne Dependencies
- `pdftools.text_extraction`: Text-Extraktion aus PDFs
- `pdftools.core.exceptions`: Exception-Hierarchie
- `pdftools.core.validators`: Path-Validierung

### 5.2 Externe Dependencies
| Library | Version | Zweck | Lizenz |
|---------|---------|-------|--------|
| (Standard Library) | - | re, datetime, pathlib, json | Python License |

---

## 6. Fehlerbehandlung

### 6.1 Exception-Hierarchie
```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── PDFProcessingError
│   └── TextExtractionError
└── ValidationError
    ├── InvalidTemplateError (new)
    └── InvalidPatternError (new)
```

### 6.2 Fehlerszenarien
| Fehler | Exception | Nachricht | Recovery |
|--------|-----------|-----------|----------|
| PDF nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch |
| Template ungültig | InvalidTemplateError | "Invalid template: {reason}" | Abbruch |
| Pattern ungültig | InvalidPatternError | "Invalid regex pattern: {pattern}" | Abbruch |
| Keine Daten extrahiert | - | Warnung | Fallback-Name |
| Zieldatei existiert | - | Warnung | Nummeriertes Suffix |

---

## 7. Logging & Monitoring

### 7.1 Log-Levels
- **DEBUG**: "Applying pattern: {pattern}"
- **INFO**: "Extracted: invoice_nr={nr}, vendor={vendor}"
- **WARNING**: "Could not extract {field} from {file}"
- **ERROR**: "Failed to rename {file}: {error}"

### 7.2 Verbose Output
```python
# Verbose mode output
if config.verbose:
    print(f"Processing: {input_path.name}")
    print(f"  Extracted Invoice #: {data.invoice_number}")
    print(f"  Extracted Date: {data.date}")
    print(f"  Extracted Vendor: {data.vendor}")
    print(f"  New name: {new_name}")
```

---

## 8. Performance

### 8.1 Performance-Ziele
- **Single PDF**: < 3 seconds
- **Batch (100 PDFs)**: < 5 minutes
- **Memory**: < 200 MB

### 8.2 Optimierungen
- [x] Text-Extraktion cached (wenn möglich)
- [x] Regex kompiliert und wiederverwendet
- [x] Lazy evaluation für Batch-Processing
- [x] Keine unnötigen File I/O Operationen

---

## 9. Testbarkeit

### 9.1 Test-Strategie

#### Unit Tests
```python
def test_invoice_data_extractor_with_mock_text():
    extractor = InvoiceDataExtractor()
    text = "Invoice Number: INV-2024-001\nDate: 2024-03-15\nFrom: Amazon"

    data = extractor.extract(text)

    assert data.invoice_number == "INV-2024-001"
    assert data.date == "2024-03-15"
    assert data.vendor == "Amazon"

def test_naming_template_render():
    template = NamingTemplate("{vendor}_{invoice_nr}.pdf")
    data = InvoiceData(
        invoice_number="12345",
        vendor="TestCorp"
    )

    result = template.render(data)

    assert result == "TestCorp_12345.pdf"

def test_template_sanitizes_invalid_chars():
    template = NamingTemplate("{vendor}.pdf")
    data = InvoiceData(vendor="Test/Corp")

    result = template.render(data)

    assert "/" not in result
    assert result == "Test_Corp.pdf"
```

#### Integration Tests
```python
def test_rename_invoice_end_to_end(sample_invoice_pdf, tmp_path):
    result = rename_invoice(
        input_path=sample_invoice_pdf,
        template="{vendor}_{invoice_nr}.pdf",
        output_dir=tmp_path
    )

    assert result.success
    assert result.new_name is not None
    assert (tmp_path / result.new_name).exists()
```

### 9.2 Test-Coverage-Ziel
- **Unit Tests**: > 90%
- **Integration Tests**: > 80%

---

## 10. Security

### 10.1 Sicherheitsüberlegungen
- [x] Path Traversal verhindert durch Validierung
- [x] Filename Sanitization (keine Shell-Injections möglich)
- [x] Regex-Patterns geprüft (keine ReDoS-Anfälligkeit)
- [x] Keine sensiblen Daten im Log

### 10.2 Filename Sanitization
```python
def _sanitize_filename(self, name: str) -> str:
    """
    Remove characters invalid in filenames across platforms.

    Removes: < > : " / \ | ? *
    Replaces with: _
    """
    import re
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, '_', name)

    # Remove control characters
    sanitized = ''.join(c for c in sanitized if ord(c) >= 32)

    return sanitized.strip()
```

---

## 11. Implementierungs-Plan

### 11.1 Phasen
1. **Phase 1**: Data Models (1h)
   - [x] models.py: InvoiceData, RenameConfig, RenameResult

2. **Phase 2**: Validators & Patterns (1-2h)
   - [x] validators.py: Template/Pattern validation
   - [x] patterns.py: Default patterns

3. **Phase 3**: Extractors (2-3h)
   - [x] extractors.py: InvoiceDataExtractor

4. **Phase 4**: Core Logic (2-3h)
   - [x] core.py: rename_invoice, batch_rename

5. **Phase 5**: CLI (1-2h)
   - [x] cli.py: Argparse integration

### 11.2 Geschätzter Aufwand
- **Total**: 7-11 Stunden
- **MVP**: Phasen 1-4 (6-9h)
- **Polish**: Phase 5 (1-2h)

---

## 12. Review & Approval

### Architektur-Review
**Reviewer**: Architecture Team
**Datum**: 2025-11-22
**Status**: ✅ Approved

**Checkpoints**:
- [x] SOLID Principles eingehalten ✅
- [x] Wiederverwendung von text_extraction ✅
- [x] Klare Separation of Concerns ✅
- [x] Testbarkeit gewährleistet ✅
- [x] Type Hints verwendet ✅
- [x] Error Handling robust ✅

---

## 13. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | Architecture Team | REQ-007 v1.0 |

---

## 14. Anhang

### 14.1 Referenzen
- Requirement: [REQ-007 v1.0](../requirements/REQ-007-invoice-renaming.md)
- Architecture Guidelines: [ARCHITECTURE_GUIDELINES.md](../architecture/ARCHITECTURE_GUIDELINES.md)

### 14.2 Beispiel Pattern JSON
```json
{
    "invoice_nr": "Invoice\\s*#\\s*(\\d{4,})",
    "date": "Date:\\s*(\\d{4}-\\d{2}-\\d{2})",
    "vendor": "From:\\s*([A-Z][a-zA-Z\\s]+)"
}
```
