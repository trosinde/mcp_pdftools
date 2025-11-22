# Feature Requirement: Command-Line Interface (CLI) Tools

**ID**: REQ-009
**Version**: 1.0
**Status**: Released
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-009 v1.0
- Test Report: TEST-009 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Benutzerfreundliche Kommandozeilen-Tools für alle PDFTools-Features, die ohne Programmierung direkt aus der Shell verwendet werden können. Jedes Feature erhält ein eigenes CLI-Tool mit harmonisierten Namen basierend auf den ursprünglichen Legacy-Tools.

### 1.2 Geschäftsziel
- **Problem**: Benutzer möchten PDF-Operationen direkt aus der Kommandozeile ausführen ohne Python-Code schreiben zu müssen
- **Nutzen**:
  - Einfache Verwendung für Nicht-Programmierer
  - Integration in Shell-Scripts und Automation
  - Schneller Zugriff auf alle Features
  - Konsistente CLI-Erfahrung über alle Tools

### 1.3 Betroffene Module
- [x] PDF Merge
- [x] PDF Split
- [x] Text Extraction
- [x] OCR
- [x] PDF Protection
- [x] Thumbnails
- [x] Invoice Renamer

---

## 2. Funktionale Anforderungen

### 2.1 CLI-Tools (7 Tools - 1 pro Feature)

#### 2.1.1 pdfmerge - PDF Zusammenführen

**Als** Benutzer
**möchte ich** mehrere PDFs über die Kommandozeile zusammenführen
**damit** ich schnell PDFs kombinieren kann ohne zu programmieren

**Akzeptanzkriterien:**
1. [ ] Tool `pdfmerge` ist nach Installation verfügbar
2. [ ] Mindestens 2 PDF-Dateien können zusammengeführt werden
3. [ ] Output-Pfad ist wählbar (`-o` / `--output`)
4. [ ] Fehlerhafte PDFs können optional übersprungen werden (`--skip-on-error`)
5. [ ] Verbose-Modus verfügbar (`--verbose`)
6. [ ] Help-Text zeigt alle Optionen (`--help`)
7. [ ] Exit Code 0 bei Erfolg, != 0 bei Fehler

**Verwendung**:
```bash
pdfmerge file1.pdf file2.pdf file3.pdf -o merged.pdf
pdfmerge *.pdf -o all_merged.pdf --skip-on-error
```

#### 2.1.2 pdfsplit - PDF Aufteilen

**Als** Benutzer
**möchte ich** ein PDF in einzelne Seiten aufteilen
**damit** ich spezifische Seiten extrahieren kann

**Akzeptanzkriterien:**
1. [ ] Tool `pdfsplit` ist nach Installation verfügbar
2. [ ] PDF wird in einzelne Seiten aufgeteilt
3. [ ] Output-Verzeichnis ist wählbar (`-o` / `--output-dir`)
4. [ ] Seiten-Bereich wählbar (`--pages 1-10` oder `--pages 1,3,5`)
5. [ ] Datei-Namensschema konfigurierbar (`--pattern "page_{n}.pdf"`)

**Verwendung**:
```bash
pdfsplit document.pdf -o output_dir/
pdfsplit document.pdf --pages 1-5 -o first_pages/
pdfsplit document.pdf --pages 1,3,5 --pattern "page_{n}.pdf"
```

#### 2.1.3 pdfgettxt - Text Extraktion

**Als** Benutzer
**möchte ich** Text aus PDFs extrahieren
**damit** ich den Inhalt weiterverarbeiten kann

**Akzeptanzkriterien:**
1. [ ] Tool `pdfgettxt` ist nach Installation verfügbar
2. [ ] Text wird aus PDF extrahiert
3. [ ] Output als Text-Datei oder STDOUT (`-o output.txt` oder keine `-o` Flag)
4. [ ] Seiten-Bereich wählbar (`--pages 1-10`)
5. [ ] Encoding wählbar (`--encoding utf-8`)

**Verwendung**:
```bash
pdfgettxt document.pdf -o extracted.txt
pdfgettxt document.pdf --pages 1-5
pdfgettxt document.pdf  # Output to STDOUT
```

#### 2.1.4 ocrutil - OCR Processing

**Als** Benutzer
**möchte ich** OCR zu gescannten PDFs hinzufügen
**damit** der Text durchsuchbar wird

**Akzeptanzkriterien:**
1. [ ] Tool `ocrutil` ist nach Installation verfügbar
2. [ ] Docker-basierte OCR mit ocrmypdf
3. [ ] Sprache wählbar (`-l deu` / `--language deu`)
4. [ ] Output-Pfad wählbar (`-o`)
5. [ ] Fehler bei fehlendem Docker klar kommuniziert
6. [ ] Force-Modus für bereits OCR-PDFs (`--force`)

**Verwendung**:
```bash
ocrutil scanned.pdf -o ocr_output.pdf -l deu
ocrutil scanned.pdf -o output.pdf -l eng --force
```

#### 2.1.5 pdfprotect - PDF Verschlüsseln

