# Architecture Guidelines für MCP PDF Tools

Version: 2.0
Datum: 2025-11-22

---

## 1. Überblick

Dieses Dokument definiert die architektonischen Richtlinien für die Entwicklung von MCP PDF Tools. Alle Entwickler und Architekten müssen diese Guidelines befolgen, um Konsistenz, Wartbarkeit und Testbarkeit zu gewährleisten.

---

## 2. Architektur-Prinzipien

### 2.1 SOLID Principles

#### Single Responsibility Principle (SRP)
- Jede Klasse/Funktion hat genau eine Verantwortung
- Trennung von Concerns: Validation, Processing, Formatting
- Beispiel:
  ```python
  # ❌ Schlecht: Alles in einer Funktion
  def process_pdf(path):
      validate(path)
      data = read(path)
      result = process(data)
      save(result)
      return result

  # ✅ Gut: Getrennte Verantwortlichkeiten
  def process_pdf(path):
      validated_path = validate_path(path)
      reader = PDFReader(validated_path)
      processor = PDFProcessor()
      result = processor.process(reader.read())
      return result
  ```

#### Open/Closed Principle (OCP)
- Offen für Erweiterung, geschlossen für Modifikation
- Verwendung von Interfaces/Abstract Classes
- Beispiel:
  ```python
  from abc import ABC, abstractmethod

  class PDFProcessor(ABC):
      @abstractmethod
      def process(self, pdf_data) -> Result:
          pass

  class MergeProcessor(PDFProcessor):
      def process(self, pdf_data) -> Result:
          # Merge-spezifische Logik
          pass
  ```

#### Liskov Substitution Principle (LSP)
- Subklassen müssen Superklassen ersetzen können
- Keine Breaking Changes in Subklassen

#### Interface Segregation Principle (ISP)
- Kleine, spezifische Interfaces statt große, monolithische
- Clients sollten nicht von Interfaces abhängen, die sie nicht nutzen

#### Dependency Inversion Principle (DIP)
- Abhängigkeiten von Abstraktionen, nicht von Konkretionen
- Dependency Injection verwenden
- Beispiel:
  ```python
  # ✅ Dependency Injection
  class PDFMerger:
      def __init__(self, reader: PDFReaderInterface):
          self.reader = reader  # Abstraktion, nicht Konkretion

      def merge(self, files: List[Path]) -> Result:
          pass
  ```

### 2.2 DRY (Don't Repeat Yourself)
- Wiederverwendbarer Code in `core` Modul
- Gemeinsame Utilities nicht duplizieren
- Configuration über zentrale Config-Klassen

### 2.3 KISS (Keep It Simple, Stupid)
- Einfache, verständliche Lösungen bevorzugen
- Keine Over-Engineering
- Clear ist besser als Clever

### 2.4 YAGNI (You Aren't Gonna Need It)
- Keine Features implementieren, die nicht benötigt werden
- Fokus auf Requirements

---

## 3. Modul-Architektur

### 3.1 Standard Modul-Struktur

Jedes PDF-Tool folgt dieser Struktur:

```
src/pdftools/[module_name]/
├── __init__.py          # Public API exports
├── core.py              # Hauptlogik, Orchestrierung
├── validators.py        # Input-Validierung
├── processors.py        # Verarbeitungslogik
├── formatters.py        # Output-Formatierung
├── exceptions.py        # Modul-spezifische Exceptions (optional)
├── models.py            # Datenmodelle (dataclasses)
├── config.py            # Konfiguration (optional)
└── cli.py               # CLI Interface
```

### 3.2 Layer-Architektur

```
┌────────────────────┐
│   CLI Layer        │  ← User Interface (cli.py)
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  Validation Layer  │  ← Input Validation (validators.py)
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│   Core Layer       │  ← Business Logic (core.py)
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  Processing Layer  │  ← PDF Operations (processors.py)
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│  Formatting Layer  │  ← Output Formatting (formatters.py)
└─────────┬──────────┘
          │
┌─────────▼──────────┐
│   File I/O         │  ← File Operations
└────────────────────┘
```

**Layer Rules:**
- Jeder Layer darf nur den darunterliegenden Layer aufrufen
- Keine Upward Dependencies
- Cross-cutting Concerns (Logging, Exceptions) über alle Layer

### 3.3 Dependency Flow

```
CLI → Validators → Core → Processors → Formatters → File I/O
  ↓        ↓        ↓         ↓            ↓
  └────── Shared Core Utilities (exceptions, logging, etc.) ──────┘
```

---

## 4. Code-Organisation

### 4.1 Public API (`__init__.py`)

Nur definierte, stabile Funktionen exportieren:

```python
# src/pdftools/module_name/__init__.py
from .core import main_function, helper_function
from .models import Result, Config
from .exceptions import ModuleSpecificError

__all__ = [
    'main_function',
    'helper_function',
    'Result',
    'Config',
    'ModuleSpecificError',
]
```

### 4.2 Private vs Public

- **Public**: Exportiert in `__init__.py`, dokumentiert, stabil
- **Private**: Präfix `_`, nicht exportiert, kann sich ändern

