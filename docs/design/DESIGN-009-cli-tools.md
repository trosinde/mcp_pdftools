# Design Document: Command-Line Interface (CLI) Tools

**ID**: DESIGN-009
**Version**: 1.0
**Requirement**: [REQ-009](../requirements/REQ-009-cli-tools.md) v1.0
**Status**: Implemented
**Architekt**: System Architect
**Entwickler**: Python Developer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-009 v1.0
- Tested by: TEST-009 v1.0

---

## 1. Übersicht

### 1.1 Ziel
7 benutzerfreundliche CLI-Tools erstellen (ein Tool pro Feature), die direkt aus der Kommandozeile ohne Programmierung verwendbar sind. Harmonisierte Namen basierend auf Legacy-Tools.

### 1.2 Scope
**In Scope:**
- CLI-Interface für pdfmerge (voll funktionsfähig, basiert auf REQ-001)
- CLI-Stubs für 6 weitere Tools (pdfsplit, pdfgettxt, ocrutil, pdfprotect, pdfthumbnails, pdfrename)
- Gemeinsame CLI-Utilities (Logging, Error Handling, Output Formatting)
- Entry Point Konfiguration (pyproject.toml)

**Out of Scope:**
- Implementierung der Core-Features für REQ-002 bis REQ-007 (separate Requirements)
- GUI-Interface
- Web-Interface

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/
├── cli/
│   ├── __init__.py
│   └── common.py           # Gemeinsame CLI-Utilities
├── merge/
│   ├── __init__.py
│   ├── core.py
│   ├── models.py
│   ├── validators.py
│   └── cli.py              # NEU: CLI für pdfmerge
├── split/
│   └── cli.py              # STUB: "Feature coming soon"
├── text_extraction/
│   └── cli.py              # STUB
├── ocr/
│   └── cli.py              # STUB
├── protection/
│   └── cli.py              # STUB
├── thumbnails/
│   └── cli.py              # STUB
└── renaming/
    └── cli.py              # STUB
```

### 2.2 Entry Points (pyproject.toml)

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

---

## 3. API Design

### 3.1 Gemeinsame CLI-Utilities (src/pdftools/cli/common.py)

```python
"""Common utilities for all CLI tools"""

import sys
from typing import Optional

# ANSI Color Codes
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_success(message: str, use_color: bool = True):
    """Print success message with green checkmark"""
    if use_color:
        print(f"{GREEN}✓{RESET} {message}")
    else:
        print(f"✓ {message}")

def print_error(message: str, use_color: bool = True):
    """Print error message with red cross"""
    if use_color:
        print(f"{RED}✗{RESET} {message}", file=sys.stderr)
    else:
        print(f"✗ {message}", file=sys.stderr)

def print_warning(message: str, use_color: bool = True):
    """Print warning message with yellow warning sign"""
    if use_color:
        print(f"{YELLOW}⚠{RESET} {message}")
    else:
        print(f"⚠ {message}")

def setup_logging(verbose: bool) -> None:
    """Setup logging based on verbose flag"""
    import logging
    level = logging.DEBUG if verbose else logging.WARNING
    logging.basicConfig(
        level=level,
        format='%(levelname)s: %(message)s'
    )

def handle_keyboard_interrupt():
    """Handle Ctrl+C gracefully"""
    print_warning("\nOperation cancelled by user")
    sys.exit(130)  # Standard exit code for SIGINT

def create_stub_message(tool_name: str, feature_name: str) -> str:
    """Create 'coming soon' message for stub tools"""
    return f"""
{tool_name} - {feature_name}

⚠ This feature is not yet implemented.

The core functionality needs to be developed first.
Check the project roadmap for implementation status.

To contribute or track progress:
- See docs/requirements/ for feature requirements
- Check docs/TRACEABILITY_MATRIX.md for status

For now, you can use the Python API if the core module exists:
    from pdftools.{tool_name.replace('pdf', '').replace('util', '')} import ...
"""
```

### 3.2 pdfmerge CLI (src/pdftools/merge/cli.py) - VOLL FUNKTIONSFÄHIG

```python
#!/usr/bin/env python3
"""CLI Interface for PDF Merge Tool"""

import argparse
import sys
from pathlib import Path
from typing import List

from pdftools.merge import merge_pdfs, MergeConfig
from pdftools.cli.common import (
    print_success, print_error, print_warning,
    setup_logging, handle_keyboard_interrupt
)

