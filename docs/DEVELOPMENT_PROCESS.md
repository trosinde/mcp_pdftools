# PDFTools Development Process

**Version**: 1.0
**Status**: Active
**Last Updated**: 2025-11-22

---

## Übersicht

Dieses Dokument beschreibt den **verbindlichen Entwicklungsprozess** für alle Features in diesem Projekt. Der Prozess basiert auf einem **9-Phasen-Workflow** mit **5 spezialisierten Team-Rollen**.

**WICHTIG**: Dieser Prozess ist **verpflichtend** für alle neuen Features und muss vollständig durchlaufen werden.

---

## Team-Rollen

Das Development Team besteht aus 5 spezialisierten Rollen:

### 1. Requirements Engineer 📋
**Verantwortlichkeiten**:
- Erstellt Requirements-Dokumente (REQ-XXX)
- Pflegt Requirements in `docs/requirements/`
- Versioniert Requirements (Semantic Versioning)
- Aktualisiert Traceability Matrix

**Deliverables**:
- `docs/requirements/REQ-XXX-name.md` (basierend auf `templates/requirement_template.md`)

### 2. Architekt 🏗️
**Verantwortlichkeiten**:
- Erstellt Design-Dokumente (DESIGN-XXX)
- Prüft Architektur auf SOLID Principles
- Reviewt Code-Struktur und Best Practices
- Stellt Testbarkeit sicher

**Deliverables**:
- `docs/design/DESIGN-XXX-name.md` (basierend auf `templates/design_template.md`)
- Architecture Review

### 3. Python Developer 💻
**Verantwortlichkeiten**:
- Implementiert Features gemäß Design
- Schreibt Type Hints und Docstrings (Google Style)
- Implementiert Error Handling
- Erstellt CLI-Interfaces

**Deliverables**:
- Implementation in `src/pdftools/module_name/`
- Code Review

### 4. Tester 🧪
**Verantwortlichkeiten**:
- Erstellt Unit, Integration und E2E Tests
- Generiert Test-Daten (Test-PDFs)
- Führt Tests aus und dokumentiert Ergebnisse
- Erstellt Test Reports (TEST-XXX)

**Deliverables**:
- Tests in `tests/unit/`, `tests/integration/`, `tests/e2e/`
- `docs/test_reports/TEST-XXX-name.md` (basierend auf `templates/test_report_template.md`)

### 5. DevOps Engineer 🐳
**Verantwortlichkeiten**:
- Setup-Skripte (Installation, Docker)
- CI/CD Integration
- Deployment-Prozesse
- Environment-Management

**Deliverables**:
- Scripts in `scripts/`
- Docker/Docker-Compose Configs

---

## 9-Phasen Workflow

Jedes Feature durchläuft **exakt** diese 9 Phasen:

### Phase 1: Requirements Engineering 📋

**Rolle**: Requirements Engineer

**Aufgaben**:
1. User-Anforderung analysieren
2. Requirement-Dokument erstellen:
   ```bash
   cp templates/requirement_template.md docs/requirements/REQ-XXX-name.md
   ```
3. Folgende Sektionen ausfüllen:
   - Übersicht & Geschäftsziel
   - Funktionale Anforderungen (mit Akzeptanzkriterien)
   - Nicht-Funktionale Anforderungen
   - Technische Details
   - Testbarkeit
   - Beispiele

**Status**: REQ-XXX Status = "Draft"

**Deliverable**: `docs/requirements/REQ-XXX-name.md`

---

### Phase 2: Team Review (Requirements) 👥

**Rollen**: Alle 5 Rollen

**Aufgaben**:
Jede Rolle prüft das Requirement aus ihrer Perspektive:

1. **Requirements Engineer**: Vollständigkeit, Klarheit
2. **Architekt**: Architektonische Implikationen, Machbarkeit
3. **Python Developer**: Implementierbarkeit, Aufwandsschätzung
4. **Tester**: Testbarkeit, Test-Daten-Anforderungen
5. **DevOps**: Setup/Installation, Deployment-Implikationen

**Review-Kriterien**:
- [ ] Alle Akzeptanzkriterien klar definiert?
- [ ] Technisch machbar?
- [ ] Testbar?
- [ ] Performance-Anforderungen realistisch?
- [ ] Dependencies geklärt?

**Status**: REQ-XXX Status = "Approved"

**Deliverable**: Review-Kommentare in REQ-XXX Dokument

---

### Phase 3: Design 🏗️

**Rolle**: Architekt

**Aufgaben**:
1. Design-Dokument erstellen:
   ```bash
   cp templates/design_template.md docs/design/DESIGN-XXX-name.md
   ```
2. Folgende Sektionen ausarbeiten:
   - Modul-Struktur
   - Komponenten-Diagramm
   - Datenfluss
   - API Design (Funktionen, Klassen, Datenmodelle)
   - Dependencies
   - Fehlerbehandlung (Exception-Hierarchie)
   - Logging & Monitoring
   - Performance-Ziele
   - Testbarkeit (Dependency Injection)
   - Security
   - Implementierungs-Plan mit Aufwandsschätzung

**SOLID Principles beachten**:
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

**Status**: DESIGN-XXX Status = "Draft"

**Deliverable**: `docs/design/DESIGN-XXX-name.md`

---

### Phase 4: Architecture Review 🔍

**Rolle**: Architekt + alle Rollen

**Aufgaben**:
Architektur-Review durchführen:

