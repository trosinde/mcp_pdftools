# Feature Requirement: PDF Text Extraction

**ID**: REQ-005
**Version**: 1.0
**Status**: Released
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-005 v1.0
- Test Report: TEST-005 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Implementierung eines PDF-Text-Extraktions-Features, das es ermöglicht, Text aus PDF-Dateien zu extrahieren. Dies kann als vollständiger Text, seitenweise oder mit Layout-Erhaltung erfolgen.

### 1.2 Geschäftsziel
- **Problem**: Text muss aus PDFs extrahiert werden für Weiterverarbeitung, Analyse, Suche oder Migration
- **Nutzen**:
  - Einfache Textextraktion aus PDFs
  - Verschiedene Extraktionsmodi (vollständig, seitenweise, mit Layout)
  - Automatisierung von Text-Extraktions-Workflows
  - Basis für weitere Verarbeitung (OCR-Fallback, Textanalyse)
  - Unterstützung verschiedener Ausgabeformate (TXT, JSON, Markdown)

### 1.3 Betroffene Module
- [ ] PDF Merge
- [ ] PDF Split
- [x] Text Extraction
- [ ] OCR
- [ ] PDF Protection
- [ ] Thumbnails
- [ ] Invoice Renamer

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität: Text aus PDF extrahieren

**Als** Benutzer
**möchte ich** Text aus einer PDF-Datei extrahieren
**damit** ich den Text weiterverarbeiten kann

**Akzeptanzkriterien:**
1. [ ] Text kann aus PDF extrahiert werden (vollständiger Text)
2. [ ] Text kann seitenweise extrahiert werden (1 Text-Datei pro Seite)
3. [ ] Layout-Erhaltung optional (Positionen, Spalten)
4. [ ] Encoding-Probleme werden behandelt (UTF-8 Output)
5. [ ] Metadaten werden optional mit extrahiert
6. [ ] Funktioniert mit verschiedenen PDF-Typen (digitale PDFs, gescannte PDFs mit Text-Layer)
7. [ ] Speichereffizient (auch bei großen PDFs)

### 2.2 Erweiterte Funktionalität: Extraktionsmodi

**Als** Benutzer
**möchte ich** verschiedene Extraktionsmodi nutzen
**damit** ich die beste Textqualität für meinen Anwendungsfall erhalte

**Akzeptanzkriterien:**
1. [ ] **Modus: SIMPLE** - Einfache Textextraktion (schnell, Standardformat)
2. [ ] **Modus: LAYOUT** - Layout-erhaltende Extraktion (behält Positionen bei)
3. [ ] **Modus: PER_PAGE** - Separate Textdatei pro Seite
4. [ ] **Modus: STRUCTURED** - JSON-Output mit Metadaten (Seite, Position, Schriftart)

### 2.3 Erweiterte Funktionalität: Ausgabeformate

**Als** Benutzer
**möchte ich** verschiedene Ausgabeformate wählen
**damit** ich den Text direkt weiterverarbeiten kann

**Akzeptanzkriterien:**
1. [ ] **Format: TXT** - Plain Text (Standard)
2. [ ] **Format: JSON** - Strukturierte Daten mit Metadaten
3. [ ] **Format: MARKDOWN** - Markdown-formatierter Text (mit Überschriften)

### 2.4 Input

- **Format**: PDF-Datei (einzelne Datei)
- **Parameter**:
  - `--input / -i`: Pfad zur Eingabe-PDF-Datei (erforderlich)
  - `--output / -o`: Ausgabedatei oder -verzeichnis (optional, Standard: stdout)
  - `--mode / -m`: Extraktionsmodus: `simple` (default), `layout`, `per_page`, `structured`
  - `--format / -f`: Ausgabeformat: `txt` (default), `json`, `markdown`
  - `--pages / -p`: Spezifische Seiten extrahieren (z.B. `1,3,5-10`)
  - `--encoding / -e`: Output-Encoding (default: utf-8)
  - `--include-metadata`: Metadaten mit extrahieren
  - `--verbose / -v`: Detaillierte Ausgabe

- **Validierung**:
  - Eingabe-PDF muss existieren
  - Eingabe-PDF muss gültiges PDF-Format haben
  - Ausgabeverzeichnis muss schreibbar sein (wird erstellt falls nicht vorhanden)
  - Seitenangaben müssen gültig sein (1-basiert, innerhalb der PDF-Seitenzahl)
  - Encoding muss gültig sein (utf-8, latin-1, etc.)

### 2.5 Output

- **Format**: Text-Dateien (TXT, JSON, MD)
- **Benennung**:
  - **Modus: simple/layout/structured**: `{prefix}.{format}` (z.B. `document.txt`)
  - **Modus: per_page**: `{prefix}_page_{001}.txt`, `{prefix}_page_{002}.txt`, etc.

- **Fehlerbehandlung**:
  - Bei Fehler: Klare Fehlermeldung mit Grund (z.B. "Keine Textebene gefunden")
  - Warnung bei gescannten PDFs ohne Text-Layer: "No text found, consider using OCR"
  - Exit Code: 0 bei Erfolg, 1 bei Fehler