```python
# ✅ Public function
def merge_pdfs(files: List[Path]) -> Result:
    """Documented public API"""
    pass

# ✅ Private function
def _internal_helper(data):
    """Internal use only"""
    pass
```

### 4.3 Type Hints

**Pflicht** für alle Funktionen:

```python
from typing import List, Optional, Union
from pathlib import Path

def process_pdf(
    input_path: Union[str, Path],
    output_path: Optional[Path] = None,
    verbose: bool = False
) -> Result:
    """
    Process a PDF file

    Args:
        input_path: Path to input PDF
        output_path: Optional output path
        verbose: Enable verbose logging

    Returns:
        Result object with processing information
    """
    pass
```

### 4.4 Docstrings

**Google Style** verwenden:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Short description (one line).

    Longer description if needed. Can span multiple lines
    and provide more context.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param1 is empty
        PDFNotFoundError: When file doesn't exist

    Example:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## 5. Error Handling

### 5.1 Exception-Hierarchie

```
PDFToolsError (base)
├── PDFNotFoundError
├── PDFProcessingError
│   ├── PDFCorruptedError
│   └── PDFEncryptedError
└── ValidationError
    ├── InvalidPathError
    └── InvalidParameterError
```

### 5.2 Exception Best Practices

```python
# ✅ Spezifische Exceptions
try:
    pdf = read_pdf(path)
except FileNotFoundError:
    raise PDFNotFoundError(path)
except PermissionError:
    raise InsufficientPermissionsError(path, "read")

# ❌ Zu breites Exception Handling
try:
    pdf = read_pdf(path)
except Exception as e:
    print(f"Error: {e}")  # Keine Fehlerbehandlung!
```

### 5.3 Context Manager

Für Ressourcen-Management verwenden:

```python
class PDFReader:
    def __enter__(self):
        self.file = open(self.path, 'rb')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()

# Verwendung
with PDFReader(path) as reader:
    data = reader.read()
```

---

## 6. Testbarkeit

### 6.1 Dependency Injection

```python
# ✅ Testbar durch DI
class PDFProcessor:
    def __init__(self, reader: PDFReaderInterface = None):
        self.reader = reader or DefaultPDFReader()

    def process(self, path: Path):
        return self.reader.read(path)

# Test
def test_processor():
    mock_reader = MockPDFReader()
    processor = PDFProcessor(reader=mock_reader)
    result = processor.process("test.pdf")
    assert result == expected
```

### 6.2 Pure Functions

Wo möglich, pure functions verwenden:

```python
# ✅ Pure function (testbar, vorhersagbar)
def calculate_pages(pdf_data: bytes) -> int:
    return len(extract_pages(pdf_data))

# ❌ Impure function (schwer testbar)
def calculate_pages() -> int:
    global current_pdf
    return len(current_pdf.pages)
```

### 6.3 Mocking-Punkte

File I/O und externe Dependencies mockbar machen:

```python
class PDFReader:
    def __init__(self, file_reader=None):
        self.file_reader = file_reader or default_file_reader

    def read(self, path: Path):
        return self.file_reader(path)  # Mockbar!
```

---

## 7. Performance

### 7.1 Performance-Ziele

| Operation | Ziel | Max |
|-----------|------|-----|
| Einzelne Datei (<10 MB) | < 2s | < 5s |
| Batch (10 Dateien) | < 20s | < 30s |
| Speicherverbrauch | < 300 MB | < 500 MB |

### 7.2 Performance Best Practices

#### Streaming für große Dateien
```python
# ✅ Streaming
def process_large_pdf(path: Path):
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            process_chunk(chunk)

# ❌ Alles in Memory laden
def process_large_pdf(path: Path):
    data = path.read_bytes()  # Kann 100+ MB sein!
    process(data)
```

#### Lazy Evaluation
```python
# ✅ Generator (lazy)
def get_pdf_pages(path: Path):
    with open(path, 'rb') as f:
        for page in iter_pages(f):
            yield page

# ❌ Eager (alle Seiten in Memory)
def get_pdf_pages(path: Path):
    return list(read_all_pages(path))
```

### 7.3 Profiling

Performance-kritische Funktionen profilen:

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# Your code
profiler.disable()
stats = pstats.Stats(profiler)
stats.print_stats()
```

---

## 8. Logging

### 8.1 Log-Levels

- **DEBUG**: Detaillierte Informationen für Debugging
- **INFO**: Normale Programmausführung, Fortschritt
- **WARNING**: Unerwartete Situationen, aber Fortsetzung möglich
- **ERROR**: Fehler, aber Programm läuft weiter
- **CRITICAL**: Fatale Fehler, Programm muss beendet werden

### 8.2 Logging Best Practices

```python
import logging

logger = logging.getLogger('pdftools.module_name')

# ✅ Structured logging
logger.info(f"Processing PDF: {path} (size: {size_mb:.2f} MB)")
logger.warning(f"Skipping corrupted file: {path}")
logger.error(f"Failed to process {path}: {error}", exc_info=True)

