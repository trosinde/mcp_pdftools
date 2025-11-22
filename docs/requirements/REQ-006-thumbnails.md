# Feature Requirement: PDF Thumbnails

**ID**: REQ-006
**Version**: 1.0
**Status**: Released
**Priority**: Medium
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-006 v1.0
- Test Report: TEST-006 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Generierung von Thumbnail-Bildern (Vorschaubilder) aus PDF-Seiten in verschiedenen Größen und Formaten zur Visualisierung von PDF-Dokumenten.

### 1.2 Geschäftsziel
Benutzer benötigen häufig Vorschaubilder von PDF-Seiten für Webseiten, Kataloge oder Dokumentenverwaltungssysteme. Dieses Feature ermöglicht die automatische Generierung von Thumbnails in konfigurierbaren Größen ohne externe Tools.

### 1.3 Betroffene Module
- [ ] PDF Merge
- [ ] PDF Split
- [ ] Text Extraction
- [ ] OCR
- [ ] PDF Protection
- [x] Thumbnails
- [ ] Invoice Renamer
- [ ] Neues Modul: N/A

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** Benutzer
**möchte ich** Thumbnail-Bilder aus PDF-Seiten generieren
**damit** ich Vorschaubilder für Webseiten oder Kataloge erstellen kann

**Akzeptanzkriterien:**
1. [x] Thumbnails können aus einzelnen oder allen PDF-Seiten generiert werden
2. [x] Verschiedene Größen verfügbar: small (150x150), medium (300x300), large (600x600), custom
3. [x] Formate: PNG, JPG
4. [x] Konfigurierbarer Qualitätsfaktor für JPG (1-100)
5. [x] Ausgabe in konfigurierbares Verzeichnis
6. [x] Automatische Dateibennung: {basename}_page_{n}.{format}

### 2.2 Input
- **Format**: PDF-Datei
- **Parameter**:
  - `-f, --file`: Pfad zur PDF-Datei (Pflicht)
  - `-o, --output-dir`: Ausgabeverzeichnis (Optional, Default: `./thumbnails`)
  - `-s, --size`: Thumbnail-Größe: small|medium|large|WxH (Optional, Default: medium)
  - `-F, --format`: Ausgabeformat: png|jpg (Optional, Default: png)
  - `-p, --pages`: Seiten (z.B. "1,3,5" oder "1-10") (Optional, Default: alle)
  - `-q, --quality`: JPG-Qualität 1-100 (Optional, Default: 85)
  - `--verbose`: Detaillierte Ausgaben
- **Validierung**:
  - Input-Datei muss existieren und valide PDF sein
  - Ausgabeverzeichnis muss schreibbar sein
  - Größenangabe muss valide sein (predefined oder WxH)
  - Format muss png oder jpg sein
  - Qualität muss zwischen 1 und 100 liegen

### 2.3 Output
- **Format**: Bilddateien (PNG oder JPG)
- **Benennung**: `{pdf_basename}_page_{page_number}.{format}`
  - Beispiel: `document_page_001.png`, `report_page_042.jpg`
- **Fehlerbehandlung**:
  - Bei ungültigem PDF: Fehler ausgeben, Abbruch
  - Bei Schreibfehler: Klare Fehlermeldung mit Grund
  - Bei einzelner fehlerhafter Seite: Warnung, fortfahren mit nächster Seite

### 2.4 Verhalten
- **Erfolgsszenario**:
  1. Benutzer gibt PDF-Datei und Optionen an
  2. System validiert Input und Optionen
  3. System generiert Thumbnails für angegebene Seiten
  4. System speichert Thumbnails im Ausgabeverzeichnis
  5. System gibt Erfolgsmeldung mit Anzahl generierter Thumbnails aus

- **Fehlerszenarios**:
  1. **Input-Datei nicht gefunden**:
     - Fehlermeldung: "PDF file not found: {path}"
     - Exit Code: 1
  2. **Ungültiges PDF**:
     - Fehlermeldung: "PDF file is corrupted: {path}"
     - Exit Code: 1
  3. **Ausgabeverzeichnis nicht schreibbar**:
     - Fehlermeldung: "Cannot write to output directory: {path}"
     - Exit Code: 1
  4. **Ungültige Seitenangabe**:
     - Fehlermeldung: "Invalid page specification: {spec}"
     - Exit Code: 1

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Verarbeitungszeit: < 1 Sekunde pro Seite für Standard-Größe (medium)
- Speicherverbrauch: < 200 MB auch für hochauflösende PDFs
- Batch-Verarbeitung: Bis zu 1000 Seiten in einem Durchlauf

### 3.2 Qualität
- Testabdeckung: > 85% (Unit Tests)
- Code-Qualität: Pylint Score > 8.0
- Dokumentation: Vollständige Docstrings (Google Style)
- Type Hints: Für alle öffentlichen Funktionen

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme: Windows, Linux, macOS
- Dependencies: pdf2image, Pillow

