# MCP PDF Tools

Eine umfassende Sammlung von Python-basierten PDF-Verarbeitungstools für verschiedene Anwendungsfälle.

## Projektübersicht

Dieses Projekt bietet eine modulare Suite von Werkzeugen zur Verarbeitung von PDF-Dokumenten. Jedes Tool ist als eigenständiges Python-Skript implementiert und kann über die Kommandozeile aufgerufen werden.

---

## Requirements & Traceability

Alle Features sind durch versionierte Requirements dokumentiert. Jedes Requirement ist mit Design-Dokumenten, Implementation und Test-Reports verknüpft.

### Requirements Index

Aktuelle Requirements (detaillierte Dokumentation in `docs/requirements/`):

| ID | Feature | Version | Status | Dokument |
|----|---------|---------|--------|----------|
| REQ-001 | PDF Merge | 1.0 | ✅ Released | [REQ-001-pdf-merge.md](docs/requirements/REQ-001-pdf-merge.md) |
| REQ-002 | PDF Split | 1.0 | Planned | docs/requirements/REQ-002-pdf-split.md |
| REQ-003 | OCR Processing | 1.0 | Planned | docs/requirements/REQ-003-ocr.md |
| REQ-004 | PDF Protection | 1.0 | Planned | docs/requirements/REQ-004-protection.md |
| REQ-005 | Text Extraction | 1.0 | Planned | docs/requirements/REQ-005-text-extraction.md |
| REQ-006 | Thumbnail Generation | 1.0 | Planned | docs/requirements/REQ-006-thumbnails.md |
| REQ-007 | Invoice Renaming | 1.0 | Planned | docs/requirements/REQ-007-invoice-renaming.md |

**Vollständige Traceability**: Siehe [TRACEABILITY_MATRIX.md](docs/TRACEABILITY_MATRIX.md)

### Versionierungs-System

**Requirements Versionierung**:
- Format: `REQ-<NUMBER>-<short-name>.md`
- Versionen: Semantic Versioning (MAJOR.MINOR.PATCH)
- Jedes Requirement referenziert Design und Tests

**Document Traceability Chain**:
```
REQ-XXX v1.0 → DESIGN-XXX v1.0 → Implementation → TEST-XXX v1.0
```

**Wichtig**: Test Reports referenzieren immer eine spezifische Requirement-Version!

---

## Features & Tools

### 1. PDF Merge
**Requirement**: [REQ-001](docs/requirements/REQ-001-pdf-merge.md) v1.0
**Status**: ✅ Released
**Modul**: `src/pdftools/merge/`
**Test Report**: [TEST-001](docs/test_reports/TEST-001-pdf-merge.md) v1.0

**Zweck**: Zusammenführen mehrerer PDF-Dateien zu einem einzelnen Dokument

**Hauptfunktionalität**:
- Akzeptiert komma-separierte Liste von PDF-Dateien
- Zusammenführung aller Seiten in der angegebenen Reihenfolge
- Anpassbarer Ausgabepfad (Standard: `merged.pdf` im Verzeichnis der ersten Datei)
- Lesezeichen und Metadaten bleiben erhalten
- Performance: < 5s für 10 PDFs mit je 10 Seiten

**Verwendung**:
```bash
pdftools-merge -f "file1.pdf,file2.pdf,file3.pdf" -o "output.pdf"
```

**Abhängigkeiten**: PyPDF2
**Dokumentation**: Siehe [REQ-001](docs/requirements/REQ-001-pdf-merge.md) für vollständige Spezifikation

---

### 2. PDF Split
**Requirement**: REQ-002 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/split/`

**Zweck**: Aufteilung einer PDF-Datei in einzelne Seiten

**Hauptfunktionalität**:
- Erstellt für jede Seite eine separate PDF-Datei
- Automatische Benennung: `[filename]_page_N.pdf`
- Batch-Verarbeitung mehrerer PDFs

---

### 3. Text Extraction
**Requirement**: REQ-005 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/text_extraction/`

**Zweck**: Extrahieren von Text aus PDF-Dokumenten

**Hauptfunktionalität**:
- Extrahiert Text von allen Seiten eines PDFs
- Ausgabe wahlweise in Datei oder stdout
- Pfad-Normalisierung für Dateien mit Leerzeichen
- Fehlerbehandlung mit aussagekräftigen Meldungen

