# Installation Guide

This guide will help you install and configure MCP PDF Tools on your system.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Method 1: pip Install (Recommended)](#method-1-pip-install-recommended)
  - [Method 2: Development Install](#method-2-development-install)
- [Dependencies](#dependencies)
- [OCR Setup (Optional)](#ocr-setup-optional)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 512 MB minimum, 2 GB recommended
- **Disk Space**: 100 MB for installation + space for PDF processing

### Recommended Requirements
- **Python**: 3.10 or higher
- **RAM**: 4 GB or more
- **Disk Space**: 1 GB or more

---

## Installation Methods

### Method 1: pip Install (Recommended)

This is the recommended method for end users.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/mcp_pdftools.git
cd mcp_pdftools
```

#### Step 2: Create Virtual Environment (Recommended)

**Linux/macOS:**
```bash
python3 -m venv pdf-env
source pdf-env/bin/activate
```

**Windows:**
```bash
python -m venv pdf-env
pdf-env\Scripts\activate
```

#### Step 3: Install Package

```bash
pip install -e .
```

This installs the package in editable mode and makes all CLI commands available:
- `pdfmerge`
- `pdfsplit`
- `ocrutil`

#### Step 4: Verify Installation

```bash
pdfmerge --version
pdfsplit --version
ocrutil --help
```

---

### Method 2: Development Install

For developers who want to contribute or customize the tools.

#### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/mcp_pdftools.git
cd mcp_pdftools
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
.\venv\Scripts\activate   # Windows
```

#### Step 3: Install Dependencies

```bash
# Install runtime dependencies
pip install -r requirements.txt

# Install package in development mode
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

#### Step 4: Generate Test PDFs (Optional)

```bash
python scripts/generate_test_pdfs.py --all
```

---

## Dependencies

The following Python packages will be installed automatically:

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyPDF2 | 3.0.1 | PDF merging and manipulation |
| pdfrw | 0.4 | PDF splitting operations |
| PyMuPDF | 1.23.8 | PDF rendering and processing |
| Pillow | 10.0.0 | Image processing |
| reportlab | 4.0.4 | PDF generation |

### OCR Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytesseract | 0.3.10 | Python wrapper for Tesseract OCR |
| pdf2image | 1.16.3 | Convert PDF pages to images |

### Utility Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| requests | 2.31.0 | HTTP requests |
| glob2 | 0.7 | Enhanced file pattern matching |

---

## OCR Setup (Optional)

OCR functionality requires **Tesseract OCR** to be installed on your system.

### Linux (Ubuntu/Debian)

```bash
# Install Tesseract OCR engine
sudo apt-get update
sudo apt-get install tesseract-ocr

# Install language packs (optional)
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-eng  # English
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-ita  # Italian
sudo apt-get install tesseract-ocr-spa  # Spanish

# Verify installation
tesseract --version
tesseract --list-langs
```

### macOS

```bash
# Install using Homebrew
brew install tesseract

# Install language packs
brew install tesseract-lang

# Verify installation
tesseract --version
tesseract --list-langs
```

### Windows

1. Download the installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer
3. During installation, select the language packs you need
4. Add Tesseract to your system PATH:
   - Default path: `C:\Program Files\Tesseract-OCR`
   - Add to System Environment Variables

5. Verify installation:
```bash
tesseract --version
tesseract --list-langs
```

### Docker Alternative (All Platforms)

If you prefer using Docker for OCR:

```bash
# Start OCR service using Docker Compose
docker-compose up -d ocrmypdf

# Verify Docker container is running
docker ps
```

The `docker-compose.yml` file in the repository configures the OCR service automatically.

---

## Verification

### Test Basic Installation

```bash
# Check if commands are available
pdfmerge --version
pdfsplit --version
ocrutil --help

# Check Python can import the package
python -c "import pdftools; print('Installation successful!')"
```

### Test PDF Merge

Create two simple test files and merge them:

```bash
# Navigate to examples directory
cd examples

# Merge example PDFs (if available)
pdfmerge -f "file1.pdf,file2.pdf" -o test_merged.pdf
```

### Test PDF Split

```bash
# Split a PDF into individual pages
pdfsplit -i document.pdf -o ./output/
```

### Test OCR (if installed)

```bash
# Test OCR on a scanned document
ocrutil -f scanned.pdf -l eng -v
```

---

## Troubleshooting

### Issue: Command not found (pdfmerge, pdfsplit, etc.)

**Cause**: The package is not properly installed or the virtual environment is not activated.

**Solution**:
```bash
# Activate your virtual environment
source pdf-env/bin/activate  # Linux/macOS
# or
pdf-env\Scripts\activate     # Windows

# Reinstall the package
pip install -e .
```

### Issue: ModuleNotFoundError

**Cause**: Missing dependencies.

**Solution**:
```bash
# Reinstall all dependencies
pip install -r requirements.txt

# If still failing, upgrade pip
pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Permission denied errors

**Cause**: Insufficient file permissions.

**Solution**:

**Linux/macOS**:
```bash
# Make sure you have write permissions
chmod +w /path/to/output/directory

# Or run without sudo (recommended - use virtual environment)
```

**Windows**:
- Run Command Prompt/PowerShell as Administrator
- Or change folder permissions in Properties

### Issue: Tesseract not found

**Cause**: Tesseract OCR is not installed or not in PATH.

**Solution**:

1. Verify Tesseract is installed:
   ```bash
   tesseract --version
   ```

2. If not found, install Tesseract (see [OCR Setup](#ocr-setup-optional))

3. **Windows**: Add Tesseract to PATH:
   - Open System Properties > Environment Variables
   - Edit PATH variable
   - Add: `C:\Program Files\Tesseract-OCR`

### Issue: Language pack not available

**Error**: `LanguageNotAvailableError: Language 'deu' not available`

**Solution**:

**Linux**:
```bash
sudo apt-get install tesseract-ocr-deu
```

**macOS**:
```bash
brew install tesseract-lang
```

**Windows**:
- Re-run Tesseract installer
- Select additional language packs during installation

### Issue: PDF file is corrupted

**Cause**: The PDF file may be damaged or not a valid PDF.

**Solution**:
```bash
# Try opening the PDF in a PDF reader first to verify it's valid
# Try using --skip-on-error flag
pdfmerge -f "file1.pdf,corrupted.pdf,file3.pdf" --skip-on-error -o output.pdf
```

### Issue: Out of memory errors

**Cause**: Processing very large PDF files.

**Solution**:
- Close other applications to free up RAM
- Process PDFs in smaller batches
- Upgrade system RAM if processing large PDFs frequently

### Issue: Slow performance

**Cause**: Large PDF files or many files being processed.

**Solutions**:
- Use SSD instead of HDD for faster I/O
- Process files in smaller batches
- Use `--verbose` flag to monitor progress
- Close unnecessary applications

---

## Platform-Specific Notes

### Linux
- Use package manager for system dependencies
- Virtual environment recommended
- Check file permissions with `ls -l`

### macOS
- Install Homebrew first: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- Use Homebrew for Tesseract: `brew install tesseract`
- Virtual environment recommended

### Windows
- Use PowerShell or Command Prompt
- Install Python from [python.org](https://www.python.org)
- Add Python and Tesseract to PATH
- Consider using Git Bash for Unix-like commands

---

## Uninstallation

To remove MCP PDF Tools:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf pdf-env  # Linux/macOS
# or
rmdir /s pdf-env  # Windows

# Uninstall package
pip uninstall mcp-pdftools

# Remove repository (if desired)
cd ..
rm -rf mcp_pdftools
```

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review tool-specific documentation in `docs/tools/`
3. Search existing GitHub issues
4. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Steps to reproduce the problem

---

## Next Steps

After successful installation:

1. Read the [README.md](README.md) for project overview
2. Explore tool-specific documentation in `docs/tools/`:
   - [PDF Merge](docs/tools/pdfmerge.md)
   - [PDF Split](docs/tools/pdfsplit.md)
   - [OCR Processing](docs/tools/ocrutil.md)
3. Try the examples in the `examples/` directory
4. Review the [Development Process](docs/DEVELOPMENT_PROCESS.md) if contributing
