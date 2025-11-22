# Feature Requirement: PDF Merge

**ID**: REQ-001
**Version**: 1.0
**Status**: Approved
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-001 v1.0
- Test Report: TEST-001 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Zusammenführen mehrerer PDF-Dateien zu einem einzelnen PDF-Dokument mit konfigurierbarer Seitenreihenfolge und Output-Optionen.

### 1.2 Geschäftsziel
Benutzer müssen häufig mehrere PDF-Dateien zu einem Dokument kombinieren (z.B. Rechnungen, Berichte, Anhänge). Aktuell müssen sie dafür Online-Tools oder proprietäre Software verwenden. Dieses Feature ermöglicht die lokale, sichere Verarbeitung ohne Upload zu externen Services.

### 1.3 Betroffene Module
- [x] PDF Merge
- [ ] PDF Split
- [ ] Text Extraction
- [ ] OCR
- [ ] PDF Protection
- [ ] Thumbnails
- [ ] Invoice Renamer
- [ ] Neues Modul: N/A

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** Benutzer
**möchte ich** mehrere PDF-Dateien zu einem einzelnen PDF zusammenführen
**damit** ich alle Dokumente in einer Datei habe und einfacher verwalten kann

**Akzeptanzkriterien:**
1. [x] Mindestens 2 PDF-Dateien können zusammengeführt werden
2. [x] Maximale Anzahl: 100 PDF-Dateien in einem Durchlauf
3. [x] Alle Seiten aller Input-PDFs werden in der angegebenen Reihenfolge eingefügt
4. [x] Ausgabe-PDF ist valide und kann mit Standard-PDF-Readern geöffnet werden
5. [x] Lesezeichen (Bookmarks) aus Original-PDFs bleiben erhalten (optional)
6. [x] Metadaten können konfiguriert werden

### 2.2 Input
- **Format**: Liste von PDF-Dateien
- **Parameter**:
  - `-f, --files`: Komma-separierte Liste von PDF-Dateipfaden (Pflicht)
  - `-o, --output`: Ausgabepfad (Optional, Default: `merged.pdf` im Verzeichnis der ersten Datei)
  - `--keep-bookmarks`: Lesezeichen beibehalten (Optional, Default: True)
  - `--add-toc`: Inhaltsverzeichnis generieren (Optional, Default: False)
  - `--verbose`: Detaillierte Ausgaben (Optional)
- **Validierung**:
  - Alle Input-Dateien müssen existieren
  - Alle Input-Dateien müssen valide PDFs sein
  - Mindestens 2 PDF-Dateien erforderlich
  - Output-Pfad muss schreibbar sein

### 2.3 Output
- **Format**: Einzelne PDF-Datei
- **Benennung**:
  - Standard: `merged.pdf` im Verzeichnis der ersten Input-Datei
  - Custom: Vom Benutzer angegebener Pfad
- **Fehlerbehandlung**:
  - Bei ungültigem PDF: Fehler ausgeben, Datei überspringen (mit Warnung) oder Abbruch (konfigurierbar)
  - Bei Schreibfehler: Klare Fehlermeldung mit Grund

### 2.4 Verhalten
- **Erfolgsszenario**:
  1. Benutzer gibt Liste von PDF-Dateien an
  2. System validiert alle Input-Dateien
  3. System führt PDFs in angegebener Reihenfolge zusammen
  4. System speichert Output-PDF
  5. System gibt Erfolgsm eldung mit Pfad zur Output-Datei aus

- **Fehlerszenarios**:
  1. **Input-Datei nicht gefunden**:
     - Fehlermeldung: "PDF file not found: {path}"
     - Exit Code: 1
  2. **Ungültiges PDF**:
     - Fehlermeldung: "PDF file is corrupted: {path}"
     - Verhalten: Überspringen mit Warnung oder Abbruch (konfigurierbar)
  3. **Output nicht schreibbar**:
     - Fehlermeldung: "Cannot write to output path: {path} (Reason: {reason})"
     - Exit Code: 1
  4. **Zu wenige Input-Dateien**:
     - Fehlermeldung: "At least 2 PDF files required for merging"
     - Exit Code: 1

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Verarbeitungszeit: < 5 Sekunden für 10 PDFs mit je 10 Seiten (insgesamt 100 Seiten)
- Speicherverbrauch: < 500 MB auch für große PDFs
- Batch-Verarbeitung: Bis zu 100 PDFs in einem Durchlauf

