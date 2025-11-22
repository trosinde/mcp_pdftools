# Feature Requirement: Invoice Renaming

**ID**: REQ-007
**Version**: 1.0
**Status**: Released
**Priority**: Medium
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-007 v1.0
- Test Report: TEST-007 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Intelligente Umbenennung von Rechnungs-PDFs basierend auf extrahierten Daten (Invoice Number, Date, Vendor) mittels konfigurierbarer Templates.

### 1.2 Geschäftsziel
Benutzer erhalten häufig Rechnungs-PDFs mit kryptischen Dateinamen (z.B. "download.pdf", "invoice_12345.pdf"). Dieses Feature ermöglicht automatische Umbenennung basierend auf Rechnungsdaten zu strukturierten Namen (z.B. "Amazon_INV-2024-001_2024-03-15.pdf"), was die Organisation und Archivierung erheblich vereinfacht.

### 1.3 Betroffene Module
- [ ] PDF Merge
- [ ] PDF Split
- [x] Text Extraction (Dependency)
- [ ] OCR
- [ ] PDF Protection
- [ ] Thumbnails
- [x] Invoice Renamer (Neu)
- [ ] Neues Modul: N/A

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** Benutzer
**möchte ich** Rechnungs-PDFs automatisch umbenennen basierend auf extrahierten Daten
**damit** meine Rechnungen strukturiert benannt und einfach zu finden sind

**Akzeptanzkriterien:**
1. [x] Extrahiere Invoice Number, Date, Vendor/Supplier aus PDF-Text
2. [x] Unterstütze konfigurierbare Naming Templates (z.B. "{vendor}_{invoice_nr}_{date}.pdf")
3. [x] Batch-Processing: Mehrere PDFs auf einmal umbenennen
4. [x] Dry-Run Modus: Zeige was passieren würde, ohne tatsächlich umzubenennen
5. [x] Custom Regex-Patterns für spezielle Rechnungsformate
6. [x] Robuste Fehlerbehandlung bei fehlenden Feldern

### 2.2 Input
- **Format**: Einzelne PDF oder Liste von PDF-Dateien
- **Parameter**:
  - `-f, --files`: PDF-Dateipfad(e) (Pflicht)
  - `-t, --template`: Naming Template (Optional, Default: "{vendor}_{invoice_nr}_{date}.pdf")
  - `-p, --patterns`: Custom Pattern-Datei (JSON) (Optional)
  - `-d, --dry-run`: Simulation ohne tatsächliche Umbenennung (Optional)
  - `-o, --output-dir`: Zielverzeichnis (Optional, Default: Gleiches Verzeichnis)
  - `--verbose`: Detaillierte Ausgaben (Optional)
- **Validierung**:
  - Alle Input-Dateien müssen existieren und valide PDFs sein
  - Template muss gültige Platzhalter enthalten
  - Custom Patterns müssen valide Regex sein

### 2.3 Output
- **Format**: Umbenannte PDF-Datei(en)
- **Benennung**:
  - Basierend auf Template und extrahierten Daten
  - Fallback: Original-Name + "_renamed" wenn Daten fehlen
  - Konflikte: Automatisch nummerierte Suffixe (_1, _2, etc.)
- **Fehlerbehandlung**:
  - Bei fehlenden Daten: Warnung ausgeben, Fallback-Name verwenden
  - Bei ungültiger PDF: Fehler ausgeben, überspringen
  - Bei Schreibfehler: Klare Fehlermeldung

### 2.4 Verhalten
- **Erfolgsszenario**:
  1. Benutzer gibt PDF-Datei(en) und Template an
  2. System extrahiert Text aus PDFs
  3. System wendet Regex-Patterns an, um Rechnungsdaten zu finden
  4. System erstellt neue Dateinamen basierend auf Template
  5. System benennt Dateien um (oder zeigt Dry-Run Preview)
  6. System gibt Erfolgsmeldung mit alten/neuen Namen aus

- **Fehlerszenarios**:
  1. **Invoice-Daten nicht gefunden**:
     - Warnung: "Could not extract {field} from {file}"
     - Verhalten: Fallback-Name verwenden
  2. **Template ungültig**:
     - Fehlermeldung: "Invalid template: Unknown placeholder {placeholder}"
     - Exit Code: 1
  3. **Datei kann nicht umbenannt werden**:
     - Fehlermeldung: "Cannot rename {file}: {reason}"
     - Verhalten: Überspringen, weiter mit nächster Datei

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Verarbeitungszeit: < 3 Sekunden pro PDF (normale Rechnung, 1-5 Seiten)
- Batch-Verarbeitung: Bis zu 100 PDFs in einem Durchlauf
- Speicherverbrauch: < 200 MB

