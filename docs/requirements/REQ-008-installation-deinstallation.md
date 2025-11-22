# Feature Requirement: Installation & De-Installation System

**ID**: REQ-008
**Version**: 1.0
**Status**: Released
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-008 v1.0
- Test Report: TEST-008 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
Ein robustes Installations- und De-Installationssystem für pdftools, das eine vollständige Python-Umgebung (virtualenv), alle Dependencies (inkl. PyPDF2, pdf2image, etc.) und eine Docker-Umgebung für OCR-Verarbeitung (ocrmypdf) automatisiert einrichtet und auf Wunsch vollständig wieder entfernt.

### 1.2 Geschäftsziel
- Nutzer können pdftools mit einem einzigen Befehl installieren (inkl. aller Dependencies)
- Docker-Umgebung für OCR wird automatisch konfiguriert und getestet
- De-Installation entfernt alle Komponenten vollständig und sauber
- Reduziert Einstiegshürde für neue Benutzer drastisch
- Vermeidet "works on my machine" Probleme durch standardisierte Umgebung

### 1.3 Betroffene Module
- [x] PDF Merge (benötigt PyPDF2)
- [x] PDF Split (benötigt PyPDF2)
- [x] Text Extraction (benötigt PyPDF2)
- [x] OCR (benötigt Docker + ocrmypdf Container)
- [x] PDF Protection (benötigt PyPDF2)
- [x] Thumbnails (benötigt pdf2image, Pillow)
- [x] Invoice Renamer (benötigt alle OCR-Dependencies)
- [x] Neues Modul: Installation/Setup System

---

## 2. Funktionale Anforderungen

### 2.1 Installation

**Als** Endbenutzer
**möchte ich** pdftools mit einem einzigen Skript installieren können
**damit** ich schnell loslegen kann ohne manuell Dependencies zu installieren

**Akzeptanzkriterien:**
1. [x] Ein Installations-Skript (`install.sh` für Linux/Mac, `install.ps1` für Windows) führt die komplette Installation durch
2. [x] Virtualenv wird automatisch erstellt (`.venv/` im Projektverzeichnis)
3. [x] Alle Python-Dependencies werden aus `requirements.txt` installiert
4. [x] Docker-Verfügbarkeit wird geprüft
5. [x] OCR Docker-Image (ocrmypdf) wird gepullt und getestet
6. [x] Test-PDFs werden generiert (`scripts/generate_test_pdfs.py`)
7. [x] Installations-Validierung wird durchgeführt (imports testen)
8. [x] Benutzer bekommt klare Erfolgsmeldung oder Fehlerdiagnose

### 2.2 Docker Setup für OCR

**Als** Entwickler/Benutzer der OCR-Funktion
**möchte ich** dass die Docker-Umgebung automatisch korrekt konfiguriert wird
**damit** OCR-Verarbeitung sofort funktioniert

**Akzeptanzkriterien:**
1. [ ] Docker ist installiert und läuft (Check)
2. [ ] OCR Docker-Image wird gepullt: `jbarlow83/ocrmypdf:latest`
3. [ ] Docker-Volume für PDF-Verarbeitung wird erstellt
4. [ ] Test-OCR-Vorgang wird durchgeführt zur Validierung
5. [ ] Fehlermeldungen bei Docker-Problemen sind klar und hilfreich
6. [ ] Docker-Compose Config ist vorhanden für erweiterte Setups
7. [ ] Dokumentation für manuelles Docker-Setup ist verfügbar

### 2.3 De-Installation

**Als** Endbenutzer
**möchte ich** pdftools vollständig deinstallieren können
**damit** keine Reste auf meinem System bleiben

**Akzeptanzkriterien:**
1. [ ] De-Installations-Skript (`uninstall.sh` / `uninstall.ps1`) vorhanden
2. [ ] Virtualenv wird gelöscht (`.venv/`)
3. [ ] Generierte Test-PDFs werden gelöscht (optional, Benutzer-wählbar)
4. [ ] Docker-Images für OCR werden optional entfernt (Benutzer-wählbar)
5. [ ] Docker-Volumes werden optional bereinigt
6. [ ] Konfigurationsdateien bleiben optional erhalten (Benutzer-Backup)
7. [ ] Bestätigungsdialog vor destruktiven Aktionen
8. [ ] Klare Rückmeldung was gelöscht wurde und was erhalten blieb

### 2.4 Validierung & Health Check

**Als** System
**möchte ich** nach Installation validieren dass alles funktioniert
**damit** Probleme sofort erkannt werden

**Akzeptanzkriterien:**
1. [ ] Health-Check-Skript (`scripts/health_check.py`) prüft Installation
2. [ ] Python-Imports werden getestet (alle Module importierbar)
3. [ ] PyPDF2 wird getestet (einfaches PDF lesen)
4. [ ] Docker-OCR wird getestet (Test-PDF durch OCR laufen lassen)
5. [ ] Test-Suite kann ausgeführt werden (`pytest`)
6. [ ] Ergebnis-Report mit allen Checks und deren Status

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- Installationszeit: < 5 Minuten (inkl. Docker-Pull)
- De-Installationszeit: < 1 Minute
- Health-Check: < 30 Sekunden
- Docker-Image-Größe: Dokumentiert und akzeptabel (< 2 GB)

### 3.2 Qualität
- Testabdeckung für Installation/De-Installation: > 80%
- Idempotenz: Wiederholte Installation überschreibt sauber
- Rollback: Bei Fehlern wird auf vorherigen Zustand zurückgesetzt
- Logging: Vollständige Log-Dateien für Debugging (`install.log`)

