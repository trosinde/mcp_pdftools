# Feature Requirement: PDF OCR Processing

**ID**: REQ-003
**Version**: 1.0
**Status**: Released
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-003 v1.0
- Test Report: TEST-003 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
OCR (Optical Character Recognition) für gescannte PDF-Dokumente ohne Textebene. Extraktion von Text mittels Tesseract OCR mit Unterstützung mehrerer Sprachen und verschiedenen Output-Formaten.

### 1.2 Geschäftsziel
Viele gescannte Dokumente (Rechnungen, Verträge, historische Dokumente) liegen nur als Bilddaten vor und können nicht durchsucht oder kopiert werden. Dieses Feature ermöglicht die lokale OCR-Verarbeitung ohne Upload zu externen Cloud-Services, wodurch Datenschutz und Vertraulichkeit gewährleistet bleiben.

### 1.3 Betroffene Module
- [ ] PDF Merge
- [ ] PDF Split
- [ ] Text Extraction
- [x] OCR
- [ ] PDF Protection
- [ ] Thumbnails
- [ ] Invoice Renamer
- [ ] Neues Modul: N/A

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** Benutzer
**möchte ich** Text aus gescannten PDF-Dokumenten extrahieren
**damit** ich diese durchsuchen, kopieren und weiterverarbeiten kann

**Akzeptanzkriterien:**
1. [x] OCR für PDFs ohne Textebene (reine Bild-PDFs)
2. [x] Unterstützung mehrerer Sprachen (deu, eng, fra, ita, spa)
3. [x] Output-Formate: TXT, PDF with Text Layer, JSON
4. [x] Automatische Spracherkennung optional
5. [x] Batch-Processing mehrerer PDFs
6. [x] Klare Fehlermeldung wenn Tesseract nicht installiert

### 2.2 Input
- **Format**: PDF-Dateien (gescannt, ohne Textebene)
- **Parameter**:
  - `-f, --file`: PDF-Dateipfad (Pflicht)
  - `-o, --output`: Ausgabepfad (Optional, Default: `{filename}_ocr.{format}`)
  - `-l, --language`: Sprache(n) für OCR (Optional, Default: deu)
  - `--output-mode`: Output-Format (txt|pdf|json) (Optional, Default: txt)
  - `--pages`: Seiten-Range "1-5,7,9-12" (Optional, Default: alle)
  - `--verbose`: Detaillierte Ausgaben (Optional)
- **Validierung**:
  - Input-Datei muss existieren
  - Input-Datei muss valides PDF sein
  - Sprache muss unterstützt sein
  - Output-Pfad muss schreibbar sein
  - Tesseract muss installiert sein

### 2.3 Output
- **Formate**:
  - **TXT**: Reiner Text, Seiten durch Formfeed getrennt
  - **PDF**: Original-PDF mit eingefügter Textebene (searchable PDF)
  - **JSON**: Strukturierte Ausgabe mit Text pro Seite, Confidence-Werten
- **Benennung**:
  - Standard: `{original_name}_ocr.{ext}` im gleichen Verzeichnis
  - Custom: Vom Benutzer angegebener Pfad
- **Fehlerbehandlung**:
  - Bei ungültigem PDF: Fehler ausgeben, Abbruch
  - Bei fehlender Sprach-Datei: Klare Fehlermeldung mit Download-Hinweis
  - Bei fehlendem Tesseract: Klare Fehlermeldung mit Docker-Hinweis

### 2.4 Verhalten
- **Erfolgsszenario**:
  1. Benutzer gibt PDF-Datei und Sprache an
  2. System validiert Input und prüft Tesseract
  3. System konvertiert PDF-Seiten zu Bildern
  4. System führt OCR für jede Seite durch
  5. System speichert Ergebnis im gewählten Format
  6. System gibt Erfolgsmeldung mit Pfad zur Output-Datei aus

- **Fehlerszenarios**:
  1. **Input-Datei nicht gefunden**:
     - Fehlermeldung: "PDF file not found: {path}"
     - Exit Code: 1
  2. **Tesseract nicht installiert**:
     - Fehlermeldung: "Tesseract OCR not found. Please install tesseract-ocr or use Docker container."
     - Exit Code: 2
  3. **Sprache nicht verfügbar**:
     - Fehlermeldung: "Language '{lang}' not available. Please install tessdata-{lang}"
     - Exit Code: 3
  4. **OCR fehlgeschlagen**:
     - Fehlermeldung: "OCR processing failed for page {n}: {reason}"
     - Exit Code: 1

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Verarbeitungszeit: < 5 Sekunden pro Seite (A4, 300dpi)
- Speicherverbrauch: < 1 GB auch für große PDFs
- Batch-Verarbeitung: Bis zu 50 PDFs in einem Durchlauf

### 3.2 Qualität
- Testabdeckung: > 85% (Unit Tests)
- Code-Qualität: Pylint Score > 8.0
- Dokumentation: Vollständige Docstrings (Google Style)
- Type Hints: Für alle öffentlichen Funktionen
- OCR Accuracy: > 95% für gut gescannte Dokumente (300dpi)

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme: Windows, Linux, macOS
- Dependencies:
  - pytesseract >= 0.3.10
  - pdf2image >= 1.16.0
  - Pillow >= 10.0.0
  - tesseract-ocr (System-Dependency)

---

## 4. Technische Details

### 4.1 Abhängigkeiten
- **Neue Libraries**:
  - pytesseract: Python-Wrapper für Tesseract
  - pdf2image: PDF → Image Konvertierung (bereits vorhanden von REQ-006)
  - Pillow: Image Processing (bereits vorhanden von REQ-006)
- **Externe Tools**:
  - tesseract-ocr (System-Binary oder Docker)
  - poppler-utils (für pdf2image)
