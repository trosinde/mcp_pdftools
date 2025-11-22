# Feature Requirement: PDF Split

**ID**: REQ-002
**Version**: 1.0
**Status**: Approved
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-002 v1.0
- Test Report: TEST-002 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Implementierung eines PDF-Split-Features, das es ermöglicht, eine PDF-Datei in mehrere kleinere PDF-Dateien aufzuteilen. Dies kann nach einzelnen Seiten, Seitenbereichen oder benutzerdefinierten Kriterien erfolgen.

### 1.2 Geschäftsziel
- **Problem**: Große PDF-Dateien müssen oft in kleinere Teile aufgeteilt werden (z.B. für E-Mail-Versand, einzelne Kapitel extrahieren, Archivierung)
- **Nutzen**:
  - Einfache Aufteilung großer PDF-Dokumente
  - Extraktion spezifischer Seiten oder Seitenbereiche
  - Automatisierung von Splitting-Workflows
  - Reduzierung von Dateigrößen für Übertragung
  - Flexible Aufteilungsstrategien (Seiten, Bereiche, Anzahl)

### 1.3 Betroffene Module
- [ ] PDF Merge
- [x] PDF Split
- [ ] Text Extraction
- [ ] OCR
- [ ] PDF Protection
- [ ] Thumbnails
- [ ] Invoice Renamer

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität: PDF nach Seiten aufteilen

**Als** Benutzer
**möchte ich** eine PDF-Datei in einzelne Seiten aufteilen
**damit** ich jede Seite als separate PDF-Datei erhalte

**Akzeptanzkriterien:**
1. [ ] Eingabe-PDF kann in einzelne Seiten aufgeteilt werden (1 Seite pro Datei)
2. [ ] Jede Ausgabe-Datei enthält genau eine Seite
3. [ ] Original-Seitenqualität bleibt erhalten (keine Kompression)
4. [ ] Metadaten werden übernommen (sofern möglich)
5. [ ] Dateinamen folgen einem logischen Schema: `{original}_page_{001}.pdf`
6. [ ] Funktioniert mit PDFs von 1 bis 1000+ Seiten
7. [ ] Speichereffizient (auch bei großen PDFs)

### 2.2 Erweiterte Funktionalität: Split nach Bereichen

**Als** Benutzer
**möchte ich** eine PDF-Datei in spezifische Seitenbereiche aufteilen
**damit** ich nur die benötigten Abschnitte extrahiere

**Akzeptanzkriterien:**
1. [ ] Bereiche können als `1-5,10-15,20-25` angegeben werden
2. [ ] Jeder Bereich wird als separate PDF-Datei gespeichert
3. [ ] Überlappende Bereiche sind erlaubt (z.B. `1-5,3-7`)
4. [ ] Ungültige Bereiche (z.B. Seite 999 bei 10-seitigem PDF) werden erkannt und gemeldet

### 2.3 Erweiterte Funktionalität: Split nach Anzahl

**Als** Benutzer
**möchte ich** eine PDF-Datei in N gleich große Teile aufteilen
**damit** ich mehrere gleichmäßig verteilte Dateien erhalte

**Akzeptanzkriterien:**
1. [ ] Anzahl der gewünschten Ausgabe-Dateien kann angegeben werden (z.B. `--parts 5`)
2. [ ] Seiten werden gleichmäßig verteilt (z.B. 100 Seiten → 5 Dateien mit je 20 Seiten)
3. [ ] Bei nicht gleich teilbarer Anzahl: Restseiten werden auf erste Dateien verteilt

### 2.4 Input

- **Format**: PDF-Datei (einzelne Datei)
- **Parameter**:
  - `--input / -i`: Pfad zur Eingabe-PDF-Datei (erforderlich)
  - `--output-dir / -o`: Ausgabeverzeichnis (optional, Standard: aktuelles Verzeichnis)
  - `--mode / -m`: Split-Modus: `pages` (default), `ranges`, `parts`
  - `--ranges / -r`: Seitenbereiche (nur bei mode=ranges), z.B. `1-5,10-15`
  - `--parts / -p`: Anzahl der Teile (nur bei mode=parts), z.B. `5`
  - `--pages`: Spezifische Seiten (komma-separiert), z.B. `1,3,5,7`
  - `--prefix`: Präfix für Ausgabe-Dateien (optional, Standard: Original-Dateiname)
  - `--verbose / -v`: Detaillierte Ausgabe