### 3.2 Qualität
- Testabdeckung: > 90% (Unit Tests)
- Code-Qualität: Pylint Score > 8.0
- Dokumentation: Vollständige Docstrings (Google Style)
- Type Hints: Für alle öffentlichen Funktionen

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme: Windows, Linux, macOS
- Dependencies: PyPDF2 >= 3.0.0

---

## 4. Technische Details

### 4.1 Abhängigkeiten
- **Neue Libraries**: Keine (PyPDF2 bereits vorhanden)
- **Externe Tools**: Keine
- **Bestehende Module**:
  - `pdftools.core.validators` für Input-Validierung
  - `pdftools.core.exceptions` für Fehlerbehandlung
  - `pdftools.core.utils` für Pfad-Normalisierung

### 4.2 Konfiguration
- **Konfigurationsdateien**: Keine erforderlich
- **Environment Variables**:
  - `PDFTOOLS_MERGE_DEFAULT_OUTPUT`: Default Output-Verzeichnis (Optional)
- **Defaults**:
  - Output: `merged.pdf` im Verzeichnis der ersten Input-Datei
  - Keep Bookmarks: True
  - Skip on Error: False (Abbruch bei fehlerhaftem PDF)

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für File I/O
- [x] Edge Cases:
  - 2 PDFs (Minimum)
  - 100 PDFs (Maximum)
  - Leere PDFs
  - Große PDFs (>50 MB)
  - PDFs mit Lesezeichen
  - Verschlüsselte PDFs

### 5.2 Integration Tests
- [x] Zusammenspiel von Validation → Merge → Output
- [x] File I/O korrekt
- [x] Fehlerbehandlung End-to-End

### 5.3 E2E Tests
- [x] CLI funktioniert wie erwartet
- [x] Reale PDF-Dateien verarbeitet
- [x] Performance-Tests mit großen Batches

### 5.4 Test-Daten
Benötigte Test-PDFs:
- [x] Einfaches PDF (1 Seite, nur Text)
- [x] Multi-Page PDF (10 Seiten)
- [x] PDF mit Bildern
- [x] PDF mit Lesezeichen
- [x] Verschlüsseltes PDF
- [x] Korruptes PDF (für Error Handling)
- [x] Großes PDF (>50 MB, 100+ Seiten)

---

## 6. Beispiele

### 6.1 CLI-Verwendung
```bash
# Beispiel 1: Grundlegende Verwendung
pdftools-merge -f "file1.pdf,file2.pdf,file3.pdf" -o "output.pdf"

# Beispiel 2: Ohne Output-Angabe (verwendet Default)
pdftools-merge -f "invoice1.pdf,invoice2.pdf"

# Beispiel 3: Mit Inhaltsverzeichnis
pdftools-merge -f "chapter1.pdf,chapter2.pdf,chapter3.pdf" -o "book.pdf" --add-toc

# Beispiel 4: Verbose-Modus
pdftools-merge -f "doc1.pdf,doc2.pdf" --verbose
```

### 6.2 Programmatische Verwendung
```python
from pdftools.merge import merge_pdfs
from pathlib import Path

# Einfaches Merge
result = merge_pdfs(
    files=[Path("file1.pdf"), Path("file2.pdf")],
    output_path=Path("merged.pdf")
)

# Mit Optionen
result = merge_pdfs(
    files=[Path("file1.pdf"), Path("file2.pdf"), Path("file3.pdf")],
    output_path=Path("output.pdf"),
    keep_bookmarks=True,
    add_toc=True,
    verbose=True
)

# Ergebnis prüfen
if result.status == "success":
    print(f"Merged PDF created: {result.output_path}")
else:
    print(f"Error: {result.message}")
```

---

## 7. Offene Fragen

1. ~~Sollen PDF-Formularfelder erhalten bleiben?~~ → Ja (beantwortet 2025-11-22)
2. ~~Sollen Annotationen/Kommentare erhalten bleiben?~~ → Ja (beantwortet 2025-11-22)
3. Welche Metadaten sollen im Output-PDF gesetzt werden? → TBD

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ Approved (2025-11-22)
- [x] Architekt: ✅ Approved with Comments - Dependency Injection empfohlen, Lesezeichen optional (2025-11-22)
- [x] Python Entwickler: ✅ Approved with Comments - Generator-Pattern vorgeschlagen (2025-11-22)
- [x] Tester: ✅ Approved - Test-PDFs mit Lesezeichen/Formularen benötigt (2025-11-22)
- [x] DevOps: ✅ Approved - Exit Codes dokumentieren (2025-11-22)

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
