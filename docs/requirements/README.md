# Requirements Documentation

## Naming Convention

Requirements folgen diesem Namensschema:

```
REQ-<NUMBER>-<short-name>.md
```

**Beispiele:**
- `REQ-001-pdf-merge.md`
- `REQ-002-ocr-processing.md`
- `REQ-003-thumbnail-generation.md`

## Versionierung

Jedes Requirement-Dokument enthält intern eine Versionsnummer:
- **Version**: Versionsnummer im Format `MAJOR.MINOR.PATCH`
- **Change History**: Tabelle mit allen Änderungen

**Version Semantik:**
- **MAJOR**: Breaking Changes, grundlegende Änderung der Anforderung
- **MINOR**: Neue Anforderungen hinzugefügt, backwards compatible
- **PATCH**: Kleinere Klarstellungen, Korrekturen

## Lifecycle Status

Jedes Requirement hat einen Status:
- **Draft**: In Erstellung
- **Under Review**: Wird vom Team geprüft
- **Approved**: Vom Team freigegeben
- **In Development**: Wird gerade implementiert
- **Implemented**: Implementierung abgeschlossen
- **Tested**: Tests erfolgreich durchgeführt
- **Released**: In Production
- **Deprecated**: Veraltet, wird nicht mehr unterstützt

## Traceability

Jedes Dokument referenziert andere:

```
Requirement (REQ-XXX v1.0)
    ↓
Design Document (DESIGN-XXX v1.0)
    ↓
Implementation (Code)
    ↓
Test Report (TEST-XXX v1.0)
```

## Index

| ID | Name | Version | Status | Beschreibung |
|----|------|---------|--------|--------------|
| REQ-001 | PDF Merge | 1.0 | Released | Zusammenführen mehrerer PDFs |
| REQ-002 | PDF Split | 1.0 | Released | PDF in einzelne Seiten/Bereiche aufteilen (4 Modi) |
| REQ-003 | OCR Processing | 1.0 | Draft | OCR-Verarbeitung von PDFs |
| REQ-004 | PDF Protection | 1.0 | Draft | PDF-Verschlüsselung |
| REQ-005 | Text Extraction | 1.0 | Released | Textextraktion aus PDFs (4 Modi, 3 Formate) |
| REQ-006 | Thumbnail Generation | 1.0 | Draft | Thumbnail-Generierung |
| REQ-007 | Invoice Renaming | 1.0 | Draft | Intelligente PDF-Umbenennung |
| REQ-008 | Installation & De-Installation | 1.0 | Released | Automatisierte Installation mit Docker-Setup für OCR |
| REQ-009 | CLI Tools | 1.0 | Released | 7 Kommandozeilen-Tools für alle Features |
