# Traceability Matrix

Diese Matrix zeigt die Verbindung zwischen Requirements, Design, Implementation und Tests.

## Format

```
REQ → DESIGN → CODE → TESTS → REPORT
```

## Matrix

| Requirement | Design | Module | Tests | Test Report | Status |
|-------------|--------|--------|-------|-------------|--------|
| [REQ-001](requirements/REQ-001-pdf-merge.md) v1.0 | [DESIGN-001](design/DESIGN-001-pdf-merge.md) v1.0 | `src/pdftools/merge/` | `tests/unit/test_merge_*.py` | [TEST-001](test_reports/TEST-001-pdf-merge.md) v1.0 | ✅ Released |
| [REQ-002](requirements/REQ-002-pdf-split.md) v1.0 | [DESIGN-002](design/DESIGN-002-pdf-split.md) v1.0 | `src/pdftools/split/` | `tests/unit/test_split_*.py` | [TEST-002](test_reports/TEST-002-pdf-split.md) v1.0 | ✅ Released |
| [REQ-003](requirements/REQ-003-ocr.md) v1.0 | DESIGN-003 v1.0 | `src/pdftools/ocr/` | `tests/unit/test_ocr.py` | TEST-003 v1.0 | Draft |
| [REQ-004](requirements/REQ-004-protection.md) v1.0 | [DESIGN-004](design/DESIGN-004-protection.md) v1.0 | `src/pdftools/protection/` | `tests/unit/test_protection.py` | TEST-004 v1.0 | ✅ Released |
| [REQ-005](requirements/REQ-005-text-extraction.md) v1.0 | [DESIGN-005](design/DESIGN-005-text-extraction.md) v1.0 | `src/pdftools/text_extraction/` | `tests/unit/test_text_extraction_*.py` | TEST-005 v1.0 | ✅ Released |
| [REQ-006](requirements/REQ-006-thumbnails.md) v1.0 | DESIGN-006 v1.0 | `src/pdftools/thumbnails/` | `tests/unit/test_thumbnails.py` | TEST-006 v1.0 | Draft |
| [REQ-007](requirements/REQ-007-invoice-renaming.md) v1.0 | DESIGN-007 v1.0 | `src/pdftools/renaming/` | `tests/unit/test_renaming.py` | TEST-007 v1.0 | Draft |
| [REQ-008](requirements/REQ-008-installation-deinstallation.md) v1.0 | [DESIGN-008](design/DESIGN-008-installation-deinstallation.md) v1.0 | `scripts/install_lib.py`, `scripts/health_check.py`, `scripts/uninstall_lib.py` | `tests/unit/test_install_lib.py`, `tests/unit/test_health_check.py` | [TEST-008](test_reports/TEST-008-installation-deinstallation.md) v1.0 | ✅ Released |
| [REQ-009](requirements/REQ-009-cli-tools.md) v1.0 | [DESIGN-009](design/DESIGN-009-cli-tools.md) v1.0 | `src/pdftools/cli/`, `src/pdftools/*/cli.py`, `setup.py` | `tests/unit/test_cli_common.py`, `tests/e2e/test_cli_tools.py` | [TEST-009](test_reports/TEST-009-cli-tools.md) v1.0 | ✅ Released |

## Status Legende

- **Draft**: Requirement dokumentiert
- **In Design**: Design-Phase
- **In Development**: Implementierung läuft
- **In Testing**: Tests werden durchgeführt
- **✅ Released**: Alles fertig, getestet, released
- **Blocked**: Blockiert, wartet auf etwas

## Version History Tracking

Wenn ein Requirement sich ändert:
1. Version im Requirement-Dokument erhöhen
2. Neues Design erstellen (oder bestehendes aktualisieren)
3. Implementation anpassen
4. Neue Tests schreiben
5. Neuen Test Report erstellen

**Wichtig**: Test Reports referenzieren immer eine spezifische Requirement-Version!

## Beispiel Workflow

```
1. REQ-001 v1.0 erstellt → Status: Draft
2. Team Review → Status: Under Review
3. Approved → Status: Approved
4. DESIGN-001 v1.0 erstellt → Status: In Design
5. Implementation → Status: In Development
6. Tests geschrieben → Status: In Testing
7. TEST-001 v1.0 erstellt (referenziert REQ-001 v1.0)
8. Release → Status: Completed
```

Wenn sich später die Anforderung ändert:
```
9. REQ-001 v1.1 (Änderung) → Status: Under Review
10. DESIGN-001 v1.1 (Update)
11. Code angepasst
12. Tests angepasst
13. TEST-001 v1.1 (referenziert REQ-001 v1.1)
```