**Abhängigkeiten**: PyMuPDF (fitz), pytesseract

---

### 4. PDF Protection
**Requirement**: REQ-004 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/protection/`

**Zweck**: Schreibschutz für PDF-Dateien durch Verschlüsselung

**Hauptfunktionalität**:
- Verschlüsselt PDF mit Owner-Passwort
- Deaktiviert alle Bearbeitungsberechtigungen (inkl. Annotations)
- Leeres User-Passwort (Datei kann geöffnet werden, aber nicht bearbeitet)
- 128-bit Verschlüsselung
- Ausgabe: `[filename]_protected.pdf`

**Abhängigkeiten**: PyPDF2

---

### 5. Thumbnail Generation
**Requirement**: REQ-006 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/thumbnails/`

**Zweck**: Generierung von PNG-Thumbnails aus PDF-Dateien

**Hauptfunktionalität**:
- Erstellt Thumbnail der ersten Seite
- Rekursive Verzeichnissuche
- Batch-Verarbeitung
- Ausgabe: `[filename].png`

**Abhängigkeiten**: PyMuPDF (fitz), glob2

---

### 6. OCR Processing
**Requirement**: REQ-003 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/ocr/`

**Zweck**: OCR-Verarbeitung von PDFs über Docker-Container

**Hauptfunktionalität**:
- Batch-Verarbeitung mehrerer PDF-Dateien
- Docker-basierte OCR mit ocrmypdf
- Force-OCR Modus (auch bei vorhandenem Text)
- Optionales Löschen der Originaldatei
- Farbiges Logging mit Debug-Modus
- Ausgabe: `[filename]_ocr.pdf`

**Abhängigkeiten**: Docker, ocrmypdf

---

### 7. Invoice Renaming
**Requirement**: REQ-007 v1.0 (geplant)
**Status**: Planned
**Modul**: `src/pdftools/renaming/`

**Zweck**: Intelligente Umbenennung von Rechnungs-PDFs basierend auf extrahierten Metadaten

**Hauptfunktionalität**:
- Regex-basierte Extraktion von Metadaten (Rechnungsnr, Bestellnr, Datum, Firma)
- Konfigurierbar über JSON-Datei für mehrere Lieferanten
- Textextraktion aus PDF
- Ausgabe: `YYYYMMDD_order_invoice_company_renamed.pdf`

**Abhängigkeiten**: PyMuPDF (fitz), pytesseract

---

## Technologie-Stack

### Haupt-Bibliotheken:
- **PyPDF2**: PDF Manipulation (Merge, Protection)
- **PyMuPDF (fitz)**: Text-Extraktion, Rendering, Thumbnails
- **pdfrw**: PDF Splitting
- **pytesseract**: OCR (über Docker)
- **glob2**: Erweiterte Dateisystem-Navigation

### Externe Tools:
- **Docker**: OCR-Verarbeitung mit ocrmypdf

## Deployment & Ausführung

Alle Tools sind als eigenständige Python-Skripte implementiert und können direkt über die Kommandozeile ausgeführt werden. Icons (`.ico` Dateien) sind für Desktop-Integration vorhanden.

### Verfügbare Icons:
- `merge.ico` - PDF Merge
- `split.ico` - PDF Split
- `txt.ico` - Text Extraction
- `thumb.ico` - Thumbnails
- `ocr.ico` - OCR Utility
- `rename-icon.ico` - Invoice Renamer

## Entwicklungshinweise

### Gemeinsame Muster:
1. Alle Tools verwenden `argparse` für CLI-Argumente
2. Pfad-Normalisierung mit `os.path.expanduser()` und `os.path.abspath()`
3. Fehlerbehandlung mit Try-Except Blöcken
4. Logging für Debug-Informationen

### Dateinamen-Konventionen:
- `*_protected.pdf` - Geschützte PDFs
- `*_page_N.pdf` - Aufgeteilte Seiten
- `*_ocr.pdf` - OCR-verarbeitete PDFs
- `*_renamed.pdf` - Umbenannte Rechnungen
- `*.png` - Thumbnails

## Zukünftige Erweiterungen

Mögliche Verbesserungen und neue Features:

1. **Batch-Verarbeitung**: Einheitliche Batch-Verarbeitung für alle Tools
2. **GUI**: Desktop-Anwendung für nicht-technische Benutzer
3. **Metadaten-Extraktion**: Erweiterte Metadaten-Analyse
4. **PDF-Kompression**: Dateigröße-Optimierung
5. **Wasserzeichen**: Automatisches Hinzufügen von Wasserzeichen
6. **Signatur-Verifizierung**: Überprüfung digitaler Signaturen
7. **MCP Server**: Integration als Model Context Protocol Server für AI-Assistenten

## Docker-Integration

Das Projekt enthält eine `docker-compose.yml` für einfaches Deployment und Ausführung in containerisierten Umgebungen.

---

## Team-Workflow & Entwicklungsprozess

### Team-Rollen

Unser Entwicklungsteam besteht aus folgenden spezialisierten Rollen:

#### 1. Requirements Engineer
**Verantwortlichkeiten**:
- Anforderungen vom Stakeholder aufnehmen
- Requirements ins `context.md` und `docs/requirements/` einpflegen
- Requirements-Template (`templates/requirement_template.md`) verwenden
- Akzeptanzkriterien definieren
- Requirements mit Team reviewen

#### 2. Architekt
**Verantwortlichkeiten**:
- Design-Dokumente erstellen (`templates/design_template.md`)
- Architektur-Richtlinien durchsetzen (`docs/architecture/ARCHITECTURE_GUIDELINES.md`)
- Code-Reviews durchführen (Best Practices, SOLID Principles)
- Testbarkeit sicherstellen
- Technische Entscheidungen treffen

#### 3. Python Entwickler
**Verantwortlichkeiten**:
- Features implementieren nach Design-Vorgaben
- Unit Tests schreiben (>90% Coverage)
- Code-Qualität sicherstellen (Type Hints, Docstrings)
- Design mit Architekt abstimmen
- Code Reviews durchführen

#### 4. DevOps/Setup Entwickler
**Verantwortlichkeiten**:
- Installationsskripte warten (`scripts/install.sh`, `scripts/install.ps1`)
- Setup-Prozess optimieren
- CI/CD Pipeline konfigurieren
- Docker-Integration
- Dependency-Management

#### 5. Tester
**Verantwortlichkeiten**:
- Test-Cases entwickeln
- Test-PDFs erstellen (`scripts/generate_test_pdfs.py`)
- Funktionen testen (Unit, Integration, E2E)
- Test-Reports erstellen (`templates/test_report_template.md`)
- Regressionstests durchführen

---

### Entwicklungs-Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. REQUIREMENTS PHASE                     │
│  Requirements Engineer erstellt Anforderungsdokument        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. TEAM REVIEW                            │
│  Alle Rollen reviewen Requirements                          │
│  - Architekt: Technische Machbarkeit                        │
│  - Entwickler: Aufwands-Schätzung                           │
│  - Tester: Testbarkeit                                      │
│  - DevOps: Setup-Anforderungen                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. DESIGN PHASE                           │
│  Entwickler + Architekt erstellen Design-Dokument           │
│  - Modul-Struktur                                           │
│  - API Design                                               │
│  - Testbarkeit                                              │
│  - Performance-Überlegungen                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    4. ARCHITECTURE REVIEW                    │
│  Architekt prüft Design gegen Guidelines                    │
│  - SOLID Principles                                         │
│  - Testbarkeit                                              │
│  - Best Practices                                           │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    5. IMPLEMENTATION PHASE                   │
│  Entwickler implementiert Feature                           │
│  - Code nach Design-Vorgaben                                │
│  - Unit Tests (>90% Coverage)                               │
│  - Type Hints & Docstrings                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    6. CODE REVIEW                            │
│  Architekt reviewt Code                                     │
│  - Architektur-Konformität                                  │
│  - Code-Qualität                                            │
│  - Test Coverage                                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    7. TESTING PHASE                          │
│  Tester führt Tests durch                                   │
│  - Funktionale Tests                                        │
│  - Integration Tests                                        │
│  - E2E Tests                                                │
│  - Performance Tests                                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    8. TEST REPORT                            │
│  Tester erstellt Test-Report                                │
│  - Coverage-Statistiken                                     │
│  - Fehler-Dokumentation                                     │
│  - Release-Empfehlung                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    9. RELEASE                                │
│  Bei erfolgreichen Tests: Feature wird released             │
│  Bei Fehlern: Zurück zu Phase 5 (Bugfixes)                  │
└─────────────────────────────────────────────────────────────┘
```