**Checkpoints**:
- [ ] SOLID Principles eingehalten
- [ ] DRY (Don't Repeat Yourself)
- [ ] Klare Separation of Concerns
- [ ] Testbarkeit gewährleistet (Dependency Injection)
- [ ] Type Hints vorgesehen
- [ ] Docstrings (Google Style) vorgesehen
- [ ] Error Handling robust
- [ ] Logging strukturiert
- [ ] Security-Aspekte berücksichtigt

**Team-Feedback**:
- Python Developer: Implementierbarkeit?
- Tester: Unit-Tests mockbar?
- DevOps: Deployment-Impact?

**Status**: DESIGN-XXX Status = "Approved"

**Deliverable**: Review-Kommentare in DESIGN-XXX Dokument

---

### Phase 5: Implementation 💻

**Rolle**: Python Developer

**Aufgaben**:
1. Modul-Struktur erstellen gemäß Design:
   ```
   src/pdftools/module_name/
   ├── __init__.py
   ├── core.py              # Hauptlogik
   ├── validators.py        # Input-Validierung
   ├── processors.py        # Verarbeitungslogik
   ├── formatters.py        # Output-Formatierung
   ├── models.py            # Datenmodelle
   └── cli.py              # CLI Interface (optional)
   ```

2. Implementation gemäß Design:
   - Type Hints **verpflichtend**
   - Docstrings **verpflichtend** (Google Style)
   - Error Handling mit spezifischen Exceptions
   - Logging mit strukturiertem Format
   - Dependency Injection für Testbarkeit

3. Code-Qualität sicherstellen:
   - Keine Code-Duplikation (DRY)
   - Klare Funktionsnamen
   - Maximal 20-30 Zeilen pro Funktion
   - Kommentare nur wo nötig (Code sollte selbsterklärend sein)

**Status**: DESIGN-XXX Status = "Implemented"

**Deliverable**: Implementation in `src/pdftools/module_name/`

---

### Phase 6: Code Review 👨‍💻

**Rolle**: Architekt

**Aufgaben**:
Code-Review durchführen:

**Checkpoints**:
- [ ] SOLID Principles eingehalten
- [ ] DRY befolgt
- [ ] Type Hints vollständig
- [ ] Docstrings vorhanden (Google Style)
- [ ] Error Handling robust
- [ ] Logging korrekt
- [ ] Security: Keine Secrets in Code/Logs
- [ ] Performance: Keine offensichtlichen Bottlenecks
- [ ] Testbarkeit: Dependency Injection verwendet

**Code-Qualität**:
- Lesbarkeit: **Ausgezeichnet** | Gut | Akzeptabel | **Unzureichend**
- Wartbarkeit: **Ausgezeichnet** | Gut | Akzeptabel | **Unzureichend**
- Performance: **Ausgezeichnet** | Gut | Akzeptabel | **Unzureichend**

**Status**: Code Review = "Approved" oder "Changes Requested"

**Deliverable**: Review-Kommentare

---

### Phase 7: Testing 🧪

**Rolle**: Tester

**Aufgaben**:

#### 7.1 Unit Tests schreiben
```
tests/unit/
  test_module_core.py
  test_module_validators.py
  test_module_processors.py
```

**Test-Coverage-Ziele**:
- Unit Tests: **> 90%**
- Core Logic: **> 95%**
- Validators: **100%**

**Test-Anforderungen**:
- Mocks für externe Dependencies
- Edge Cases abgedeckt
- Error Paths getestet

#### 7.2 Integration Tests schreiben
```
tests/integration/
  test_module_workflow.py
```

**Test-Szenarien**:
- End-to-End Workflows
- Zusammenspiel der Komponenten
- Reale File I/O

#### 7.3 E2E Tests (optional)
```
tests/e2e/
  test_module_cli.py
```

**Test-Szenarien**:
- CLI-Interface
- Reale Test-PDFs
- Performance-Tests

#### 7.4 Test-Daten generieren
- Test-PDFs erstellen mit `scripts/generate_test_pdfs.py`
- Verschiedene Szenarien: einfach, komplex, mit Bildern, OCR, verschlüsselt, korrupt

#### 7.5 Tests ausführen
```bash
pytest tests/unit/ -v --cov=src/pdftools/module_name
pytest tests/integration/ -v
```

**Akzeptanzkriterium**: Alle Tests müssen bestanden sein (100%)

**Status**: Tests = "Passed" oder "Failed"

**Deliverable**: Test-Dateien in `tests/`

---

### Phase 8: Test Report 📊

**Rolle**: Tester

**Aufgaben**:
1. Test-Report erstellen:
   ```bash
   cp templates/test_report_template.md docs/test_reports/TEST-XXX-name.md
   ```

2. Folgende Sektionen ausfüllen:
   - Test-Übersicht (Umgebung, Zeitraum)
   - Test-Coverage (Code Coverage, Kategorien)
   - Unit Tests (Ergebnisse, Zusammenfassung)
   - Integration Tests (Szenarien)
   - E2E Tests (CLI Tests)
   - Test-Daten & Fixtures
   - Performance Tests (optional)
   - Fehler & Issues
   - **Akzeptanzkriterien** (aus REQ-XXX prüfen!)
   - Empfehlungen

**Wichtig**: Jedes Akzeptanzkriterium aus REQ-XXX muss einzeln geprüft werden:
```markdown
1. [x] ✅ Kriterium 1: Erfüllt
   - Test: test_functional_requirement_1
   - Ergebnis: Passed
```

**Status Optionen**:
- ✅ **Passed**: Alle Tests bestanden, alle Akzeptanzkriterien erfüllt
- ⚠️ **Passed with Issues**: Tests bestanden, aber Minor Issues vorhanden
- ❌ **Failed**: Kritische Tests fehlgeschlagen

**Deliverable**: `docs/test_reports/TEST-XXX-name.md`

---

### Phase 9: Release Decision 🚀

**Rolle**: Alle Rollen (Product Team)

**Aufgaben**:
1. Review aller Artefakte:
   - REQ-XXX: Vollständig?
   - DESIGN-XXX: Korrekt umgesetzt?
   - Implementation: Code-Qualität OK?
   - TEST-XXX: Alle Akzeptanzkriterien erfüllt?

2. Release-Entscheidung treffen:

**Decision Matrix**:
| Kriterium | Status | Bewertung |
|-----------|--------|-----------|
| Requirements erfüllt | ✅/❌ | |
| Design umgesetzt | ✅/❌ | |
| Code Review bestanden | ✅/❌ | |
| Tests bestanden | ✅/❌ | |
| Akzeptanzkriterien | ✅/❌ | |
| Performance OK | ✅/❌ | |
| Security OK | ✅/❌ | |

**Release-Optionen**:
- ✅ **GO - Ready for Production**: Alle Kriterien erfüllt
- ⚠️ **GO with Restrictions**: Minor Issues, dokumentiert
- ❌ **NO-GO**: Kritische Issues, zurück zu Implementation/Testing

3. Status aktualisieren:
   ```markdown
   REQ-XXX: Status = "Released"
   DESIGN-XXX: Status = "Implemented"
   TEST-XXX: Status = "Passed"
   ```

4. Traceability Matrix aktualisieren:
   ```markdown
   | REQ-XXX v1.0 | DESIGN-XXX v1.0 | src/pdftools/module/ | tests/.../test_*.py | TEST-XXX v1.0 | ✅ Released |
   ```

5. Requirements Index aktualisieren:
   `docs/requirements/README.md`

**Deliverable**: Release Decision dokumentiert

---

## Git/GitHub Workflow 🔄

### Übersicht

Dieser Abschnitt definiert die **verbindliche Git/GitHub-Integration** in den 9-Phasen-Prozess.

**Strategie**: Feature Branch Workflow mit kontinuierlichen Commits

**Kernprinzipien**:
- Jede Phase committed ihre Artefakte sofort
- Ein Feature Branch pro REQ-XXX
- Pull Request für Release Decision
- Tags für produktive Releases

---

### Branch-Strategie

**Branch-Typen**:
```
main                                    # Production-ready code
  ├── feature/REQ-001-pdf-merge        # Feature branches
  ├── feature/REQ-002-pdf-split
  ├── feature/REQ-XXX-feature-name
  └── hotfix/fix-critical-bug          # Hotfixes (direkt von main)
```

**Naming Convention**:
- Feature Branches: `feature/REQ-XXX-short-name`
- Hotfix Branches: `hotfix/brief-description`
- Beispiele:
  - `feature/REQ-009-cli-tools`
  - `feature/REQ-010-ocr-processing`
  - `hotfix/fix-merge-memory-leak`

**Branch-Regeln**:
- **main**: Immer stabil, nur durch Merge von Feature-Branches
- **Feature Branches**: Leben während der gesamten Feature-Entwicklung (Phase 1-9)
- Nach Release: Feature Branch kann gelöscht werden
- Kein direktes Committen auf main!

---

### Commit Message Konventionen

**Format** (basierend auf Conventional Commits):
```
<type>(<scope>): <subject>

[optional body]

[optional footer]
```

**Types**:
| Type | Verwendung | Beispiel |
|------|------------|----------|
| `req` | Requirements-Dokumente | `req(cli): Create REQ-009 v1.0` |
| `design` | Design-Dokumente | `design(merge): Add DESIGN-001 architecture` |
| `feat` | Neue Features/Funktionen | `feat(cli): Implement pdfmerge CLI` |
| `test` | Tests hinzufügen/ändern | `test(merge): Add unit tests for validators` |
| `docs` | Dokumentation (außer req/design) | `docs(test): Add TEST-009 report` |
| `refactor` | Code-Refactoring ohne Funktionsänderung | `refactor(merge): Extract validation logic` |
| `fix` | Bugfixes | `fix(merge): Handle empty PDF files` |
| `build` | Build-System (setup.py, requirements.txt) | `build(setup): Add CLI entry points` |
| `ci` | CI/CD-Konfiguration | `ci(github): Add pytest workflow` |
| `chore` | Andere Änderungen (z.B. .gitignore) | `chore: Update .gitignore` |

**Scopes**:
- Modul-Namen: `merge`, `split`, `ocr`, `text`, `protection`, `thumbnails`, `renaming`
- Übergreifend: `cli`, `core`, `tests`

**Subject-Regeln**:
- Imperativ ("Add", nicht "Added" oder "Adds")
- Kein Punkt am Ende
- Maximal 72 Zeichen
- Englisch bevorzugt (für internationale Teams)

**Beispiele guter Commit Messages**:
```
req(cli): Create REQ-009 for CLI tools v1.0
design(merge): Add sequence diagrams to DESIGN-001
feat(cli): Implement common CLI utilities
feat(merge): Add pdfmerge command-line interface
test(cli): Add E2E tests for CLI tools
docs(test): Add TEST-009 comprehensive test report
fix(merge): Handle edge case for empty PDF files
refactor(cli): Extract argument parsing to common module
build(setup): Configure 7 CLI entry points
```

**Body & Footer** (optional):
```
feat(ocr): Add Docker-based OCR processing

Implements OCR functionality using Tesseract in Docker container.
Supports multiple languages (deu, eng, fra).

Closes #42
Refs: REQ-004 v1.0, DESIGN-004 v1.0
```

---

### Git-Aktivitäten pro Phase

#### Phase 1: Requirements Engineering 📋

**Git-Workflow**:
```bash
# 1. Feature Branch erstellen
git checkout main
git pull origin main
git checkout -b feature/REQ-009-cli-tools

# 2. Requirement-Dokument erstellen
cp templates/requirement_template.md docs/requirements/REQ-009-cli-tools.md
# ... Dokument ausfüllen ...

# 3. Committen
git add docs/requirements/REQ-009-cli-tools.md
git commit -m "req(cli): Create REQ-009 for CLI tools v1.0"

# 4. Push to remote
git push -u origin feature/REQ-009-cli-tools
```

**Commit Message Beispiel**:
```
req(cli): Create REQ-009 for CLI tools v1.0

Initial requirements for 7 CLI tools:
- pdfmerge, pdfsplit, pdfgettxt, ocrutil, pdfprotect, pdfthumbnails, pdfrename
```

---

#### Phase 2: Team Review (Requirements) 👥

**Git-Workflow**:
```bash
# Nach Review-Feedback: Requirement aktualisieren
git add docs/requirements/REQ-009-cli-tools.md
git commit -m "req(cli): Update REQ-009 after team review - Status: Approved"
git push
```

**Commit Message Beispiel**:
```
req(cli): Update REQ-009 after team review - Status: Approved

Addressed feedback:
- Clarified acceptance criteria for stub tools
- Added examples for all 7 CLI commands
```

---

#### Phase 3: Design 🏗️

**Git-Workflow**:
```bash
# Weiterhin auf demselben Feature Branch arbeiten
git checkout feature/REQ-009-cli-tools

# Design-Dokument erstellen
cp templates/design_template.md docs/design/DESIGN-009-cli-tools.md
# ... Dokument ausarbeiten ...

# Committen
git add docs/design/DESIGN-009-cli-tools.md
git commit -m "design(cli): Add DESIGN-009 architecture v1.0"
git push
```

**Commit Message Beispiel**:
```
design(cli): Add DESIGN-009 architecture v1.0

Architecture for 7 CLI tools with common utilities.
Defines entry points, argument parsing, and stub implementation strategy.
```

---

#### Phase 4: Architecture Review 🔍

**Git-Workflow**:
```bash
# Nach Review: Design aktualisieren falls nötig
git add docs/design/DESIGN-009-cli-tools.md
git commit -m "design(cli): Update DESIGN-009 after architecture review"
git push
```

---

#### Phase 5: Implementation 💻

**Git-Workflow** (mehrere Commits während Entwicklung):
```bash
# Weiterhin auf feature/REQ-009-cli-tools

# Commit 1: Gemeinsame Utilities
git add src/pdftools/cli/__init__.py src/pdftools/cli/common.py
git commit -m "feat(cli): Add common CLI utilities"

# Commit 2: pdfmerge CLI
git add src/pdftools/merge/cli.py
git commit -m "feat(merge): Implement pdfmerge CLI interface"

# Commit 3: Stub CLIs
git add src/pdftools/split/cli.py \
        src/pdftools/text_extraction/cli.py \
        src/pdftools/ocr/cli.py \
        src/pdftools/protection/cli.py \
        src/pdftools/thumbnails/cli.py \
        src/pdftools/renaming/cli.py
git commit -m "feat(cli): Add stub implementations for 6 CLI tools"

# Commit 4: Setup.py Entry Points
git add setup.py
git commit -m "build(setup): Configure CLI entry points for 7 tools"

# Push aller Commits
git push
```

**Best Practices für Implementation-Commits**:
- **Atomic Commits**: Jeder Commit ist eine logische Einheit
- **Häufige Commits**: Lieber viele kleine als ein großer Commit
- **Funktionierende States**: Jeder Commit sollte buildbar sein
- **Klare Messages**: Was wurde geändert und warum

---

#### Phase 6: Code Review 👨‍💻

**Git-Workflow**:
```bash
# Falls Code Review Änderungen erfordert
git add src/pdftools/cli/common.py
git commit -m "refactor(cli): Address code review feedback

- Improved error handling in print_error
- Added type hints to create_stub_message
- Extracted constants to top of file"

git push
```

**Code Review via GitHub**:
- Architekt reviewt direkt auf GitHub im Feature Branch
- Kommentare zu spezifischen Code-Zeilen
- Request Changes oder Approve
- Developer addressed Feedback, pushed neue Commits

---

#### Phase 7: Testing 🧪

**Git-Workflow**:
```bash
# Tests hinzufügen
git add tests/unit/test_cli_common.py
git commit -m "test(cli): Add unit tests for CLI common utilities"

git add tests/e2e/test_cli_tools.py
git commit -m "test(cli): Add E2E tests for all 7 CLI tools"

# Test-Fixtures
git add tests/fixtures/
git commit -m "test(cli): Add test fixtures for CLI testing"

git push
```

**Commit Message Beispiele**:
```
test(merge): Add unit tests for merge validators

- test_validate_input_files_with_valid_paths
- test_validate_input_files_with_invalid_paths
- test_validate_output_path_creates_directory
Coverage: 100% for validators module

---

test(merge): Add integration tests for merge workflow

End-to-end tests covering:
- Merging 2 PDFs
- Merging 10 PDFs
- Error handling for corrupted files
```

---

#### Phase 8: Test Report 📊

**Git-Workflow**:
```bash
# Test Report erstellen
git add docs/test_reports/TEST-009-cli-tools.md
git commit -m "docs(test): Add TEST-009 comprehensive test report

Status: ✅ Passed
- All 10 manual tests passed
- All 7 CLI tools available
- All acceptance criteria met
Recommendation: Ready for Production"

git push
```

---

#### Phase 9: Release Decision 🚀

**Git-Workflow**:

**Schritt 1: Pull Request erstellen**
```bash
# Via GitHub UI oder gh CLI
gh pr create \
  --title "REQ-009: CLI Tools v2.0.0" \
  --body "## Feature Summary

Complete implementation of 7 CLI tools with harmonized names.

## Traceability
- Requirements: REQ-009 v1.0 ✅ Approved
- Design: DESIGN-009 v1.0 ✅ Implemented
- Tests: TEST-009 v1.0 ✅ Passed

## Test Results
- Manual Tests: 10/10 passed
- All 7 CLI tools available
- All acceptance criteria met

## Release Decision
✅ **GO - Ready for Production**

Closes #XX"
```

**Schritt 2: Team Review des Pull Requests**
- Alle 5 Rollen reviewen den PR
- Prüfen Traceability (REQ → DESIGN → TEST)
- Approve oder Request Changes

**Schritt 3: Merge nach Approval**
```bash
# Merge via GitHub UI (Squash & Merge oder Merge Commit)
# Oder via CLI:
git checkout main
git pull origin main
git merge --no-ff feature/REQ-009-cli-tools
git push origin main
```

**Schritt 4: Release Tag erstellen**
```bash
# Semantic Versioning Tag
git tag -a v2.0.0 -m "Release: CLI Tools (REQ-009)

Features:
- 7 CLI tools with harmonized names
- pdfmerge fully functional
- 6 stub tools with informative messages

Traceability: REQ-009 v1.0 → DESIGN-009 v1.0 → TEST-009 v1.0"

git push origin v2.0.0
```

**Schritt 5: Feature Branch aufräumen (optional)**
```bash
# Lokal
git branch -d feature/REQ-009-cli-tools

# Remote
git push origin --delete feature/REQ-009-cli-tools
```

**Schritt 6: Traceability Matrix & README aktualisieren**
```bash
# Dokumente aktualisieren
git add docs/TRACEABILITY_MATRIX.md docs/requirements/README.md
git commit -m "docs: Update traceability for REQ-009 release"
git push origin main
```

---

### Pull Request Template

**Erstelle `.github/pull_request_template.md`**:
```markdown
## REQ-XXX: [Feature Name]

### Feature Summary
<!-- Kurze Beschreibung des Features -->

### Traceability
- [ ] Requirements: `REQ-XXX v1.0` - Status: Approved
- [ ] Design: `DESIGN-XXX v1.0` - Status: Implemented
- [ ] Tests: `TEST-XXX v1.0` - Status: Passed

### Development Process Checklist
- [ ] Phase 1-2: Requirements erstellt und reviewed
- [ ] Phase 3-4: Design erstellt und reviewed
- [ ] Phase 5-6: Implementation abgeschlossen und reviewed
- [ ] Phase 7: Tests geschrieben und ausgeführt (100% passed)
- [ ] Phase 8: Test Report erstellt
- [ ] Phase 9: Ready for Release Decision

### Test Results
- Manual Tests: X/X passed
- Unit Tests: X/X passed (Coverage: X%)
- Integration Tests: X/X passed
- E2E Tests: X/X passed

### Code Quality
- [ ] Type Hints vollständig
- [ ] Docstrings (Google Style) vorhanden
- [ ] SOLID Principles eingehalten
- [ ] Error Handling robust
- [ ] Logging strukturiert
- [ ] No security issues

### Acceptance Criteria
<!-- Liste alle Akzeptanzkriterien aus REQ-XXX und Status -->
- [ ] Kriterium 1: ...
- [ ] Kriterium 2: ...

### Release Decision
<!-- Wird vom Team ausgefüllt -->
- [ ] ✅ GO - Ready for Production
- [ ] ⚠️ GO with Restrictions (siehe Kommentare)
- [ ] ❌ NO-GO (zurück zu Phase X)

### Related Issues
Closes #XX
Refs: REQ-XXX, DESIGN-XXX, TEST-XXX
```

---

### GitHub Actions (CI/CD) - Optional

**Erstelle `.github/workflows/test.yml`**:
```yaml
name: Test Suite

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run unit tests
        run: |
          pytest tests/unit/ -v --cov=src/pdftools --cov-report=xml

      - name: Run integration tests
        run: |
          pytest tests/integration/ -v

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

**Erstelle `.github/workflows/lint.yml`**:
```yaml
name: Code Quality

on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install black isort flake8 mypy

      - name: Check code formatting (black)
        run: black --check src/ tests/

      - name: Check import sorting (isort)
        run: isort --check-only src/ tests/

      - name: Lint with flake8
        run: flake8 src/ tests/ --max-line-length=100

      - name: Type check with mypy
        run: mypy src/ --strict
```

---

### Branch Protection Rules (GitHub Settings)

**Empfohlene Settings für `main` Branch**:
- ✅ Require pull request reviews before merging (mindestens 1 Approval)
- ✅ Require status checks to pass before merging
  - `test` workflow must pass
  - `lint` workflow must pass
- ✅ Require conversation resolution before merging
- ✅ Require linear history (optional)
- ✅ Include administrators (auch Admins müssen PRs verwenden)

---

### Semantic Versioning für Releases

**Versions-Schema**: `MAJOR.MINOR.PATCH`

**Tag-Naming**:
```
v1.0.0    # Initial Release (REQ-001)
v2.0.0    # Major Release (REQ-009: CLI Tools)
v2.1.0    # Minor Release (REQ-010: New feature)
v2.1.1    # Patch Release (Bugfix)
```

**Wann welche Version?**:
- **MAJOR (v1.0 → v2.0)**: Breaking Changes, API-Änderungen
  - Beispiel: Umbenennung CLI-Tools, neue Modul-Struktur
- **MINOR (v2.0 → v2.1)**: Neue Features, backwards compatible
  - Beispiel: Neues Feature (OCR) hinzugefügt
- **PATCH (v2.1.0 → v2.1.1)**: Bugfixes, keine neuen Features
  - Beispiel: Fehler in pdfmerge behoben

**Release Tag erstellen**:
```bash
# Annotated Tag (bevorzugt)
git tag -a v2.0.0 -m "Release: CLI Tools

Features:
- REQ-009: CLI Tools with harmonized names
  - pdfmerge, pdfsplit, pdfgettxt, ocrutil
  - pdfprotect, pdfthumbnails, pdfrename

Traceability:
- REQ-009 v1.0 → DESIGN-009 v1.0 → TEST-009 v1.0

Breaking Changes: None
"

git push origin v2.0.0
```

---

### Hotfix-Workflow (Kritische Bugfixes)

**Szenario**: Kritischer Bug in Production muss sofort gefixt werden

**Workflow**:
```bash
# 1. Hotfix Branch von main erstellen
git checkout main
git pull origin main
git checkout -b hotfix/fix-merge-memory-leak

# 2. Bugfix implementieren
# ... Code ändern ...
git add src/pdftools/merge/core.py
git commit -m "fix(merge): Fix memory leak in large PDF processing

Closes #123"

# 3. Tests hinzufügen
git add tests/unit/test_merge_memory.py
git commit -m "test(merge): Add regression test for memory leak"

# 4. Push und Pull Request erstellen
git push -u origin hotfix/fix-merge-memory-leak
gh pr create --title "Hotfix: Memory leak in PDF merge" --label "hotfix"

# 5. Nach Approval: Merge zu main
git checkout main
git merge hotfix/fix-merge-memory-leak

# 6. Patch Release Tag
git tag -a v2.0.1 -m "Hotfix: Memory leak in merge"
git push origin main v2.0.1

# 7. Hotfix Branch löschen
git branch -d hotfix/fix-merge-memory-leak
git push origin --delete hotfix/fix-merge-memory-leak
```

**Hinweis**: Hotfixes überspringen normalerweise den vollen 9-Phasen-Prozess, müssen aber trotzdem:
- Getestet werden (mindestens Regression-Test)
- Reviewed werden
- Dokumentiert werden (im Commit und in Changelog)

---

### Best Practices

**Commit-Hygiene**:
- ✅ Committe häufig (nach jeder logischen Änderung)
- ✅ Jeder Commit sollte buildbar/lauffähig sein
- ✅ Aussagekräftige Commit Messages
- ✅ Atomic Commits (eine Änderung = ein Commit)
- ❌ Keine "WIP"-Commits auf main
- ❌ Keine Secrets in Commits
- ❌ Keine großen Binary-Files committen

**Branch-Hygiene**:
- ✅ Feature Branches regelmäßig mit main synchronisieren (rebase oder merge)
- ✅ Branches löschen nach Merge
- ✅ Branch-Namen beschreibend halten
- ❌ Kein direktes Committen auf main
- ❌ Keine lang laufenden Feature Branches (> 2 Wochen)

**Pull Request Best Practices**:
- ✅ Beschreibender Titel und Body
- ✅ Template verwenden
- ✅ Screenshots/GIFs bei UI-Änderungen
- ✅ Traceability zu REQ/DESIGN/TEST herstellen
- ✅ Selbst-Review vor Einreichung
- ❌ Keine riesigen PRs (> 500 Lines Changed)

**Review-Hygiene**:
- ✅ Konstruktives Feedback
- ✅ Code UND Dokumentation reviewen
- ✅ Traceability prüfen (REQ → DESIGN → Implementation → Tests)
- ✅ Tests lokal ausführen
- ❌ Nicht nur "LGTM" ohne echtes Review

---

### Git-Befehle Cheat Sheet

**Tägliche Arbeit**:
```bash
# Status checken
git status

# Änderungen stagen
git add file.py
git add src/pdftools/module/  # Ganzes Verzeichnis

# Committen
git commit -m "feat(module): Add feature X"

# Pushen
git push

# Aktualisieren
git pull

# Branch wechseln
git checkout branch-name

# Neuer Branch
git checkout -b feature/REQ-XXX-name
```

**Feature Branch Workflow**:
```bash
# Neues Feature starten
git checkout main
git pull
git checkout -b feature/REQ-010-ocr

# Während Entwicklung
git add .
git commit -m "feat(ocr): Implement OCR processing"
git push

# Main in Feature Branch mergen (bei Konflikten)
git checkout feature/REQ-010-ocr
git merge main
# Konflikte lösen
git commit

# Feature fertig: Pull Request erstellen
gh pr create --title "REQ-010: OCR Processing"

# Nach Merge: Branch löschen
git branch -d feature/REQ-010-ocr
git push origin --delete feature/REQ-010-ocr
```

**Fehler beheben**:
```bash
# Letzten Commit rückgängig (noch nicht gepusht!)
git reset --soft HEAD~1

# Änderungen verwerfen
git checkout -- file.py

# Commit Message ändern (noch nicht gepusht!)
git commit --amend -m "Neue Message"

# Versehentlich auf main committed (noch nicht gepusht!)
git checkout -b feature/REQ-XXX-name  # Neuer Branch mit Änderungen
git checkout main
git reset --hard origin/main  # Main zurücksetzen
```

---

### Visualisierung: Feature Branch Lifecycle

```
main:     A───B───────────────G───H  (v2.0.0)
               \               /
feature:        C───D───E───F
                    └── PR ──┘

C: req(cli): Create REQ-009 v1.0
D: design(cli): Add DESIGN-009 v1.0
E: feat(cli): Implement CLI tools
F: docs(test): Add TEST-009 report
G: Merge feature → main
H: Tag v2.0.0
```

---

### Zusammenfassung Git-Integration

**Kernpunkte**:
1. **Ein Feature Branch pro REQ-XXX** - Feature-basierte Entwicklung
2. **Kontinuierliche Commits** - Nach jeder Phase committen
3. **Klare Commit Messages** - Conventional Commits Format
4. **Pull Requests für Release** - Phase 9 als PR-Review
5. **Tags für Releases** - Semantic Versioning
6. **Main ist heilig** - Nur stabile, getestete Features

**Workflow in einem Satz**:
> Feature Branch erstellen → 9 Phasen durchlaufen (mit Commits) → Pull Request → Review → Merge → Tag → Release

---

## Versionierung

### Requirements Versioning (Semantic Versioning)

**Format**: `MAJOR.MINOR.PATCH`

**Semantik**:
- **MAJOR**: Breaking Changes, grundlegende Änderung der Anforderung
  - Beispiel: REQ-001 v1.0 → v2.0 (API komplett geändert)
- **MINOR**: Neue Anforderungen hinzugefügt, backwards compatible
  - Beispiel: REQ-001 v1.0 → v1.1 (neues optionales Feature)
- **PATCH**: Kleinere Klarstellungen, Korrekturen, keine funktionalen Änderungen
  - Beispiel: REQ-001 v1.0 → v1.0.1 (Typo-Fix)

**Version Change Workflow**:
```
1. REQ-XXX Version erhöhen (z.B. v1.0 → v1.1)
2. DESIGN-XXX entsprechend aktualisieren (v1.0 → v1.1)
3. Implementation anpassen
4. Tests anpassen/erweitern
5. TEST-XXX neu erstellen (referenziert neue REQ-Version!)
```

### Traceability

**Wichtig**: Jeder Test Report referenziert **exakt** eine Requirement-Version:
```markdown
**Tested Requirement Version**: REQ-008 v1.0

Bei Änderungen an den Requirements muss ein neuer Test-Report erstellt werden!
```

**Traceability Chain**:
```
REQ-XXX v1.0 ──→ DESIGN-XXX v1.0 ──→ Implementation ──→ TEST-XXX v1.0
     ↑                                                        |
     └────────────────────────────────────────────────────────┘
                    (referenziert Requirement-Version)
```

---

## File Structure

```
mcp_pdftools/
├── docs/
│   ├── requirements/
│   │   ├── README.md                    # Requirements Index
│   │   ├── REQ-001-pdf-merge.md
│   │   ├── REQ-002-pdf-split.md
│   │   └── REQ-XXX-name.md
│   ├── design/
│   │   ├── DESIGN-001-pdf-merge.md
│   │   └── DESIGN-XXX-name.md
│   ├── test_reports/
│   │   ├── TEST-001-pdf-merge.md
│   │   └── TEST-XXX-name.md
│   ├── TRACEABILITY_MATRIX.md           # Vollständige Traceability
│   └── DEVELOPMENT_PROCESS.md           # Dieses Dokument
│
├── templates/
│   ├── requirement_template.md
│   ├── design_template.md
│   └── test_report_template.md
│
├── src/
│   └── pdftools/
│       ├── core/
│       │   ├── exceptions.py
│       │   ├── validators.py
│       │   └── utils.py
│       └── module_name/
│           ├── __init__.py
│           ├── core.py
│           ├── validators.py
│           ├── processors.py
│           ├── models.py
│           └── cli.py
│
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_module_core.py
│   │   └── test_module_validators.py
│   ├── integration/
│   │   └── test_module_workflow.py
│   └── e2e/
│       └── test_module_cli.py
│
└── scripts/
    ├── generate_test_pdfs.py
    ├── install.sh
    └── uninstall.sh
```

---

## Code-Qualität Standards

### Python Code Style

**Type Hints**: Verpflichtend
```python
def merge_pdfs(
    files: List[Path],
    output_path: Optional[Path] = None,
    config: Optional[MergeConfig] = None
) -> MergeResult:
    ...
```

**Docstrings**: Google Style, verpflichtend
```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description.

    Longer description with more details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        PDFNotFoundError: When file not found
        PDFProcessingError: When processing fails

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

**Error Handling**: Spezifische Exceptions
```python
# Exception-Hierarchie in src/pdftools/core/exceptions.py
class PDFToolsError(Exception):
    """Base exception for all PDFTools errors"""

class PDFNotFoundError(PDFToolsError):
    """PDF file not found"""

class PDFProcessingError(PDFToolsError):
    """PDF processing failed"""

# Usage
def process_pdf(path: Path) -> Result:
    if not path.exists():
        raise PDFNotFoundError(f"PDF file not found: {path}")

    try:
        # ... processing ...
    except Exception as e:
        raise PDFProcessingError(f"Failed to process {path}: {e}")
```

**Logging**: Strukturiert
```python
import logging

logger = logging.getLogger('pdftools.module_name')

# Log-Levels:
logger.debug("Detailed processing info")
logger.info("Processing file: {path}")
logger.warning("Skipping corrupted file: {path}")
logger.error("Failed to process {path}: {error}")
logger.critical("Fatal error")
```

**Dependency Injection**: Für Testbarkeit
```python
from typing import Protocol

class PDFReaderInterface(Protocol):
    def read(self, path: Path) -> PdfReader: ...

class PDFProcessor:
    def __init__(self, reader: Optional[PDFReaderInterface] = None):
        self.reader = reader or DefaultPDFReader()

    def process(self, path: Path) -> Result:
        pdf = self.reader.read(path)  # Mockbar!
        # ...
```

---

## Testing Standards

### Unit Tests

**Naming Convention**:
```python
def test_function_name_with_valid_input():
    """Test function_name with valid input"""
    ...

def test_function_name_with_invalid_path():
    """Test function_name raises error on invalid path"""
    ...

def test_function_name_edge_case_empty_list():
    """Test function_name handles empty list"""
    ...
```

**Coverage Requirements**:
- **Core Logic**: > 95%
- **Validators**: 100%
- **Processors**: > 90%
- **CLI**: > 80%
- **Overall**: > 90%

**Mocking**: Verwende pytest-mock oder monkeypatch
```python
def test_with_mock(monkeypatch):
    mock_reader = Mock()
    processor = PDFProcessor(reader=mock_reader)
    ...
```

### Integration Tests

**Test-Szenarien**:
- End-to-End Workflows
- Datei I/O (mit temp directories)
- Error Handling
- Performance (optional)

---

## Beispiel: Vollständiger Workflow

**User-Anforderung**: "Ich möchte PDFs zusammenführen können"

### Phase 1-2: Requirements
1. Requirements Engineer erstellt `REQ-001-pdf-merge.md`
2. Team reviewt → **APPROVED**

### Phase 3-4: Design
3. Architekt erstellt `DESIGN-001-pdf-merge.md`
4. Team reviewt Design → **APPROVED**

### Phase 5-6: Implementation
5. Python Developer implementiert `src/pdftools/merge/`
6. Architekt reviewt Code → **APPROVED**

### Phase 7-8: Testing
7. Tester schreibt 38 Tests (29 Unit, 9 Integration)
8. Tester erstellt `TEST-001-pdf-merge.md` → **PASSED**

### Phase 9: Release
9. Team Decision: **✅ GO - Ready for Production**
10. Status-Updates:
    - REQ-001 → "Released"
    - DESIGN-001 → "Implemented"
    - TEST-001 → "Passed"
11. Traceability Matrix aktualisiert

**Ergebnis**: Feature ist released und produktionsbereit! 🎉

---

## Checkliste für neue Features

- [ ] **Phase 1**: REQ-XXX erstellt (aus Template)
- [ ] **Phase 2**: Team Review durchgeführt, alle Rollen approved
- [ ] **Phase 3**: DESIGN-XXX erstellt (aus Template)
- [ ] **Phase 4**: Architecture Review durchgeführt, SOLID Principles geprüft
- [ ] **Phase 5**: Implementation in `src/pdftools/module_name/`
- [ ] **Phase 6**: Code Review bestanden
- [ ] **Phase 7**: Tests geschrieben (Unit + Integration)
- [ ] **Phase 7**: Tests ausgeführt, alle bestanden
- [ ] **Phase 8**: TEST-XXX erstellt, Akzeptanzkriterien geprüft
- [ ] **Phase 9**: Release Decision getroffen
- [ ] **Phase 9**: Traceability Matrix aktualisiert
- [ ] **Phase 9**: Requirements Index aktualisiert

---

## Weitere Ressourcen

**Templates**:
- `templates/requirement_template.md`
- `templates/design_template.md`
- `templates/test_report_template.md`

**Dokumentation**:
- `docs/architecture/ARCHITECTURE_GUIDELINES.md`
- `docs/TRACEABILITY_MATRIX.md`

**Tools**:
- `scripts/generate_test_pdfs.py` - Test-PDF-Generierung
- `scripts/health_check.py` - Installation-Validierung

---

## Kontakt & Support

**Bei Fragen zum Prozess**:
- Siehe Beispiel-Features: REQ-001 (PDF Merge), REQ-008 (Installation)
- Verwende Templates in `templates/`
- Orientiere dich an TRACEABILITY_MATRIX.md

**Prozess-Updates**:
- Dieses Dokument wird bei Prozess-Änderungen aktualisiert
- Version History siehe unten

---

## Version History

| Datum | Version | Änderung | Von |
|-------|---------|----------|-----|
| 2025-11-22 | 1.0 | Initiale Prozess-Dokumentation | Development Team |

---

**Happy Development! 🚀**