# ❌ Print statements
print(f"Processing {path}")  # Nicht verwenden!
```

### 8.3 Sensible Daten

**Niemals** sensible Daten loggen:

```python
# ❌ Passwörter loggen
logger.info(f"Decrypting PDF with password: {password}")

# ✅ Keine sensiblen Daten
logger.info(f"Decrypting PDF (password provided)")
```

---

## 9. Security

### 9.1 Input Validation

**Immer** User-Input validieren:

```python
from pdftools.core.validators import validate_pdf_path

def process_pdf(user_input: str):
    # ✅ Validierung verhindert Path Traversal
    path = validate_pdf_path(user_input, must_exist=True)
    # Weiter verarbeiten...
```

### 9.2 Path Traversal Prevention

```python
# ✅ Sicher
def save_output(user_filename: str, output_dir: Path):
    filename = Path(user_filename).name  # Nur Filename, kein Path
    output_path = output_dir / filename
    output_path = output_path.resolve()

    if not str(output_path).startswith(str(output_dir)):
        raise SecurityError("Path traversal detected")

    return output_path
```

### 9.3 Command Injection Prevention

```python
# ❌ Command Injection möglich
import os
os.system(f"ocrmypdf {user_input}")

# ✅ Sicher mit subprocess
import subprocess
subprocess.run(["ocrmypdf", user_input], check=True)
```

---

## 10. Configuration

### 10.1 Configuration Hierarchy

1. CLI Arguments (höchste Priorität)
2. Environment Variables
3. Config File (.json, .yaml)
4. Defaults (niedrigste Priorität)

### 10.2 Configuration Example

```python
from dataclasses import dataclass
import os

@dataclass
class ModuleConfig:
    verbose: bool = False
    output_dir: Path = Path("./output")
    batch_size: int = 10

    @classmethod
    def from_env(cls):
        return cls(
            verbose=os.getenv("PDFTOOLS_VERBOSE", "false").lower() == "true",
            output_dir=Path(os.getenv("PDFTOOLS_OUTPUT_DIR", "./output")),
            batch_size=int(os.getenv("PDFTOOLS_BATCH_SIZE", "10"))
        )
```

---

## 11. Code Review Checklist

Vor jedem Merge muss der Code diese Kriterien erfüllen:

### Funktionalität
- [ ] Erfüllt Requirements
- [ ] Edge Cases behandelt
- [ ] Error Handling vollständig

### Code-Qualität
- [ ] SOLID Principles befolgt
- [ ] DRY (keine Code-Duplizierung)
- [ ] Type Hints vorhanden
- [ ] Docstrings vollständig
- [ ] Clean Code (lesbar, verständlich)

### Testbarkeit
- [ ] Unit Tests geschrieben (>90% Coverage)
- [ ] Integration Tests geschrieben
- [ ] Mocking möglich (DI verwendet)

### Performance
- [ ] Performance-Ziele erfüllt
- [ ] Keine Memory Leaks
- [ ] Streaming für große Dateien

### Security
- [ ] Input Validierung
- [ ] Keine Path Traversal
- [ ] Keine sensiblen Daten in Logs

### Dokumentation
- [ ] Docstrings aktualisiert
- [ ] README aktualisiert (falls nötig)
- [ ] Design Document vorhanden

---

## 12. Anti-Patterns (Zu vermeiden!)

### 12.1 God Objects
```python
# ❌ God Object
class PDFManager:
    def read(self): pass
    def write(self): pass
    def merge(self): pass
    def split(self): pass
    def ocr(self): pass
    def encrypt(self): pass
    # ... 20 weitere Methoden
```

### 12.2 Spaghetti Code
```python
# ❌ Verschachtelte If-Statements
def process(path):
    if exists(path):
        if is_pdf(path):
            if not encrypted(path):
                if size < MAX:
                    # ... 5 weitere Levels
```

### 12.3 Magic Numbers
```python
# ❌ Magic Numbers
if size > 10485760:  # Was ist 10485760?

# ✅ Konstanten
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
if size > MAX_FILE_SIZE_BYTES:
```

### 12.4 Global State
```python
# ❌ Global State
current_pdf = None

def process():
    global current_pdf
    # ...

# ✅ Dependency Injection / Parameter Passing
def process(pdf: PDF):
    # ...
```

---

## 13. Versionierung & Breaking Changes

### 13.1 Semantic Versioning

- **Major** (X.0.0): Breaking Changes
- **Minor** (0.X.0): Neue Features (backwards compatible)
- **Patch** (0.0.X): Bug Fixes

### 13.2 Deprecation Policy

```python
import warnings

def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    return new_function()
```

---

## 14. Continuous Improvement

### 14.1 Code Metrics

Regelmäßig überprüfen:
- Code Coverage (Ziel: >85%)
- Cyclomatic Complexity (Ziel: <10 per function)
- Duplication (Ziel: <5%)

### 14.2 Tech Debt Management

- Tech Debt in Backlog tracken
- Regelmäßige Refactoring-Sessions
- "Boy Scout Rule": Code sauberer hinterlassen als vorgefunden

---

## Anhang: Referenzen

- [PEP 8 – Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Clean Code by Robert C. Martin](https://www.oreilly.com/library/view/clean-code-a/9780136083238/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
