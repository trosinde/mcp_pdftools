# PDF Utilities

A collection of Python scripts for working with PDF files including OCR, merging, splitting, renaming, and more.

## Features

- **OCR Processing** (`ocrutil.py`) - Add OCR to PDF files using Docker and ocrmypdf
- **PDF Renaming** (`renamepdf.py`) - Automatically rename invoice PDFs based on extracted text patterns
- **PDF Merging** (`pdfmerge.py`) - Merge multiple PDF files into one
- **PDF Splitting** (`splitpdf.py`) - Split PDF files into individual pages
- **PDF Protection** (`protect.py`) - Add password protection to PDF files
- **Text Extraction** (`pdfgettxt.py`) - Extract text from PDF files
- **Thumbnail Generation** (`thumbnails.py`) - Generate thumbnail images from PDFs
- **PDF Upload** (`uploadpdf.py`) - Upload PDF files to web services

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
Add OCR to PDF files and optionally delete originals:

```bash
# Using alias
pdfocr document.pdf

# Direct command
python ocrutil.py -files document.pdf -delete
python ocrutil.py -path "*.pdf"  # Process all PDFs in directory
```

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
Protect PDF files with password encryption and permissions:

```bash
# Protect with user password only
pdfprotect -i document.pdf -u secret123

# Protect with user and owner passwords
pdfprotect -i contract.pdf -u open123 -w admin456

# Allow specific permissions (printing and copying)
pdfprotect -i report.pdf -u read123 -p print,copy

# Custom output path
pdfprotect -i invoice.pdf -o secure_invoice.pdf -u pass123

# Verbose output
pdfprotect -i document.pdf -u secret --verbose
```

Valid permissions: `print`, `copy`, `modify`, `annotate`

### Thumbnail Generation
Generate thumbnail preview images from PDF pages:

```bash
# Basic usage (all pages, medium size, PNG format)
pdfthumbnails -f document.pdf

# Custom size and format
pdfthumbnails -f report.pdf -s large -F jpg -o ./previews

# Specific pages only
pdfthumbnails -f manual.pdf -p "1,5,10-15" -s small

# Custom dimensions
pdfthumbnails -f catalog.pdf -s 800x600 -F jpg -q 95

# Verbose output
pdfthumbnails -f book.pdf --verbose
```

**Thumbnail Sizes:**
- `small`: 150x150 pixels
- `medium`: 300x300 pixels (default)
- `large`: 600x600 pixels
- `WxH`: Custom size (e.g., `800x600`)

**Output Formats:**
- `png`: PNG format, lossless (default)
- `jpg`: JPEG format, lossy with quality control (1-100)

**Note:** Aspect ratio is always preserved. Images are scaled to fit within the specified size without cropping.

**Dependencies:**
- `pdf2image`: PDF to image conversion
- `Pillow`: Image processing
- `poppler-utils`: System dependency (required by pdf2image)

Install system dependencies:
```bash
# Ubuntu/Debian
sudo apt-get install poppler-utils

# macOS
brew install poppler

# Windows
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
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