### 2.6 Verhalten

- **Erfolgsszenario**:
  1. Benutzer führt `pdfgettxt -i document.pdf -o output.txt` aus
  2. Tool prüft Eingabe-PDF (50 Seiten)
  3. Tool extrahiert Text von allen Seiten
  4. Progress-Indikator zeigt Fortschritt: `Extracting text: [====>    ] 25/50 pages`
  5. Erfolgsmeldung: "✓ Text extracted: 12,450 characters written to output.txt"

- **Fehlerszenarios**:
  1. **Ungültige PDF**: "✗ Error: document.pdf is not a valid PDF file"
  2. **Keine Textebene**: "⚠ Warning: No text layer found. PDF may be scanned. Use OCR instead."
  3. **Keine Schreibrechte**: "✗ Error: Cannot write to file output.txt (permission denied)"
  4. **Encoding-Problem**: "⚠ Warning: Some characters could not be encoded, using replacement characters"

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance

- **Verarbeitungszeit**:
  - Kleine PDFs (< 10 Seiten): < 0.5 Sekunden
  - Mittelgroße PDFs (10-100 Seiten): < 3 Sekunden
  - Große PDFs (100-1000 Seiten): < 20 Sekunden

- **Speicherverbrauch**:
  - Peak Memory < 200 MB für PDFs bis 1000 Seiten
  - Streaming-basierter Ansatz für sehr große PDFs

- **Textqualität**:
  - Korrekte UTF-8 Kodierung
  - Erhaltung von Zeilenumbrüchen (bei Layout-Modus)
  - Korrekte Worttrennung

### 3.2 Qualität

- **Testabdeckung**: > 90% (Core-Logik: > 95%)
- **Code-Qualität**:
  - Type Hints für alle Funktionen
  - Docstrings (Google Style) für alle öffentlichen Funktionen
  - SOLID Principles
  - DRY (keine Code-Duplikation)

- **Dokumentation**:
  - API-Dokumentation (Docstrings)
  - CLI-Hilfe (`--help`)
  - Beispiele im README

### 3.3 Kompatibilität

- **Python-Version**: >= 3.8
- **Betriebssysteme**: Windows, Linux, macOS
- **Dependencies**:
  - PyPDF2 oder pypdf (bereits vorhanden)
  - pathlib (Standard Library)
  - argparse (Standard Library)
  - json (Standard Library)

---

## 4. Technische Details

### 4.1 Abhängigkeiten

- **Neue Libraries**: Keine (nutzt bestehende PyPDF2/pypdf Dependency)
- **Externe Tools**: Keine
- **Bestehende Module**:
  - `pdftools.core.validators`: Input-Validierung
  - `pdftools.core.utils`: Datei-Utilities
  - `pdftools.cli.common`: CLI-Utilities (Logging, Error Handling)

### 4.2 Konfiguration

- **Konfigurationsdateien**: Keine (alle Parameter via CLI oder API)
- **Environment Variables**: Keine
- **Defaults**:
  - Output: stdout (wenn keine Ausgabedatei angegeben)
  - Modus: `simple` (einfache Textextraktion)
  - Format: `txt` (Plain Text)
  - Encoding: `utf-8`

### 4.3 CLI-Tool Integration

- **Tool-Name**: `pdfgettxt`
- **Entry Point**: `src/pdftools/text_extraction/cli.py`
- **Setup.py**: Eintrag in `console_scripts`:
  ```python
  "pdfgettxt=pdftools.text_extraction.cli:main"
  ```

---

## 5. Testbarkeit

### 5.1 Unit Tests

- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für PyPDF2 Reader
- [x] Edge Cases:
  - [ ] PDF ohne Textebene (gescannt)
  - [ ] PDF mit verschiedenen Encodings
  - [ ] PDF mit komplexem Layout (Spalten, Tabellen)
  - [ ] Sehr kleine PDF (1 Seite, 10 Zeichen)
  - [ ] Sehr große PDF (1000+ Seiten)
  - [ ] Spezielle Zeichen (Unicode, Emojis)

### 5.2 Integration Tests

- [x] Zusammenspiel mit pdftools.core
- [x] File I/O korrekt (echte Text-Dateien schreiben/lesen)
- [x] Fehlerbehandlung End-to-End
- [x] Output-Validierung (erzeugte Textdateien sind gültig UTF-8)

### 5.3 E2E Tests

- [x] CLI funktioniert wie erwartet (`pdfgettxt --help`, `pdfgettxt -i test.pdf`)
- [x] Reale PDF-Dateien verarbeitet
- [x] Progress-Indikator funktioniert
- [x] Exit Codes korrekt

### 5.4 Test-Daten

Benötigte Test-PDFs:
- [x] Einfaches PDF (1 Seite, nur Text)
- [x] Multi-Page PDF (10 Seiten, Text)
- [x] PDF mit komplexem Layout (Spalten, Tabellen)
- [x] PDF mit Unicode-Zeichen
- [x] Gescanntes PDF ohne Textebene
- [x] Korruptes PDF (für Fehlerhandling)