---

### Projekt-Struktur (Version 2.0)

```
mcp_pdftools/
├── src/pdftools/              # Modularisierter Source Code
│   ├── __init__.py
│   ├── core/                  # Gemeinsame Utilities
│   │   ├── __init__.py
│   │   ├── exceptions.py      # Exception-Hierarchie
│   │   ├── validators.py      # Input-Validierung
│   │   └── utils.py           # Helper-Funktionen
│   ├── merge/                 # PDF Merge Module
│   ├── split/                 # PDF Split Module
│   ├── ocr/                   # OCR Module
│   ├── protection/            # PDF Protection Module
│   ├── text_extraction/       # Text Extraction Module
│   ├── thumbnails/            # Thumbnail Generation Module
│   └── renaming/              # Invoice Renaming Module
│
├── tests/                     # Test-Suite
│   ├── conftest.py            # Pytest Configuration & Fixtures
│   ├── unit/                  # Unit Tests
│   ├── integration/           # Integration Tests
│   ├── e2e/                   # End-to-End Tests
│   └── fixtures/              # Test-PDFs
│
├── docs/                      # Dokumentation
│   ├── requirements/          # Requirements-Dokumente
│   ├── design/                # Design-Dokumente
│   ├── architecture/          # Architektur-Richtlinien
│   │   └── ARCHITECTURE_GUIDELINES.md
│   └── test_reports/          # Test-Reports
│
├── scripts/                   # Utilities & Tools
│   ├── generate_test_pdfs.py  # Test-PDF Generator
│   ├── install.sh             # Installation (Linux/Mac)
│   └── install.ps1            # Installation (Windows)
│
├── templates/                 # Team-Workflow Templates
│   ├── requirement_template.md
│   ├── design_template.md
│   └── test_report_template.md
│
├── pytest.ini                 # Pytest Configuration
├── setup.py                   # Package Setup
├── requirements.txt           # Dependencies
├── context.md                 # Dieses Dokument
└── README.md                  # Hauptdokumentation
```