### 3.2 Qualität
- Testabdeckung: > 90% (Unit Tests)
- Code-Qualität: Pylint Score > 8.0
- Dokumentation: Vollständige Docstrings (Google Style)
- Type Hints: Für alle öffentlichen Funktionen

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme: Windows, Linux, macOS
- Dependencies: Nutzt bestehendes `pdftools.text_extraction` Modul

---

## 4. Technische Details

### 4.1 Abhängigkeiten
- **Interne Module**:
  - `pdftools.text_extraction` für PDF-Text-Extraktion
  - `pdftools.core.validators` für Input-Validierung
  - `pdftools.core.exceptions` für Fehlerbehandlung
- **Externe Libraries**:
  - Standard Library: `re`, `datetime`, `pathlib`, `json`

### 4.2 Konfiguration
- **Template-Platzhalter**:
  - `{vendor}`: Lieferant/Aussteller der Rechnung
  - `{invoice_nr}`: Rechnungsnummer
  - `{date}`: Rechnungsdatum (Format: YYYY-MM-DD)
  - `{year}`, `{month}`, `{day}`: Einzelne Datumskomponenten
- **Pattern-Konfiguration**:
  - JSON-Datei mit Custom Regex-Patterns
  - Vordefinierte Patterns für gängige Formate

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Regex-Patterns isoliert testbar
- [x] Template-Rendering testbar
- [x] Extraktoren testbar (mit Mock-Text)
- [x] Edge Cases:
  - Fehlende Felder
  - Ungültige Patterns
  - Mehrere Matches
  - Verschiedene Datumsformate

### 5.2 Integration Tests
- [x] End-to-End: PDF → Text → Extraktion → Template → Umbenennung
- [x] Batch-Processing
- [x] Dry-Run Modus

### 5.3 Test-Daten
- [x] Sample Invoice PDFs mit verschiedenen Formaten
- [x] Custom Pattern JSON-Dateien

---

## 6. Beispiele

### 6.1 CLI-Verwendung
```bash
# Beispiel 1: Einzelne Rechnung mit Default-Template
pdfrename -f "invoice.pdf"

# Beispiel 2: Custom Template
pdfrename -f "rechnung.pdf" -t "{date}_{vendor}_{invoice_nr}.pdf"

# Beispiel 3: Batch mit Dry-Run
pdfrename -f "invoices/*.pdf" -d

# Beispiel 4: Custom Patterns + Output-Verzeichnis
pdfrename -f "*.pdf" -p "patterns.json" -o "renamed_invoices/"

# Beispiel 5: Verbose Modus
pdfrename -f "invoice.pdf" --verbose
```

### 6.2 Programmatische Verwendung
```python
from pdftools.renaming import rename_invoice
from pathlib import Path

# Einfaches Rename
result = rename_invoice(
    input_path=Path("invoice.pdf"),
    template="{vendor}_{invoice_nr}_{date}.pdf"
)

# Mit Custom Patterns
custom_patterns = {
    "invoice_nr": r"Invoice\s*#?\s*(\d{4,})",
    "vendor": r"From:\s*([A-Z][a-zA-Z\s]+)"
}

result = rename_invoice(
    input_path=Path("invoice.pdf"),
    template="{vendor}_{invoice_nr}.pdf",
    custom_patterns=custom_patterns,
    dry_run=True
)

# Ergebnis prüfen
if result.success:
    print(f"Renamed: {result.old_name} -> {result.new_name}")
else:
    print(f"Error: {result.message}")
```

---

## 7. Offene Fragen

1. ~~Welche Standard-Patterns sollen vordefiniert sein?~~ → Amazon, PayPal, eBay, generische Formate (beantwortet 2025-11-22)
2. ~~Soll OCR unterstützt werden für gescannte Rechnungen?~~ → Nein, zunächst nur Text-PDFs (beantwortet 2025-11-22)
3. ~~Sollen Duplikate automatisch erkannt werden?~~ → Ja, via nummerierte Suffixe (beantwortet 2025-11-22)

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ Approved (2025-11-22)
- [x] Architekt: ✅ Approved - Nutzt bestehende text_extraction (2025-11-22)
- [x] Python Entwickler: ✅ Approved - Regex-Patterns erweiterbar (2025-11-22)
- [x] Tester: ✅ Approved - Test-Strategie klar (2025-11-22)

### Änderungshistorie
| Datum | Version | Änderung | Von | Auswirkung |
|-------|---------|----------|-----|------------|
| 2025-11-22 | 1.0 | Initiale Erstellung | Requirements Engineer | Neu |

**Versions-Semantik**:
- **MAJOR.x.x**: Breaking Changes
- **x.MINOR.x**: Neue Features
- **x.x.PATCH**: Bugfixes, Klarstellungen

---

## 9. Freigabe

**Freigegeben durch**: Team (alle Rollen)
**Datum**: 2025-11-22
**Status**: Released
**Nächster Schritt**: ✅ Design-Phase