---

## 6. Beispiele

### 6.1 CLI-Verwendung

```bash
# Beispiel 1: Einfache Textextraktion (stdout)
pdfgettxt -i document.pdf
# Output: Text wird auf stdout ausgegeben

# Beispiel 2: Textextraktion in Datei
pdfgettxt -i document.pdf -o output.txt
# Output: output.txt

# Beispiel 3: Layout-erhaltende Extraktion
pdfgettxt -i document.pdf -m layout -o output.txt
# Output: output.txt (mit Layout)

# Beispiel 4: Seitenweise Extraktion
pdfgettxt -i document.pdf -m per_page -o ./pages/
# Output: ./pages/document_page_001.txt, ./pages/document_page_002.txt, ...

# Beispiel 5: Strukturierte JSON-Ausgabe
pdfgettxt -i document.pdf -f json -o output.json
# Output: output.json (mit Metadaten)

# Beispiel 6: Spezifische Seiten extrahieren
pdfgettxt -i document.pdf -p 1,5,10-15 -o output.txt
# Output: output.txt (nur Seiten 1, 5, 10-15)

# Beispiel 7: Markdown-Ausgabe
pdfgettxt -i document.pdf -f markdown -o output.md
# Output: output.md

# Beispiel 8: Mit Metadaten
pdfgettxt -i document.pdf --include-metadata -f json -o output.json
# Output: output.json (mit PDF-Metadaten)

# Beispiel 9: Verbose Mode
pdfgettxt -i document.pdf -o output.txt -v
# Output mit detailliertem Log
```

### 6.2 Programmatische Verwendung

```python
from pdftools.text_extraction import extract_text, ExtractionMode, OutputFormat, ExtractionConfig

# Beispiel 1: Einfache Textextraktion
text = extract_text(input_path="document.pdf")
print(text)  # String mit komplettem Text

# Beispiel 2: Layout-erhaltende Extraktion
result = extract_text(
    input_path="document.pdf",
    mode=ExtractionMode.LAYOUT
)
print(result.text)

# Beispiel 3: Seitenweise Extraktion
config = ExtractionConfig(
    mode=ExtractionMode.PER_PAGE,
    output_dir="./pages/"
)
result = extract_text(
    input_path="document.pdf",
    config=config
)
print(f"Extracted {result.num_pages} pages")

# Beispiel 4: Strukturierte Extraktion
result = extract_text(
    input_path="document.pdf",
    mode=ExtractionMode.STRUCTURED,
    output_format=OutputFormat.JSON
)
# result.data enthält JSON mit Metadaten

# Beispiel 5: Spezifische Seiten
result = extract_text(
    input_path="document.pdf",
    pages=[1, 5, 10, 15]
)
```

---

## 7. Offene Fragen

1. ~~Soll OCR-Fallback integriert werden, wenn keine Textebene vorhanden ist?~~
   → **Antwort**: Nein, separates Feature (REQ-003). Warnung ausgeben stattdessen.

2. ~~Sollen Tabellen speziell extrahiert werden (z.B. als CSV)?~~
   → **Antwort**: Nice-to-have für v1.1, nicht für v1.0

3. ~~Maximale Textlänge pro Ausgabedatei?~~
   → **Antwort**: Keine Limitierung in v1.0

---

## 8. Review

### Team Review

**Requirements Engineer**: ✅ Vollständig, klar definiert
- Alle Akzeptanzkriterien sind testbar
- Input/Output klar spezifiziert
- Beispiele decken alle Modi ab

**Architekt**: ✅ Approved
- [x] Architektonische Implikationen geprüft: Passt ins bestehende System
- [x] Integration mit bestehendem Core: Nutzt core.validators, core.utils
- [x] Performance-Anforderungen realistisch: Ja, PyPDF2 ist ausreichend performant

**Python Entwickler**: ✅ Approved
- [x] Implementierbarkeit bestätigt: Machbar mit PyPDF2
- [x] Aufwandsschätzung: 1-2 Tage (Core + CLI + Tests)
- [x] Dependencies ausreichend: PyPDF2 bereits vorhanden

**Tester**: ✅ Approved
- [x] Testbarkeit gewährleistet: Dependency Injection vorgesehen
- [x] Test-Daten-Generierung machbar: Test-PDFs können generiert werden
- [x] Edge Cases vollständig: Encoding, kein Text, komplexes Layout abgedeckt

**DevOps**: ✅ Approved
- [x] Keine neuen Setup-Anforderungen: Verwendet bestehende Dependencies
- [x] CLI-Integration klar: Entry Point pdfgettxt definiert

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

**Freigegeben durch**: All 5 Roles (Requirements Engineer, Architekt, Python Developer, Tester, DevOps)
**Datum**: 2025-11-22
**Nächster Schritt**: Design-Phase (DESIGN-005)
