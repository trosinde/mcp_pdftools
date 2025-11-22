# Feature Requirement: PDF Protection

**ID**: REQ-004
**Version**: 1.0
**Status**: Released
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-004 v1.0
- Test Report: TEST-004 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Verschlüsselung von PDF-Dateien mit Passwortschutz und konfigurierbaren Berechtigungen für Druck, Kopieren, Bearbeiten und Annotationen.

### 1.2 Geschäftsziel
Benutzer müssen vertrauliche PDF-Dokumente schützen (z.B. Verträge, Rechnungen, persönliche Dokumente). Aktuell müssen sie dafür Online-Tools oder proprietäre Software verwenden. Dieses Feature ermöglicht die lokale, sichere Verschlüsselung ohne Upload zu externen Services.

### 1.3 Betroffene Module
- [ ] PDF Merge
- [ ] PDF Split
- [ ] Text Extraction
- [ ] OCR
- [x] PDF Protection
- [ ] Thumbnails
- [ ] Invoice Renamer
- [ ] Neues Modul: N/A

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** Benutzer
**möchte ich** PDF-Dateien mit Passwort verschlüsseln und Berechtigungen setzen
**damit** ich sensible Dokumente vor unbefugtem Zugriff und Manipulation schützen kann

**Akzeptanzkriterien:**
1. [x] PDF kann mit User-Passwort verschlüsselt werden (zum Öffnen erforderlich)
2. [x] PDF kann mit Owner-Passwort verschlüsselt werden (zum Ändern von Rechten erforderlich)
3. [x] Berechtigungen können einzeln konfiguriert werden: PRINT, COPY, MODIFY, ANNOTATE
4. [x] Ausgabe-PDF ist mit Standard-PDF-Readern kompatibel
5. [x] Bestehende PDF-Inhalte bleiben unverändert (nur Verschlüsselung hinzugefügt)

### 2.2 Input
- **Format**: Einzelne PDF-Datei
- **Parameter**:
  - `-i, --input`: Input-PDF-Dateipfad (Pflicht)
  - `-o, --output`: Ausgabepfad (Optional, Default: `{input}_protected.pdf`)
  - `-u, --user-password`: Passwort zum Öffnen (Optional)
  - `-w, --owner-password`: Passwort zum Ändern von Rechten (Optional)
  - `-p, --permissions`: Komma-separierte Liste: print,copy,modify,annotate (Optional, Default: alle verboten)
  - `--verbose`: Detaillierte Ausgaben (Optional)
- **Validierung**:
  - Input-Datei muss existieren
  - Input-Datei muss valides PDF sein
  - Mindestens ein Passwort muss gesetzt werden
  - Output-Pfad muss schreibbar sein
  - Permissions müssen gültige Werte sein

### 2.3 Output
- **Format**: Verschlüsselte PDF-Datei
- **Benennung**:
  - Standard: `{input}_protected.pdf` im gleichen Verzeichnis
  - Custom: Vom Benutzer angegebener Pfad
- **Fehlerbehandlung**:
  - Bei ungültigem PDF: Fehler ausgeben, Abbruch
  - Bei Schreibfehler: Klare Fehlermeldung mit Grund
  - Bei fehlenden Passwörtern: Fehler ausgeben

### 2.4 Verhalten
- **Erfolgsszenario**:
  1. Benutzer gibt Input-PDF und Passwörter/Berechtigungen an
  2. System validiert Input-Datei
  3. System verschlüsselt PDF mit angegebenen Einstellungen
  4. System speichert verschlüsseltes PDF
  5. System gibt Erfolgsmeldung mit Pfad zur Output-Datei aus

- **Fehlerszenarios**:
  1. **Input-Datei nicht gefunden**:
     - Fehlermeldung: "PDF file not found: {path}"
     - Exit Code: 1
  2. **Ungültiges PDF**:
     - Fehlermeldung: "PDF file is corrupted: {path}"
     - Exit Code: 1
  3. **Keine Passwörter angegeben**:
     - Fehlermeldung: "At least one password (user or owner) must be provided"
     - Exit Code: 1
  4. **Output nicht schreibbar**:
     - Fehlermeldung: "Cannot write to output path: {path} (Reason: {reason})"
     - Exit Code: 1
  5. **Ungültige Berechtigungen**:
     - Fehlermeldung: "Invalid permission: {perm}. Valid: print, copy, modify, annotate"
     - Exit Code: 1

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Verarbeitungszeit: < 2 Sekunden für PDF mit 100 Seiten
- Speicherverbrauch: < 200 MB auch für große PDFs
- Verschlüsselung: 128-bit AES (Standard in PyPDF2)