- **Validierung**:
  - Eingabe-PDF muss existieren
  - Eingabe-PDF muss gültiges PDF-Format haben
  - Ausgabeverzeichnis muss schreibbar sein (wird erstellt falls nicht vorhanden)
  - Seitenbereiche müssen gültig sein (1-basiert, innerhalb der PDF-Seitenzahl)
  - `--parts` muss positive Ganzzahl sein
  - Modi schließen sich gegenseitig aus

### 2.5 Output

- **Format**: Mehrere PDF-Dateien
- **Benennung**:
  - **Mode: pages**: `{prefix}_page_{001}.pdf`, `{prefix}_page_{002}.pdf`, etc.
  - **Mode: ranges**: `{prefix}_pages_{001-005}.pdf`, `{prefix}_pages_{010-015}.pdf`, etc.
  - **Mode: parts**: `{prefix}_part_{1}.pdf`, `{prefix}_part_{2}.pdf`, etc.
  - **Specific pages**: `{prefix}_page_{001}.pdf`, `{prefix}_page_{003}.pdf`, etc.

- **Fehlerbehandlung**:
  - Bei Fehler: Klare Fehlermeldung mit Grund (z.B. "Seite 100 existiert nicht")
  - Bereits erstellte Dateien bleiben erhalten (kein Rollback)
  - Exit Code: 0 bei Erfolg, 1 bei Fehler

### 2.6 Verhalten

- **Erfolgsszenario**:
  1. Benutzer führt `pdfsplit -i document.pdf -m pages` aus
  2. Tool prüft Eingabe-PDF (100 Seiten)
  3. Tool erstellt 100 separate PDF-Dateien
  4. Progress-Indikator zeigt Fortschritt: `Splitting: [====>    ] 45/100`
  5. Erfolgsmeldung: "✓ Split completed: 100 pages extracted to ./output/"

- **Fehlerszenarios**:
  1. **Ungültige PDF**: "✗ Error: document.pdf is not a valid PDF file"
  2. **Seite nicht vorhanden**: "✗ Error: Page 150 does not exist (PDF has 100 pages)"
  3. **Keine Schreibrechte**: "✗ Error: Cannot write to directory ./output/ (permission denied)"
  4. **Korruptes PDF**: "✗ Error: PDF is corrupted and cannot be processed"

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance

- **Verarbeitungszeit**:
  - Kleine PDFs (< 10 Seiten): < 1 Sekunde
  - Mittelgroße PDFs (10-100 Seiten): < 5 Sekunden
  - Große PDFs (100-1000 Seiten): < 30 Sekunden
  - Sehr große PDFs (> 1000 Seiten): < 2 Minuten

- **Speicherverbrauch**:
  - Peak Memory < 500 MB für PDFs bis 1000 Seiten
  - Streaming-basierter Ansatz für sehr große PDFs (keine vollständige Ladung in RAM)

- **Batch-Verarbeitung**:
  - Soll später erweiterbar sein für Verzeichnisse mit mehreren PDFs

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
  - PyPDF2 oder pypdf (bereits vorhanden für merge)
  - pathlib (Standard Library)
  - argparse (Standard Library)

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
  - Output-Verzeichnis: Aktuelles Verzeichnis
  - Mode: `pages` (Split in einzelne Seiten)
  - Prefix: Original-Dateiname (ohne Extension)

### 4.3 CLI-Tool Integration

- **Tool-Name**: `pdfsplit`
- **Entry Point**: `src/pdftools/split/cli.py`
- **Setup.py**: Eintrag in `console_scripts`:
  ```python
  "pdfsplit=pdftools.split.cli:main"
  ```

---

## 5. Testbarkeit

### 5.1 Unit Tests

- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für PyPDF2 Reader/Writer
- [x] Edge Cases:
  - [ ] 1-seitige PDF
  - [ ] 1000+ seitige PDF
  - [ ] Leere Seitenbereiche
  - [ ] Ungültige Seitenzahlen
  - [ ] Überlappende Bereiche

### 5.2 Integration Tests

- [x] Zusammenspiel mit pdftools.core
- [x] File I/O korrekt (echte PDFs schreiben/lesen)
- [x] Fehlerbehandlung End-to-End
- [x] Output-Validierung (erzeugte PDFs sind gültig)

### 5.3 E2E Tests

