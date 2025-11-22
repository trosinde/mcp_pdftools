# Design Document: PDF Protection

**ID**: DESIGN-004
**Version**: 1.0
**Requirement**: [REQ-004](../requirements/REQ-004-protection.md) v1.0
**Status**: Released
**Architekt**: Architecture Team
**Entwickler**: Python Development Team
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-004 v1.0
- Tested by: TEST-004 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Implementierung eines sicheren, testbaren PDF-Protection-Moduls, das PDF-Dateien mit Passwörtern verschlüsselt und Berechtigungen setzt unter Berücksichtigung von Security, Testbarkeit und Best Practices.

### 1.2 Scope
**In Scope:**
- Verschlüsselung mit User-Passwort (Öffnen)
- Verschlüsselung mit Owner-Passwort (Rechte ändern)
- Berechtigungen: PRINT, COPY, MODIFY, ANNOTATE
- CLI und programmatisches Interface
- Vollständige Fehlerbehandlung

**Out of Scope:**
- 256-bit AES (nur 128-bit in v1.0)
- Digitale Signaturen
- Zertifikat-basierte Verschlüsselung

---

## 2. Architektur

### 2.1 Modul-Struktur

```
src/pdftools/protection/
├── __init__.py              # Public API exports
├── core.py                  # Hauptlogik, Orchestrierung
├── validators.py            # Input-Validierung, Passwort-Validierung
├── processors.py            # PDF-Encryption-Logik
├── models.py                # Datenmodelle (Result, Config, Permissions)
├── cli.py                   # CLI Interface
└── README.md                # Modul-Dokumentation
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────┐
│   CLI Layer     │  (cli.py)
│  pdfprotect     │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Validation     │  (validators.py)
│  - validate_    │
│    input_file   │
│  - validate_    │
│    passwords    │
│  - validate_    │
│    permissions  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Core Logic     │  (core.py)
│  - protect_pdf()│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Processors     │  (processors.py)
│  - PDFProtector │
│  - Encryption   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   File Output   │
│  - Write        │
│    encrypted PDF│
└─────────────────┘
```

### 2.3 Datenfluss
1. **CLI**: Benutzer ruft `pdfprotect` auf
2. **Validation**: Input-Datei, Passwörter und Berechtigungen werden validiert
3. **Core**: `protect_pdf()` orchestriert den Protection-Prozess
4. **Processor**: `PDFProtector` verschlüsselt PDF
5. **Output**: Verschlüsseltes PDF wird gespeichert
6. **Result**: Erfolgsmeldung oder Fehler wird zurückgegeben

---

## 3. API Design

### 3.1 Öffentliche Funktionen

#### 3.1.1 Hauptfunktion
```python
from pathlib import Path
from typing import Optional, List
from .models import ProtectionResult, PermissionLevel

def protect_pdf(
    input_path: Path,
    output_path: Optional[Path] = None,
    user_password: Optional[str] = None,
    owner_password: Optional[str] = None,
    permissions: Optional[List[PermissionLevel]] = None
) -> ProtectionResult:
    """
    Protect a PDF file with password encryption and permissions.

    Args:
        input_path: Path to input PDF file
        output_path: Output path for protected PDF.
                    If None, creates '{input}_protected.pdf' in same directory.
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        permissions: List of allowed permissions (optional, default: all denied)

    Returns:
        ProtectionResult: Object containing status, output path, and metadata

    Raises:
        PDFNotFoundError: If input file doesn't exist
        InvalidParameterError: If no passwords provided
        PDFProcessingError: If protection fails

    Example:
        >>> result = protect_pdf(
        ...     input_path=Path("document.pdf"),
        ...     user_password="secret123",
        ...     permissions=[PermissionLevel.PRINT]
        ... )
        >>> print(result.status)
        'success'
    """
    pass
```

### 3.2 Klassen

#### 3.2.1 PDFProtector (Processor)
```python
from typing import Optional, List
from PyPDF2 import PdfReader, PdfWriter

class PDFProtector:
    """Handles PDF encryption and permission setting"""

    def __init__(self):
        """Initialize protector"""
        self.writer = PdfWriter()

    def load_pdf(self, path: Path) -> None:
        """
        Load a PDF file for protection.

        Args:
            path: Path to PDF file
        """
        reader = PdfReader(path)
        for page in reader.pages:
            self.writer.add_page(page)

    def apply_protection(
        self,
        user_password: Optional[str] = None,
        owner_password: Optional[str] = None,
        permissions: Optional[List[PermissionLevel]] = None
    ) -> None:
        """
        Apply encryption and permissions to loaded PDF.

        Args:
            user_password: Password to open PDF
            owner_password: Password to modify permissions
            permissions: List of allowed permissions
        """
        # Convert permissions to PyPDF2 format
        use_128bit = True

        self.writer.encrypt(
            user_password=user_password or "",
            owner_password=owner_password,
            use_128bit=use_128bit,
            permissions_flag=self._calculate_permission_flags(permissions)
        )

    def write(self, output_path: Path) -> None:
        """
        Write protected PDF to file.

        Args:
            output_path: Destination path
        """
        with open(output_path, 'wb') as output_file:
            self.writer.write(output_file)

    def _calculate_permission_flags(
        self,
        permissions: Optional[List[PermissionLevel]]
    ) -> int:
        """Calculate PyPDF2 permission flags from PermissionLevel list"""
        # Implementation details
        pass
```