### 3.3 Kompatibilität
- Python-Version: >= 3.8
- Betriebssysteme:
  - Linux (Ubuntu 20.04+, Debian 11+)
  - macOS (11.0+)
  - Windows 10/11 (PowerShell 5.1+)
- Docker: >= 20.10
- Docker Compose: >= 1.29 (optional, für erweiterte Setups)

---

## 4. Technische Details

### 4.1 Abhängigkeiten

**Python Dependencies (requirements.txt)**:
- PyPDF2 >= 3.0.0
- pdf2image >= 1.16.0
- Pillow >= 9.0.0
- pytesseract >= 0.3.10 (für lokale OCR-Fallback)
- pytest >= 7.0.0
- pytest-cov >= 4.0.0
- reportlab >= 4.0.0 (für Test-PDF-Generierung)

**Docker Dependencies**:
- Docker Engine >= 20.10
- OCR Image: `jbarlow83/ocrmypdf:latest`

**System Dependencies** (müssen vorhanden sein):
- git (für Repository-Operationen)
- curl/wget (für Downloads)
- Python 3.8+ (mit venv-Modul)

### 4.2 Konfiguration

**Umgebungsvariablen** (`.env`):
```bash
PDFTOOLS_DOCKER_IMAGE=jbarlow83/ocrmypdf:latest
PDFTOOLS_VENV_PATH=.venv
PDFTOOLS_TEST_DATA_DIR=tests/test_data
PDFTOOLS_LOG_LEVEL=INFO
```

**Install Config** (`install_config.json`):
```json
{
  "install_test_pdfs": true,
  "pull_docker_images": true,
  "run_health_check": true,
  "verbose": true
}
```

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [ ] Installation-Skript-Logik isoliert testbar
- [ ] Docker-Check-Funktionen mockbar
- [ ] Virtualenv-Erstellung simulierbar
- [ ] Edge Cases: Bereits installiert, fehlende Dependencies, etc.

### 5.2 Integration Tests
- [ ] Vollständige Installation in sauberer Umgebung (CI/CD)
- [ ] De-Installation entfernt alle Komponenten
- [ ] Re-Installation nach De-Installation funktioniert
- [ ] Docker-OCR End-to-End Test

### 5.3 E2E Tests
- [ ] Installation auf frischem Ubuntu 22.04 System
- [ ] Installation auf macOS (GitHub Actions)
- [ ] Installation auf Windows 11 (PowerShell)
- [ ] Docker-OCR-Workflow von Installation bis PDF-Verarbeitung
- [ ] De-Installation und Cleanup-Verifikation

### 5.4 Test-Daten
- Benötigte Test-Umgebungen:
  - [ ] Clean Ubuntu 22.04 VM/Container
  - [ ] Clean macOS (GitHub Actions Runner)
  - [ ] Clean Windows 11 VM
  - [ ] System mit bereits existierendem Python/Docker
  - [ ] System ohne Docker (Fehlerfall)
  - [ ] System mit alter Python-Version (< 3.8, Fehlerfall)

---

## 6. Beispiele

### 6.1 Installation (Linux/Mac)

```bash
# Grundlegende Installation
./scripts/install.sh

# Installation mit Optionen
./scripts/install.sh --no-docker --no-test-pdfs

# Verbose Installation mit Log
./scripts/install.sh --verbose 2>&1 | tee install.log
```

### 6.2 Installation (Windows)

```powershell
# PowerShell Installation
.\scripts\install.ps1

# Mit Optionen
.\scripts\install.ps1 -NoDocker -NoTestPDFs

# Als Administrator (falls Docker-Setup erforderlich)
# Start-Process powershell -Verb RunAs -ArgumentList "-File .\scripts\install.ps1"
```

### 6.3 De-Installation

```bash
# Vollständige De-Installation (interaktiv)
./scripts/uninstall.sh

# Automatische De-Installation (alle löschen)
./scripts/uninstall.sh --all --no-confirm

# Nur Python-Umgebung löschen, Test-PDFs behalten
./scripts/uninstall.sh --keep-test-data --keep-docker
```

### 6.4 Health Check

```bash
# Nach Installation Health Check ausführen
python scripts/health_check.py

# Detaillierter Health Check
python scripts/health_check.py --verbose --test-docker
```

### 6.5 Docker OCR Test

```bash
# Manueller Docker-OCR-Test
docker run --rm -v $(pwd)/tests/test_data:/data \
  jbarlow83/ocrmypdf:latest \
  /data/test_no_ocr.pdf /data/test_with_ocr.pdf

# Über Health Check
python scripts/health_check.py --test-ocr
```

---

## 7. Offene Fragen

1. Soll Docker automatisch installiert werden falls nicht vorhanden? (wahrscheinlich NEIN, nur Warnung)
2. Sollen virtuelle Umgebungen auch global installiert werden können (nicht empfohlen)?
3. Wie sollen wir mit verschiedenen Docker-Backends umgehen (Docker Desktop, Podman, etc.)?
4. Sollen wir ein Upgrade-Skript bereitstellen für spätere Versionen?

---

## 8. Review

### Team Review
- [x] Requirements Engineer: ✅ APPROVED - Vollständig und klar strukturiert
- [x] Architekt: ✅ APPROVED - Modularität, Error Codes, State Management beachten
- [x] Python Entwickler: ✅ APPROVED - Implementierbar in 2-3 Tagen
- [x] Tester: ✅ APPROVED - Testbarkeit gut durchdacht, E2E auf allen OS
- [x] DevOps: ✅ APPROVED - Docker-Image pinnen, CI/CD ready machen

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

**Freigegeben durch**: [Pending Team Review]
**Datum**: [TBD]
**Nächster Schritt**: Team Review → Design-Phase