- **Bestehende Module**:
  - `pdftools.core.validators` für Input-Validierung
  - `pdftools.core.exceptions` für Fehlerbehandlung
  - `pdftools.core.utils` für Pfad-Normalisierung

### 4.2 Konfiguration
- **Konfigurationsdateien**: Keine erforderlich
- **Environment Variables**:
  - `PDFTOOLS_OCR_LANGUAGE`: Default OCR-Sprache (Optional, Default: deu)
  - `TESSERACT_CMD`: Pfad zu tesseract Binary (Optional, für Custom-Installation)
- **Defaults**:
  - Language: deu (Deutsch)
  - Output Mode: txt
  - Output Path: `{filename}_ocr.{ext}`

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für Tesseract Engine
- [x] Edge Cases:
  - Leere PDFs
  - Ein-Seiten PDFs
  - Multi-Page PDFs (100+ Seiten)
  - PDFs mit schlechter Scan-Qualität
  - PDFs mit mehrsprachigem Text
  - Nicht-unterstützte Sprachen

### 5.2 Integration Tests
- [x] Zusammenspiel von Validation → OCR → Output
- [x] File I/O korrekt
- [x] Fehlerbehandlung End-to-End
- [x] Verschiedene Output-Formate

### 5.3 E2E Tests
- [x] CLI funktioniert wie erwartet
- [x] Reale gescannte PDFs verarbeitet
- [x] Performance-Tests mit verschiedenen DPI-Werten

### 5.4 Test-Daten
Benötigte Test-PDFs:
- [x] Gescanntes PDF (1 Seite, Deutsch)
- [x] Multi-Page gescanntes PDF (10 Seiten)
- [x] Schlechte Scan-Qualität (niedrige DPI)
- [x] Mehrsprachiges PDF (Deutsch + Englisch)
- [x] PDF mit Tabellen
- [x] PDF mit Bildern und Text gemischt

---

## 6. Beispiele

### 6.1 CLI-Verwendung
```bash
# Beispiel 1: Grundlegende Verwendung (Deutsch)
pdftools-ocr -f "scanned_invoice.pdf" -l deu

# Beispiel 2: Mehrere Sprachen, PDF-Output
pdftools-ocr -f "document.pdf" -l "deu+eng" --output-mode pdf -o "searchable.pdf"

# Beispiel 3: Nur bestimmte Seiten
pdftools-ocr -f "contract.pdf" -l deu --pages "1-5,10" --output-mode txt

# Beispiel 4: JSON-Output für Weiterverarbeitung
pdftools-ocr -f "receipt.pdf" -l eng --output-mode json -o "receipt.json"

# Beispiel 5: Verbose-Modus
pdftools-ocr -f "scan.pdf" -l deu --verbose
```

### 6.2 Programmatische Verwendung
```python
from pdftools.ocr import perform_ocr
from pdftools.ocr.models import OCRLanguage, OutputMode
from pathlib import Path

# Einfache OCR (TXT-Output)
result = perform_ocr(
    input_path=Path("scanned.pdf"),
    output_path=Path("output.txt"),
    language=OCRLanguage.GERMAN
)

# PDF mit Textebene erstellen
result = perform_ocr(
    input_path=Path("scan.pdf"),
    output_path=Path("searchable.pdf"),
    language=OCRLanguage.GERMAN,
    output_mode=OutputMode.PDF
)

# JSON-Output mit mehreren Sprachen
result = perform_ocr(
    input_path=Path("multilang.pdf"),
    output_path=Path("result.json"),
    language=[OCRLanguage.GERMAN, OCRLanguage.ENGLISH],
    output_mode=OutputMode.JSON
)

# Ergebnis prüfen
if result.success:
    print(f"OCR completed: {result.output_path}")
    print(f"Pages processed: {result.pages_processed}")
    print(f"Average confidence: {result.metadata['avg_confidence']:.2%}")
else:
    print(f"Error: {result.message}")
```

---

## 7. Offene Fragen

1. ~~Sollen PDF-Annotationen beim PDF-Output erhalten bleiben?~~ → Ja (beantwortet 2025-11-22)
2. ~~Welche Sprachen sollen initial unterstützt werden?~~ → deu, eng, fra, ita, spa (beantwortet 2025-11-22)
3. Soll automatische Spracherkennung implementiert werden? → TBD (zukünftiges Feature)
4. ~~Soll Docker-Container bereitgestellt werden?~~ → Ja, docker-compose.yml vorhanden (beantwortet 2025-11-22)

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ Approved (2025-11-22)
- [x] Architekt: ✅ Approved - Dependency Injection für Tesseract-Engine empfohlen (2025-11-22)
- [x] Python Entwickler: ✅ Approved - pytesseract als Wrapper geeignet (2025-11-22)
- [x] Tester: ✅ Approved - Test-PDFs mit verschiedenen Qualitäten benötigt (2025-11-22)
- [x] DevOps: ✅ Approved - Docker-Integration wichtig für CI/CD (2025-11-22)

### Änderungshistorie
| Datum | Version | Änderung | Von | Auswirkung |
|-------|---------|----------|-----|------------|
| 2025-11-22 | 1.0 | Initiale Erstellung | Requirements Engineer | Neu |

**Versions-Semantik**:
- **MAJOR.x.x**: Breaking Changes, grundlegende Änderung der Anforderung
- **x.MINOR.x**: Neue Anforderungen, backwards compatible
- **x.x.PATCH**: Kleinere Klarstellungen, Korrekturen

---

## 9. Freigabe

**Freigegeben durch**: Team (alle Rollen)
**Datum**: 2025-11-22
**Nächster Schritt**: ✅ Design-Phase → ✅ Implementation → ✅ Released