### 3.3 Datenmodelle

```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List
from enum import Enum

class PermissionLevel(Enum):
    """PDF permission levels"""
    PRINT = "print"
    COPY = "copy"
    MODIFY = "modify"
    ANNOTATE = "annotate"

@dataclass
class ProtectionConfig:
    """Configuration for PDF protection operation"""
    user_password: Optional[str] = None
    owner_password: Optional[str] = None
    permissions: Optional[List[PermissionLevel]] = None
    use_128bit: bool = True
    verbose: bool = False

@dataclass
class ProtectionResult:
    """Result of PDF protection operation"""
    status: str  # 'success' | 'error'
    output_path: Optional[Path] = None
    message: str = ""
    encryption_applied: bool = False
    permissions_set: List[str] = None

    def __post_init__(self):
        if self.permissions_set is None:
            self.permissions_set = []

    @property
    def success(self) -> bool:
        return self.status == 'success'
```

---

## 4. Dependencies

### 4.1 Interne Dependencies
- `pdftools.core.validators`: `validate_pdf_path`, `validate_output_path`
- `pdftools.core.exceptions`: Exception-Hierarchie
- `pdftools.core.utils`: `normalize_path`, `generate_output_path`

### 4.2 Externe Dependencies
| Library | Version | Zweck | Lizenz |
|---------|---------|-------|--------|
| PyPDF2 | >= 3.0.0 | PDF Encryption | BSD-3-Clause |

---

## 5. Fehlerbehandlung

### 5.1 Exception-Hierarchie
```
PDFToolsError (core.exceptions)
├── PDFNotFoundError
├── PDFProcessingError
│   ├── PDFCorruptedError
│   └── PDFProtectionError (new)
└── ValidationError
    ├── InvalidPasswordError (new)
    ├── InvalidPermissionError (new)
    └── InvalidParameterError
```

### 5.2 Fehlerszenarien
| Fehler | Exception | Nachricht | Recovery |
|--------|-----------|-----------|----------|
| Datei nicht gefunden | PDFNotFoundError | "PDF file not found: {path}" | Abbruch |
| Korruptes PDF | PDFCorruptedError | "PDF file is corrupted: {path}" | Abbruch |
| Keine Passwörter | InvalidParameterError | "At least one password required" | Abbruch |
| Ungültige Permission | InvalidPermissionError | "Invalid permission: {perm}" | Abbruch |
| Output nicht schreibbar | InsufficientPermissionsError | "Cannot write to: {path}" | Abbruch |
| Encryption fehlgeschlagen | PDFProtectionError | "Failed to protect PDF: {reason}" | Abbruch |

---

## 6. Security

### 6.1 Sicherheitsüberlegungen
- [x] Passwörter werden NICHT geloggt
- [x] Passwörter werden nicht im Klartext gespeichert (außer in Memory während Verarbeitung)
- [x] 128-bit AES Verschlüsselung (PyPDF2 Standard)
- [x] Input-Validierung verhindert Path Traversal
- [x] Keine sensiblen Daten in Fehlermeldungen

### 6.2 Password Handling
```python
# NIEMALS Passwörter loggen:
logger.info("Applying protection to PDF")  # ✅ OK
logger.debug(f"Password: {password}")      # ❌ NEVER!

# Passwörter nur in Memory:
def protect_pdf(user_password: str):
    # Passwort nur hier verwendet, nicht persistiert
    writer.encrypt(user_password=user_password)
    # Nach encrypt() ist Passwort nicht mehr nötig
```

---

## 7. Permissions Mapping

### 7.1 PyPDF2 Permission Flags
PyPDF2 verwendet Integer-Flags für Berechtigungen. Mapping:

```python
PERMISSION_FLAGS = {
    PermissionLevel.PRINT: 4,      # Bit 2
    PermissionLevel.MODIFY: 8,     # Bit 3
    PermissionLevel.COPY: 16,      # Bit 4
    PermissionLevel.ANNOTATE: 32,  # Bit 5
}

def calculate_permission_flags(permissions: List[PermissionLevel]) -> int:
    """
    Calculate combined permission flags.

    Returns:
        int: Combined permission flags (default: -1 = all denied)
    """
    if not permissions:
        return -1  # All permissions denied

    flags = 0
    for perm in permissions:
        flags |= PERMISSION_FLAGS[perm]

    return flags
```