---

### Standard Modul-Struktur

Jedes neue Feature folgt dieser Struktur:

```
src/pdftools/[module_name]/
├── __init__.py          # Public API Exports
├── core.py              # Hauptlogik & Orchestrierung
├── validators.py        # Input-Validierung
├── processors.py        # Verarbeitungslogik
├── formatters.py        # Output-Formatierung
├── exceptions.py        # Modul-spezifische Exceptions (optional)
├── models.py            # Datenmodelle (dataclasses)
├── config.py            # Konfiguration (optional)
└── cli.py               # CLI Interface
```

**Layer-Architektur:**
```
CLI → Validators → Core → Processors → Formatters → File I/O
```

---

### Templates & Dokumentation

#### Requirements Template
Speicherort: `templates/requirement_template.md`

Enthält:
- Funktionale Anforderungen
- Nicht-funktionale Anforderungen (Performance, Qualität)
- Akzeptanzkriterien
- Test-Anforderungen
- Team-Review-Checkboxes

#### Design Template
Speicherort: `templates/design_template.md`

Enthält:
- Architektur-Übersicht
- API Design
- Fehlerbehandlung
- Testbarkeit
- Performance-Überlegungen
- Architektur-Review-Checkboxes

#### Test Report Template
Speicherort: `templates/test_report_template.md`

Enthält:
- Coverage-Statistiken
- Test-Ergebnisse (Unit, Integration, E2E)
- Performance-Benchmarks
- Fehler-Dokumentation
- Release-Empfehlung

---

### Test-Strategie

#### 1. Unit Tests
**Ziel**: >90% Coverage
**Fokus**: Einzelne Funktionen isoliert testen

```python
# Beispiel: tests/unit/test_merge_core.py
def test_merge_two_pdfs(pdf_simple_text, pdf_multipage, temp_dir):
    merger = PDFMerger()
    result = merger.merge([pdf_simple_text, pdf_multipage], temp_dir / "out.pdf")
    assert result.status == "success"
    assert result.output_path.exists()
```