**Als** Benutzer
**möchte ich** PDFs mit Passwort schützen
**damit** nur autorisierte Personen darauf zugreifen können

**Akzeptanzkriterien:**
1. [ ] Tool `pdfprotect` ist nach Installation verfügbar
2. [ ] User-Passwort setzbar (`--user-password`)
3. [ ] Owner-Passwort setzbar (`--owner-password`)
4. [ ] Permissions konfigurierbar (`--allow-printing`, `--allow-modification`)
5. [ ] Output-Pfad wählbar (`-o`)

**Verwendung**:
```bash
pdfprotect document.pdf -o protected.pdf --user-password secret123
pdfprotect doc.pdf -o protected.pdf --user-password user123 --owner-password owner456 --allow-printing
```

#### 2.1.6 pdfthumbnails - Thumbnail Generierung

**Als** Benutzer
**möchte ich** Thumbnails von PDF-Seiten generieren
**damit** ich Vorschaubilder erstellen kann

**Akzeptanzkriterien:**
1. [ ] Tool `pdfthumbnails` ist nach Installation verfügbar
2. [ ] Thumbnails als PNG/JPG generiert
3. [ ] Output-Verzeichnis wählbar (`-o`)
4. [ ] Größe konfigurierbar (`--size 200x200`)
5. [ ] Seiten-Auswahl möglich (`--pages 1,5,10` oder `--first-page-only`)
6. [ ] Format wählbar (`--format png` / `--format jpg`)

**Verwendung**:
```bash
pdfthumbnails document.pdf -o thumbnails/ --size 200x200
pdfthumbnails document.pdf -o thumbs/ --first-page-only --format jpg
```

#### 2.1.7 pdfrename - Invoice Renaming

**Als** Benutzer
**möchte ich** Rechnungs-PDFs automatisch umbenennen
**damit** sie nach Datum/Lieferant organisiert sind

**Akzeptanzkriterien:**
1. [ ] Tool `pdfrename` ist nach Installation verfügbar
2. [ ] Text-Muster aus Konfiguration (`renamepdf.json`)
3. [ ] Automatische Erkennung von Datum und Lieferant
4. [ ] Dry-Run-Modus (`--dry-run`)
5. [ ] Namensschema konfigurierbar
6. [ ] Batch-Verarbeitung möglich

**Verwendung**:
```bash
pdfrename invoice.pdf --dry-run
pdfrename *.pdf --config renamepdf.json
```

---

### 2.2 Gemeinsame CLI-Features

Alle Tools teilen diese gemeinsamen Features:

**Standard-Parameter**:
- `-h`, `--help`: Help-Text anzeigen
- `-v`, `--verbose`: Detaillierte Ausgabe
- `--version`: Tool-Version anzeigen

**Fehlerbehandlung**:
- Exit Code 0: Erfolg
- Exit Code 1: Allgemeiner Fehler (File not found, etc.)
- Exit Code 2: Validierungsfehler (ungültige Parameter)
- Exit Code 3: Verarbeitungsfehler (PDF corrupted, etc.)

**Output-Format**:
- Klare Fortschrittsmeldungen: "Processing file1.pdf..."
- Erfolg: "✓ Successfully processed file.pdf"
- Fehler: "✗ Error: [clear error message]"
- Warnungen: "⚠ Warning: [warning message]"

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- CLI-Start: < 1 Sekunde
- Verarbeitung: Abhängig vom Feature (siehe jeweilige REQ-001 bis REQ-007)
- Kein unnötiges Laden von Dependencies

### 3.2 Qualität
- Help-Text vollständig und klar
- Error Messages benutzerfreundlich (keine Python Tracebacks!)
- Testabdeckung: > 80% für CLI-Code
- Type Hints in allen CLI-Modulen

### 3.3 Kompatibilität
- Python >= 3.8
- Windows (cmd.exe, PowerShell)
- Linux (bash, zsh)
- macOS (bash, zsh)

### 3.4 Usability
- Konsistente Argument-Namen über alle Tools
- Intuitive Defaults (z.B. output.pdf wenn `-o` fehlt)
- Farbige Ausgabe optional (`--no-color` für Scripts)
- Progress-Bars für lange Operationen (optional)

---

## 4. Technische Details

### 4.1 Abhängigkeiten

**Interne Dependencies**:
- `pdftools.merge` (für pdfmerge)
- `pdftools.split` (für pdfsplit)
- `pdftools.text_extraction` (für pdfgettxt)
- `pdftools.ocr` (für ocrutil)
- `pdftools.protection` (für pdfprotect)
- `pdftools.thumbnails` (für pdfthumbnails)
- `pdftools.renaming` (für pdfrename)

**Externe Dependencies**:
- `argparse`: Argument Parsing (Python stdlib)
- `colorama` (optional): Farbige Terminal-Ausgabe
- `tqdm` (optional): Progress Bars

### 4.2 Installation & Entry Points