---

## 4. Technische Details

### 4.1 Abhängigkeiten
- **Neue Libraries**:
  - `pdf2image`: Konvertierung PDF → Image
  - `Pillow (PIL)`: Image Processing und Resize
- **Externe Tools**:
  - `poppler-utils` (für pdf2image Backend)
- **Bestehende Module**:
  - `pdftools.core.validators` für Input-Validierung
  - `pdftools.core.exceptions` für Fehlerbehandlung

### 4.2 Konfiguration
- **Konfigurationsdateien**: Keine erforderlich
- **Environment Variables**:
  - `PDFTOOLS_THUMBNAILS_DEFAULT_SIZE`: Default Thumbnail-Größe
  - `PDFTOOLS_THUMBNAILS_DEFAULT_FORMAT`: Default Format
- **Defaults**:
  - Size: medium (300x300)
  - Format: png
  - Quality: 85 (für JPG)
  - Output: `./thumbnails`

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für PDF-to-Image Konvertierung
- [x] Edge Cases:
  - Single-Page PDF
  - Multi-Page PDF (100+ Seiten)
  - Verschiedene Größen (small, medium, large, custom)
  - Verschiedene Formate (PNG, JPG)
  - Verschiedene Qualitätsstufen

### 5.2 Integration Tests
- [x] Zusammenspiel von Validation → Generation → Output
- [x] File I/O korrekt
- [x] Fehlerbehandlung End-to-End

### 5.3 E2E Tests
- [x] CLI funktioniert wie erwartet
- [x] Reale PDF-Dateien verarbeitet
- [x] Generierte Thumbnails sind valide Bilder

### 5.4 Test-Daten
Benötigte Test-PDFs:
- [x] Einfaches PDF (1 Seite, nur Text)
- [x] Multi-Page PDF (10+ Seiten)
- [x] PDF mit Bildern/Grafiken
- [x] Hochauflösendes PDF
- [x] Korruptes PDF (für Error Handling)

---

## 6. Beispiele

### 6.1 CLI-Verwendung
```bash
# Beispiel 1: Grundlegende Verwendung (alle Seiten, medium, PNG)
pdfthumbnails -f document.pdf

# Beispiel 2: Spezifische Größe und Format
pdfthumbnails -f report.pdf -s large -F jpg -o ./previews

# Beispiel 3: Nur bestimmte Seiten
pdfthumbnails -f manual.pdf -p "1,5,10-15" -s small

# Beispiel 4: Custom Größe
pdfthumbnails -f catalog.pdf -s 800x600 -F jpg -q 95

# Beispiel 5: Verbose-Modus
pdfthumbnails -f book.pdf --verbose
```

### 6.2 Programmatische Verwendung
```python
from pdftools.thumbnails import generate_thumbnails, ThumbnailSize, ThumbnailFormat
from pathlib import Path

# Einfache Verwendung
result = generate_thumbnails(
    input_path=Path("document.pdf"),
    output_dir=Path("./thumbnails")
)

# Mit spezifischen Optionen
result = generate_thumbnails(
    input_path=Path("report.pdf"),
    output_dir=Path("./previews"),
    size=ThumbnailSize.LARGE,
    format=ThumbnailFormat.JPG,
    pages=[1, 3, 5],
    quality=90,
    verbose=True
)

# Custom Größe
result = generate_thumbnails(
    input_path=Path("catalog.pdf"),
    output_dir=Path("./images"),
    size=(800, 600),
    format=ThumbnailFormat.PNG
)

# Ergebnis prüfen
if result.status == "success":
    print(f"Generated {result.thumbnails_created} thumbnails")
    for thumb in result.thumbnail_paths:
        print(f"  - {thumb}")
else:
    print(f"Error: {result.message}")
```

---

## 7. Offene Fragen

1. Soll Aspect Ratio beibehalten werden oder Crop/Stretch? → Aspect Ratio beibehalten (beantwortet 2025-11-22)
2. Sollen Thumbnails von verschlüsselten PDFs generiert werden können? → Ja, wenn Passwort angegeben (beantwortet 2025-11-22)

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ Approved (2025-11-22)
- [x] Architekt: ✅ Approved - pdf2image + Pillow ist gute Wahl (2025-11-22)
- [x] Python Entwickler: ✅ Approved - Generator-Pattern für große PDFs erwägen (2025-11-22)
- [x] Tester: ✅ Approved - Test-PDFs mit verschiedenen Auflösungen benötigt (2025-11-22)
- [x] DevOps: ✅ Approved - poppler-utils Dependency dokumentieren (2025-11-22)

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
**Nächster Schritt**: ✅ Design-Phase