def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for pdfmerge"""
    parser = argparse.ArgumentParser(
        description='Merge multiple PDF files into one',
        prog='pdfmerge',
        epilog='Example: pdfmerge file1.pdf file2.pdf -o merged.pdf'
    )

    parser.add_argument(
        'files',
        nargs='+',
        type=Path,
        metavar='FILE',
        help='PDF files to merge (minimum 2 files)'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        required=True,
        metavar='OUTPUT',
        help='Output PDF file path'
    )

    parser.add_argument(
        '--skip-on-error',
        action='store_true',
        help='Skip corrupted files instead of aborting'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0'
    )

    return parser

def main():
    """Main entry point for pdfmerge command"""
    try:
        parser = create_parser()
        args = parser.parse_args()

        # Setup
        setup_logging(args.verbose)
        use_color = not args.no_color

        # Validate minimum files
        if len(args.files) < 2:
            print_error("At least 2 PDF files are required", use_color)
            sys.exit(2)

        # Merge PDFs
        print(f"Merging {len(args.files)} PDF file(s)...")

        config = MergeConfig(
            skip_on_error=args.skip_on_error,
            verbose=args.verbose
        )

        result = merge_pdfs(
            files=args.files,
            output_path=args.output,
            config=config
        )

        # Handle result
        if result.success:
            print_success(
                f"Successfully merged {result.pages_merged} pages",
                use_color
            )
            print_success(f"Output: {result.output_path}", use_color)

            if result.skipped_files:
                print_warning(
                    f"Skipped {len(result.skipped_files)} file(s):",
                    use_color
                )
                for f in result.skipped_files:
                    print(f"  - {f}")

            sys.exit(0)
        else:
            print_error(f"Error: {result.message}", use_color)
            sys.exit(1)

    except KeyboardInterrupt:
        handle_keyboard_interrupt()
    except Exception as e:
        print_error(f"Unexpected error: {e}", use_color=True)
        sys.exit(3)

if __name__ == '__main__':
    main()
```

### 3.3 Stub CLI Template (für alle anderen Tools)

```python
#!/usr/bin/env python3
"""CLI Stub for [TOOL_NAME]"""

import sys
from pdftools.cli.common import create_stub_message

def main():
    """Main entry point - shows 'coming soon' message"""
    print(create_stub_message(
        tool_name="[tool_name]",
        feature_name="[Feature Name]"
    ))
    sys.exit(1)

if __name__ == '__main__':
    main()
```

---

## 4. Implementation Plan

### Phase 1: Common Utilities (1 Stunde)
- [ ] Erstelle `src/pdftools/cli/__init__.py`
- [ ] Implementiere `src/pdftools/cli/common.py`
- [ ] Unit Tests für common utilities

### Phase 2: pdfmerge CLI (2 Stunden)
- [ ] Erstelle `src/pdftools/merge/cli.py`
- [ ] Implementiere vollständiges CLI mit argparse
- [ ] Unit Tests für Argument Parsing
- [ ] Integration Tests mit Mocks
- [ ] E2E Tests via Subprocess

### Phase 3: CLI Stubs (1 Stunde)
- [ ] Erstelle 6 Stub-Dateien:
  - `src/pdftools/split/cli.py`
  - `src/pdftools/text_extraction/cli.py`
  - `src/pdftools/ocr/cli.py`
  - `src/pdftools/protection/cli.py`
  - `src/pdftools/thumbnails/cli.py`
  - `src/pdftools/renaming/cli.py`

### Phase 4: Entry Points Setup (30 Minuten)
- [ ] Update `pyproject.toml` mit allen Entry Points
- [ ] Test Installation: `pip install -e .`
- [ ] Verify alle 7 Kommandos sind verfügbar

**Total Effort**: ~4.5 Stunden

---

## 5. Testing Strategy

### 5.1 Unit Tests (tests/unit/test_cli_*.py)

```python
# tests/unit/test_cli_merge.py
def test_pdfmerge_parser():
    """Test argument parser"""
    from pdftools.merge.cli import create_parser

    parser = create_parser()
    args = parser.parse_args(['f1.pdf', 'f2.pdf', '-o', 'out.pdf'])

    assert len(args.files) == 2
    assert args.output == Path('out.pdf')
    assert not args.skip_on_error
    assert not args.verbose

def test_pdfmerge_minimum_files_error():
    """Test error when less than 2 files"""
    # Test validation logic
```

### 5.2 Integration Tests

```python
# tests/integration/test_cli_merge_integration.py
def test_pdfmerge_calls_core_function(monkeypatch):
    """Test CLI calls merge_pdfs correctly"""
    from pdftools.merge.cli import main
    from pdftools.merge import merge_pdfs, MergeResult

    # Mock merge_pdfs
    mock_result = MergeResult(success=True, pages_merged=5)
    mock_merge = Mock(return_value=mock_result)
    monkeypatch.setattr('pdftools.merge.cli.merge_pdfs', mock_merge)

    # Mock sys.argv
    monkeypatch.setattr('sys.argv', [
        'pdfmerge', 'f1.pdf', 'f2.pdf', '-o', 'out.pdf'
    ])

    # Run
    with pytest.raises(SystemExit) as exc:
        main()

    assert exc.value.code == 0
    assert mock_merge.called
```

### 5.3 E2E Tests

```python
# tests/e2e/test_cli_e2e.py
def test_pdfmerge_e2e(test_pdfs, tmp_path):
    """Test actual CLI execution"""
    output = tmp_path / "merged.pdf"

    result = subprocess.run([
        'pdfmerge',
        str(test_pdfs['simple']),
        str(test_pdfs['multipage']),
        '-o', str(output)
    ], capture_output=True, text=True)

    assert result.returncode == 0
    assert output.exists()
    assert "Successfully merged" in result.stdout
```

---

## 6. Error Handling

### Exit Codes
- **0**: Success
- **1**: General error (file not found, processing error)
- **2**: Validation error (invalid arguments)
- **3**: Unexpected error
- **130**: Keyboard interrupt (Ctrl+C)

### Error Messages
```python
# User-friendly, no Python tracebacks
✗ Error: PDF file not found: input.pdf
✗ Error: At least 2 PDF files are required
✗ Error: Cannot write to output.pdf (permission denied)
```

---

## 7. Review & Approval

### Architektur-Review
**Reviewer**: [TBD]
**Status**: ⏳ Pending

**Checkpoints**:
- [ ] SOLID Principles
- [ ] DRY
- [ ] Separation of Concerns (CLI ↔ Core)
- [ ] Testbarkeit
- [ ] Type Hints
- [ ] Docstrings
- [ ] Error Handling

---

## 8. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | System Architect | REQ-009 v1.0 |