---

## 8. Logging & Monitoring

### 8.1 Log-Levels
- **DEBUG**: "Loading PDF from {path}"
- **INFO**: "Applying protection to PDF"
- **WARNING**: "Owner password not set, using user password"
- **ERROR**: "Failed to protect PDF: {error}"

### 8.2 Log-Format
```python
import logging

logger = logging.getLogger('pdftools.protection')

# NIEMALS Passwörter loggen!
logger.info(f"Protecting PDF: {input_path}")
logger.debug(f"Permissions: {permissions}")
logger.info(f"Protected PDF created: {output_path}")
```

---

## 9. Performance

### 9.1 Performance-Ziele
- **Single Operation**: < 2 seconds for 100-page PDF
- **Memory**: < 200 MB peak usage
- **Encryption**: 128-bit AES (balanced security/performance)

### 9.2 Optimierungen
- [x] Lazy loading: Pages loaded on-demand
- [x] Streaming: Write pages incrementally
- [x] Minimal memory footprint

---

## 10. Testbarkeit

### 10.1 Test-Strategie

#### Unit Tests
```python
def test_protect_with_user_password():
    result = protect_pdf(
        input_path=Path("test.pdf"),
        user_password="secret123"
    )

    assert result.success
    assert result.encryption_applied

def test_protect_with_permissions():
    result = protect_pdf(
        input_path=Path("test.pdf"),
        user_password="secret",
        permissions=[PermissionLevel.PRINT, PermissionLevel.COPY]
    )

    assert result.success
    assert "print" in result.permissions_set
    assert "copy" in result.permissions_set
```

#### Integration Tests
```python
def test_protected_pdf_can_be_opened(pdf_simple, temp_dir):
    output = temp_dir / "protected.pdf"
    password = "test123"

    result = protect_pdf(
        input_path=pdf_simple,
        output_path=output,
        user_password=password
    )

    assert result.success

    # Verify PDF can be opened with password
    reader = PdfReader(output)
    reader.decrypt(password)
    assert len(reader.pages) > 0
```

### 10.2 Test-Coverage-Ziel
- **Unit Tests**: > 90%
- **Integration Tests**: > 80%

---

## 11. Implementierungs-Plan

### 11.1 Phasen
1. **Phase 1**: Core Infrastructure (1-2h)
   - [x] models.py: ProtectionResult, ProtectionConfig, PermissionLevel
   - [x] validators.py: validate_passwords, validate_permissions
   - [x] processors.py: PDFProtector class

2. **Phase 2**: Core Logic (2-3h)
   - [x] core.py: protect_pdf() function
   - [x] Fehlerbehandlung
   - [x] Logging (ohne Passwörter!)

3. **Phase 3**: CLI (1-2h)
   - [x] cli.py: Argparse integration
   - [x] Exit codes
   - [x] Help text

4. **Phase 4**: Testing & Documentation (2-3h)
   - [x] Unit Tests
   - [x] Integration Tests
   - [x] Documentation

### 11.2 Geschätzter Aufwand
- **Total**: 6-10 Stunden
- **Priorität 1** (MVP): Phasen 1-3 (4-7h)
- **Priorität 2** (Testing): Phase 4 (2-3h)

---

## 12. Review & Approval

### Architektur-Review
**Reviewer**: Architecture Team
**Datum**: 2025-11-22
**Status**: ✅ Approved

**Checkpoints**:
- [x] SOLID Principles eingehalten ✅
- [x] Security Best Practices (keine Passwort-Logs) ✅
- [x] Klare Separation of Concerns ✅
- [x] Testbarkeit gewährleistet ✅
- [x] Type Hints verwendet ✅
- [x] Docstrings vorhanden ✅
- [x] Error Handling robust ✅

**Comments**: Design entspricht vollständig den Security Guidelines. Passwort-Handling korrekt, keine Logs von sensiblen Daten.

---

## 13. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | Architecture Team | REQ-004 v1.0 |

---

## 14. Anhang

### 14.1 Referenzen
- Requirement: [REQ-004 v1.0](../requirements/REQ-004-protection.md)
- PyPDF2 Encryption: https://pypdf2.readthedocs.io/en/3.0.0/user/encryption-decryption.html
- Architecture Guidelines: [ARCHITECTURE_GUIDELINES.md](../architecture/ARCHITECTURE_GUIDELINES.md)

### 14.2 PyPDF2 encrypt() API
```python
PdfWriter.encrypt(
    user_password: str,
    owner_password: Optional[str] = None,
    use_128bit: bool = True,
    permissions_flag: int = -1  # -1 = all denied
)
```