- [x] CLI funktioniert wie erwartet (`pdfsplit --help`, `pdfsplit -i test.pdf`)
- [x] Reale PDF-Dateien verarbeitet
- [x] Progress-Indikator funktioniert
- [x] Exit Codes korrekt

### 5.4 Test-Daten

Benötigte Test-PDFs:
- [x] Einfaches PDF (1 Seite, nur Text)
- [x] Multi-Page PDF (10 Seiten, Text)
- [x] Großes PDF (100+ Seiten)
- [x] PDF mit Bildern (komplexes Layout)
- [x] Geschütztes PDF (Read-Only)
- [x] Korruptes PDF (für Fehlerhandling)

---

## 6. Beispiele

### 6.1 CLI-Verwendung

```bash
# Beispiel 1: Split in einzelne Seiten (Standard-Modus)
pdfsplit -i document.pdf
# Output: document_page_001.pdf, document_page_002.pdf, ...

# Beispiel 2: Split in einzelne Seiten mit Ausgabeverzeichnis
pdfsplit -i document.pdf -o ./output/
# Output: ./output/document_page_001.pdf, ...

# Beispiel 3: Split nach Seitenbereichen
pdfsplit -i document.pdf -m ranges -r "1-5,10-15,20-25"
# Output: document_pages_001-005.pdf, document_pages_010-015.pdf, document_pages_020-025.pdf

# Beispiel 4: Split in 5 gleich große Teile
pdfsplit -i document.pdf -m parts -p 5
# Output: document_part_1.pdf (20 Seiten), document_part_2.pdf (20 Seiten), ...

# Beispiel 5: Spezifische Seiten extrahieren
pdfsplit -i document.pdf --pages 1,5,10,15
# Output: document_page_001.pdf, document_page_005.pdf, document_page_010.pdf, document_page_015.pdf

# Beispiel 6: Mit custom Präfix
pdfsplit -i document.pdf --prefix chapter
# Output: chapter_page_001.pdf, chapter_page_002.pdf, ...

# Beispiel 7: Verbose Mode
pdfsplit -i document.pdf -v
# Output mit detailliertem Log
```

### 6.2 Programmatische Verwendung

```python
from pdftools.split import split_pdf, SplitMode, SplitConfig

# Beispiel 1: Split in einzelne Seiten
result = split_pdf(
    input_path="document.pdf",
    output_dir="./output/",
    mode=SplitMode.PAGES
)
print(f"Created {result.num_files} files")

# Beispiel 2: Split nach Bereichen
config = SplitConfig(
    mode=SplitMode.RANGES,
    ranges=[(1, 5), (10, 15), (20, 25)]
)
result = split_pdf(
    input_path="document.pdf",
    config=config
)

# Beispiel 3: Split in N Teile
result = split_pdf(
    input_path="document.pdf",
    mode=SplitMode.PARTS,
    num_parts=5
)

# Beispiel 4: Spezifische Seiten
result = split_pdf(
    input_path="document.pdf",
    pages=[1, 5, 10, 15]
)
```

---

## 7. Offene Fragen

1. ~~Soll das Tool auch verschlüsselte/geschützte PDFs verarbeiten können?~~
   → **Antwort**: Ja, falls möglich (Read-Only PDFs); mit Fehlermeldung bei passwortgeschützten PDFs

2. ~~Sollen Lesezeichen/Bookmarks in den Split-PDFs erhalten bleiben?~~
   → **Antwort**: Nice-to-have für v1.1, nicht für v1.0

3. ~~Maximale Dateigröße pro Split-Datei konfigurierbar?~~
   → **Antwort**: Nicht in v1.0, potentiell in v2.0 (Mode: `filesize`)

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
- [x] Aufwandsschätzung: 2-3 Tage (Core + CLI + Tests)
- [x] Dependencies ausreichend: PyPDF2 bereits vorhanden

**Tester**: ✅ Approved
- [x] Testbarkeit gewährleistet: Dependency Injection vorgesehen
- [x] Test-Daten-Generierung machbar: Test-PDFs können generiert werden
- [x] Edge Cases vollständig: 1-seitige PDF, große PDFs, ungültige Bereiche abgedeckt

**DevOps**: ✅ Approved
- [x] Keine neuen Setup-Anforderungen: Verwendet bestehende Dependencies
- [x] CLI-Integration klar: Entry Point pdfsplit definiert

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
**Nächster Schritt**: Design-Phase (DESIGN-002)