**Setup über pyproject.toml / setup.py**:
```toml
[project.scripts]
pdfmerge = "pdftools.merge.cli:main"
pdfsplit = "pdftools.split.cli:main"
pdfgettxt = "pdftools.text_extraction.cli:main"
ocrutil = "pdftools.ocr.cli:main"
pdfprotect = "pdftools.protection.cli:main"
pdfthumbnails = "pdftools.thumbnails.cli:main"
pdfrename = "pdftools.renaming.cli:main"
```

Nach Installation mit `pip install -e .` sind alle Tools verfügbar:
```bash
$ which pdfmerge
/path/to/.venv/bin/pdfmerge
```

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [ ] CLI-Argument-Parsing isoliert testbar
- [ ] Mocks für Core-Funktionen (merge_pdfs, etc.)
- [ ] Error Handling für alle Exit Codes
- [ ] Help-Text vollständig

### 5.2 Integration Tests
- [ ] CLI ruft Core-Funktionen korrekt auf
- [ ] File I/O funktioniert
- [ ] Error Handling End-to-End

### 5.3 E2E Tests
- [ ] CLI als Subprocess ausführen
- [ ] Exit Codes korrekt
- [ ] Output korrekt
- [ ] Alle Beispiele aus Dokumentation funktionieren

### 5.4 Test-Daten
Verwende Test-PDFs aus `tests/test_data/`:
- test_simple.pdf
- test_multipage.pdf
- test_with_images.pdf
- test_no_ocr.pdf
- test_encrypted.pdf
- test_corrupted.pdf

---

## 6. Beispiele

### 6.1 pdfmerge
```bash
# Einfaches Mergen
pdfmerge file1.pdf file2.pdf -o merged.pdf

# Alle PDFs im Verzeichnis
pdfmerge *.pdf -o all.pdf

# Mit Fehlertoleranz
pdfmerge *.pdf -o output.pdf --skip-on-error --verbose
```

### 6.2 pdfsplit
```bash
# Alle Seiten splitten
pdfsplit document.pdf -o pages/

# Nur bestimmte Seiten
pdfsplit doc.pdf --pages 1-10 -o first_10/

# Einzelne Seiten
pdfsplit doc.pdf --pages 1,5,10 -o selected/
```

### 6.3 pdfgettxt
```bash
# In Datei schreiben
pdfgettxt document.pdf -o text.txt

# Zu STDOUT (für Pipes)
pdfgettxt document.pdf | grep "Important"

# Nur bestimmte Seiten
pdfgettxt doc.pdf --pages 1-5 -o first_pages.txt
```

### 6.4 ocrutil
```bash
# Deutsch OCR
ocrutil scanned.pdf -o ocr.pdf -l deu

# Englisch OCR mit force
ocrutil scan.pdf -o output.pdf -l eng --force
```

### 6.5 pdfprotect
```bash
# User-Passwort
pdfprotect doc.pdf -o protected.pdf --user-password secret

# Mit Permissions
pdfprotect doc.pdf -o prot.pdf --user-password user --owner-password owner --allow-printing
```

### 6.6 pdfthumbnails
```bash
# Thumbnails generieren
pdfthumbnails document.pdf -o thumbs/ --size 200x200

# Nur erste Seite als JPG
pdfthumbnails doc.pdf -o thumb/ --first-page-only --format jpg
```

### 6.7 pdfrename
```bash
# Dry-Run (zeigt nur was passieren würde)
pdfrename invoice_*.pdf --dry-run

# Tatsächlich umbenennen
pdfrename invoice_*.pdf --config renamepdf.json
```

---

## 7. Offene Fragen

1. Sollen alle Tools auch als `python -m pdftools.merge.cli` aufrufbar sein? (Ja, als Fallback)
2. Farbige Ausgabe per Default oder opt-in? (Default ON, opt-out mit `--no-color`)
3. Progress Bars für alle Tools oder nur für lange Operationen? (Nur für lange Ops)
4. Ein zentrales `pdftools` Command mit Subcommands zusätzlich? (Future Enhancement, aktuell 7 separate Tools)

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ APPROVED - Vollständig und klar
- [x] Architekt: ✅ APPROVED - Gemeinsame CLI-Utilities empfohlen
- [x] Python Entwickler: ✅ APPROVED - pdfmerge sofort, Rest als Stubs
- [x] Tester: ✅ APPROVED - E2E Tests via Subprocess
- [x] DevOps: ✅ APPROVED - Entry Points Setup klar

### Änderungshistorie
| Datum | Version | Änderung | Von | Auswirkung |
|-------|---------|----------|-----|------------|
| 2025-11-22 | 1.0 | Initiale Erstellung | Requirements Engineer | Neu |

**Versions-Semantik**:
- **MAJOR.x.x**: Breaking Changes (z.B. CLI-Argumente ändern)
- **x.MINOR.x**: Neue CLI-Features, backwards compatible
- **x.x.PATCH**: Bug-Fixes, Help-Text-Verbesserungen

---

## 9. Freigabe

**Freigegeben durch**: [Pending Team Review]
**Datum**: [TBD]
**Nächster Schritt**: Team Review → Design-Phase
