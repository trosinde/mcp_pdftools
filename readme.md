# PDF Utilities

A collection of Python scripts for working with PDF files including OCR, merging, splitting, renaming, and more.

## Features

- **OCR Processing** - Extract text from scanned PDFs using Tesseract OCR
  - Multi-language support (German, English, French, Italian, Spanish)
  - Output formats: TXT, searchable PDF, JSON
  - CLI tool: `pdftools-ocr`
- **PDF Merging** - Merge multiple PDF files into one
  - Preserve bookmarks and metadata
  - CLI tool: `pdftools-merge`
- **PDF Splitting** - Split PDF files into individual pages
  - Range selection support
  - CLI tool: `pdftools-split`
- **PDF Renaming** - Automatically rename invoice PDFs based on extracted text patterns
- **PDF Protection** - Add password protection to PDF files
- **Text Extraction** - Extract text from PDF files
- **Thumbnail Generation** - Generate thumbnail images from PDFs
- **PDF Upload** - Upload PDF files to web services

## Prerequisites

### Docker (Required for OCR)
OCR functionality requires Docker. Install Docker for your platform:

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Add user to docker group
# Log out and back in for group changes to take effect
```

**macOS:**
```bash
brew install --cask docker
# Or download Docker Desktop from https://docker.com
```

**Windows:**
Download and install Docker Desktop from https://docker.com

Start the OCR service using Docker Compose:
```bash
docker-compose up -d ocrmypdf
```

This will automatically pull and start the `jbarlow83/ocrmypdf` image.

### Tesseract OCR Engine
Install Tesseract for text extraction:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS  
brew install tesseract

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Installation

### Option 1: Standard Python Setup

1. Clone the repository:
```bash
git clone https://github.com/trosinde/pdf.git
cd pdf
```

2. Create a virtual environment (recommended):
```bash
python -m venv pdf-env
source pdf-env/bin/activate  # Linux/macOS
# pdf-env\Scripts\activate   # Windows
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Option 2: Anaconda Setup

1. Clone the repository:
```bash
git clone https://github.com/trosinde/pdf.git
cd pdf
```

2. Create and activate conda environment:
```bash
conda create -n pdf python=3.11
conda activate pdf
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

### Bash Aliases Setup

Add these aliases to your `~/.bashrc` or `~/.bash_profile` for convenient command access:

```bash
# PDF Utilities Aliases
export PDF_TOOLS_PATH="/path/to/pdf"  # Replace with actual path

alias pdfocr='python "$PDF_TOOLS_PATH/ocrutil.py" -delete -files "$@"'
alias pdfrename='python "$PDF_TOOLS_PATH/renamepdf.py" -loglevel DEBUG -f'
alias pdfmerge='python "$PDF_TOOLS_PATH/pdfmerge.py"'

# Optional additional aliases:
# alias pdfsplit='python "$PDF_TOOLS_PATH/splitpdf.py"'
# alias pdfprotect='python "$PDF_TOOLS_PATH/protect.py"'
# alias pdftext='python "$PDF_TOOLS_PATH/pdfgettxt.py"'
# alias pdfthumbs='python "$PDF_TOOLS_PATH/thumbnails.py"'
# alias pdfupload='python "$PDF_TOOLS_PATH/uploadpdf.py"'

# Reload bash configuration
source ~/.bashrc
```

**Important:** Replace `/path/to/pdf` with the actual absolute path to this repository.

### Environment Activation

Remember to activate your environment before using the tools:

```bash
# Standard Python
source pdf-env/bin/activate

# Anaconda
conda activate pdf
```

## Usage

### OCR Processing
Extract text from scanned PDF documents using Tesseract OCR:

```bash
# Basic usage (German language, TXT output)
pdftools-ocr -f scan.pdf

# Multiple languages, searchable PDF output
pdftools-ocr -f document.pdf -l deu+eng --output-mode pdf -o searchable.pdf

# Specific pages only
pdftools-ocr -f contract.pdf --pages "1-5,10"

# JSON output for further processing
pdftools-ocr -f receipt.pdf --output-mode json -o result.json

# Verbose mode
pdftools-ocr -f scan.pdf --verbose
```

**Supported languages**: deu (German), eng (English), fra (French), ita (Italian), spa (Spanish)

**Note**: Requires Tesseract OCR to be installed (see Prerequisites section)

### PDF Renaming
Automatically rename invoice PDFs based on extracted information:

```bash
# Using alias
pdfrename invoice.pdf

# Direct command
python renamepdf.py -f invoice.pdf -config renamepdf.json
```

The script extracts company name, invoice number, order number, and date from PDFs to generate standardized filenames.

### PDF Merging
Combine multiple PDF files:

```bash
python pdfmerge.py input1.pdf input2.pdf -output merged.pdf
```

### PDF Splitting
Split PDF into individual pages:

```bash
python splitpdf.py document.pdf
```

### Text Extraction
Extract text from PDF files:

```bash
python pdfgettxt.py document.pdf
```

### PDF Protection
Add password protection:

```bash
python protect.py -input document.pdf -password mypassword
```

### Thumbnail Generation
Generate thumbnail images:

```bash
python thumbnails.py document.pdf
```

## Configuration

### PDF Renaming Configuration
The `renamepdf.json` file contains patterns for extracting information from different company invoices:

```json
{
    "COMPANY_NAME": {
        "names": ["Company Name", "COMPANY"],
        "invoice": "Invoice:\\s*(\\w+-\\d{4}-\\d{2})",
        "order": "\\b47\\d{8}\\b",
        "date": "(?:January|February|...)\\s+\\d{1,2},\\s+\\d{4}",
        "date_format": "%B %d, %Y"
    }
}
```

## Docker Services

A `docker-compose.yml` file is included for running services in containers.

## Troubleshooting

### OCR Issues
- Ensure Docker is running and ocrmypdf image is available
- Check file permissions and paths
- Use `-d` flag for debug output

### Module Not Found Errors
- Install missing dependencies: `pip install -r requirements.txt`
- Ensure you're using the correct Python environment

### File Not Found Errors
- Check file paths are correct
- Ensure files exist in the specified location
- Use absolute paths when necessary

## Contributing

Feel free to submit issues and enhancement requests!