#### 2. Integration Tests
**Ziel**: >80% Coverage
**Fokus**: Zusammenspiel mehrerer Komponenten

```python
# Beispiel: tests/integration/test_merge_workflow.py
def test_merge_workflow_end_to_end(multiple_pdfs, output_dir):
    # Validation → Core → Processing → Output
    result = merge_pdfs_workflow(multiple_pdfs, output_dir / "merged.pdf")
    assert result.success
```

#### 3. E2E Tests
**Fokus**: CLI-Interface & reale Szenarien

```python
# Beispiel: tests/e2e/test_merge_cli.py
def test_cli_merge_command(multiple_pdfs, temp_dir):
    cmd = ["pdftools-merge", "-f", ",".join(map(str, multiple_pdfs)), "-o", str(temp_dir / "out.pdf")]
    result = subprocess.run(cmd, capture_output=True)
    assert result.returncode == 0
```

#### Test-PDF Generator
```bash
# Alle Test-PDFs generieren
python scripts/generate_test_pdfs.py --all

# Spezifische Test-PDFs
python scripts/generate_test_pdfs.py --simple --multipage 10
python scripts/generate_test_pdfs.py --with-image --with-ocr
python scripts/generate_test_pdfs.py --encrypted --corrupted
```

**Verfügbare Test-PDFs**:
- Simple Text (1 Seite, nur Text)
- Multipage (10-500 Seiten)
- Mit Bildern (ohne OCR)
- Mit Bildern (mit OCR-Text)
- Verschlüsselt
- Korrupt/Invalid
- Large (Performance-Tests)

---

### Installation & Setup

#### Linux/Mac:
```bash
./scripts/install.sh
```

#### Windows:
```powershell
.\scripts\install.ps1
```

#### Manuelle Installation:
```bash
# Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
.\venv\Scripts\Activate.ps1  # Windows

# Dependencies
pip install -r requirements.txt

# Package (Development Mode)
pip install -e .

# Development Dependencies
pip install -e ".[dev]"

# Test-PDFs generieren
python scripts/generate_test_pdfs.py --all

# Tests ausführen
pytest -v --cov=src/pdftools
```

---

### Qualitätssicherung

#### Code-Qualität Tools
```bash
# Linting
flake8 src/
pylint src/

# Type Checking
mypy src/

# Code Formatting
black src/
isort src/

# Tests mit Coverage
pytest -v --cov=src/pdftools --cov-report=html
```

#### Code Review Checklist
- [ ] SOLID Principles befolgt
- [ ] Type Hints vorhanden
- [ ] Docstrings vollständig
- [ ] Tests geschrieben (>90% Unit, >80% Integration)
- [ ] Keine Code-Duplizierung
- [ ] Error Handling vollständig
- [ ] Performance-Ziele erfüllt
- [ ] Security: Input-Validierung
- [ ] Architektur-Guidelines befolgt

---

### Best Practices

#### 1. Dependency Injection für Testbarkeit
```python
class PDFProcessor:
    def __init__(self, reader: PDFReaderInterface = None):
        self.reader = reader or DefaultPDFReader()
```

#### 2. Type Hints verwenden
```python
def merge_pdfs(files: List[Path], output: Path) -> Result:
    pass
```

#### 3. Docstrings (Google Style)
```python
def process(path: Path) -> Result:
    """
    Process a PDF file.

    Args:
        path: Path to PDF file

    Returns:
        Result object with processing info

    Raises:
        PDFNotFoundError: If file doesn't exist
    """
    pass
```

#### 4. Proper Exception Handling
```python
try:
    result = process_pdf(path)
except PDFNotFoundError:
    logger.error(f"File not found: {path}")
    raise
except PDFProcessingError as e:
    logger.error(f"Processing failed: {e}")
    raise
```

---

### Weitere Dokumentation

Detaillierte Dokumentation verfügbar in:
- `README.md` - Hauptdokumentation
- `docs/architecture/ARCHITECTURE_GUIDELINES.md` - Architektur-Richtlinien
- `templates/` - Workflow-Templates
- `*.md` - Tool-spezifische Dokumentation