### 3.2 Qualität
- Testabdeckung: > 90% (Unit Tests)
- Code-Qualität: Pylint Score > 8.0
- Dokumentation: Vollständige Docstrings (Google Style)
- Type Hints: Für alle öffentlichen Funktionen

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme: Windows, Linux, macOS
- Dependencies: PyPDF2 >= 3.0.0

### 3.4 Security
- Passwörter werden nicht geloggt
- Passwörter werden nicht im Klartext gespeichert
- Sichere Verschlüsselung (AES)

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
- **Environment Variables**: Keine
- **Defaults**:
  - Output: `{input}_protected.pdf` im gleichen Verzeichnis
  - Permissions: Alle verboten (höchste Sicherheit)

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Core-Funktionen isoliert testbar (Dependency Injection)
- [x] Mocks für File I/O
- [x] Edge Cases:
  - Nur User-Passwort
  - Nur Owner-Passwort
  - Beide Passwörter
  - Verschiedene Permission-Kombinationen
  - Leeres PDF
  - Großes PDF (>50 MB)

### 5.2 Integration Tests
- [x] Zusammenspiel von Validation → Protection → Output
- [x] File I/O korrekt
- [x] Fehlerbehandlung End-to-End

### 5.3 E2E Tests
- [x] CLI funktioniert wie erwartet
- [x] Geschützte PDFs können mit Passwort geöffnet werden
- [x] Berechtigungen werden korrekt angewendet

### 5.4 Test-Daten
Benötigte Test-PDFs:
- [x] Einfaches PDF (1 Seite, nur Text)
- [x] Multi-Page PDF (10 Seiten)
- [x] PDF mit Bildern
- [x] Großes PDF (>50 MB, 100+ Seiten)

---

## 6. Beispiele

### 6.1 CLI-Verwendung
```bash
# Beispiel 1: Nur User-Passwort (Öffnen geschützt)
pdfprotect -i document.pdf -u "secret123"

# Beispiel 2: User + Owner Passwort
pdfprotect -i contract.pdf -u "open123" -w "admin456"

# Beispiel 3: Mit Berechtigungen (Druck und Kopieren erlaubt)
pdfprotect -i report.pdf -u "read123" -p "print,copy"

# Beispiel 4: Custom Output-Pfad
pdfprotect -i invoice.pdf -o secure_invoice.pdf -u "pass123"

# Beispiel 5: Verbose-Modus
pdfprotect -i document.pdf -u "secret" --verbose
```

### 6.2 Programmatische Verwendung
```python
from pdftools.protection import protect_pdf, PermissionLevel
from pathlib import Path

# Einfacher Schutz
result = protect_pdf(
    input_path=Path("document.pdf"),
    output_path=Path("protected.pdf"),
    user_password="secret123"
)

# Mit allen Optionen
result = protect_pdf(
    input_path=Path("contract.pdf"),
    output_path=Path("secure_contract.pdf"),
    user_password="open123",
    owner_password="admin456",
    permissions=[PermissionLevel.PRINT, PermissionLevel.COPY]
)

# Ergebnis prüfen
if result.success:
    print(f"Protected PDF created: {result.output_path}")
else:
    print(f"Error: {result.message}")
```

---

## 7. Offene Fragen

1. ~~Soll 256-bit AES unterstützt werden?~~ → Nein, 128-bit ausreichend für v1.0 (beantwortet 2025-11-22)
2. ~~Sollen digitale Signaturen unterstützt werden?~~ → Nein, out of scope (beantwortet 2025-11-22)

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ Approved (2025-11-22)
- [x] Architekt: ✅ Approved - Security-Aspekte beachtet (2025-11-22)
- [x] Python Entwickler: ✅ Approved - PyPDF2 encrypt() verwenden (2025-11-22)
- [x] Tester: ✅ Approved - Test mit verschiedenen PDF-Readern (2025-11-22)
- [x] Security: ✅ Approved - Passwörter nicht loggen (2025-11-22)

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
**Nächster Schritt**: ✅ Released
