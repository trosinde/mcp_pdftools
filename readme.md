# MCP PDF Tools

A professional, modular PDF processing suite with command-line tools for merging, splitting, OCR, and more.

## Overview

MCP PDF Tools is a comprehensive collection of Python-based utilities for PDF document manipulation. Each tool is designed to handle specific PDF processing tasks with professional-grade reliability and performance.

### Current Release Status

| Tool | Status | Version | Documentation |
|------|--------|---------|---------------|
| **pdfmerge** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfmerge.md) |
| **pdfsplit** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfsplit.md) |
| **ocrutil** | ✅ Released | 1.0.0 | [Documentation](docs/tools/ocrutil.md) |
| **pdfgettxt** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfgettxt.md) |
| **pdfprotect** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfprotect.md) |
| **pdfthumbnails** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfthumbnails.md) |
| **pdfrename** | ✅ Released | 1.0.0 | [Documentation](docs/tools/pdfrename.md) |

---

## Features

- **PDF Merging** - Combine multiple PDF files into one document
- **PDF Splitting** - Split PDF files by pages or page ranges
- **Invoice Renaming** - Intelligently rename invoice PDFs based on extracted data (invoice #, date, vendor)
- **OCR Processing** - Add OCR to PDF files using Docker and ocrmypdf
- **PDF Protection** - Add password protection to PDF files
- **Text Extraction** - Extract text content from PDF files
- **Thumbnail Generation** - Generate thumbnail images from PDFs
- **CLI Tools** - Comprehensive command-line interface for all features

#### PDF Merge
Combine multiple PDF files into a single document with preserved bookmarks and metadata.

**Key Features**:
- Merge 2+ PDF files in specified order
- Preserve or skip bookmarks
- Handle corrupted files gracefully
- Performance: < 5s for 10 PDFs @ 10 pages each
- Detailed progress reporting

**Quick Start**:
```bash
pdfmerge -f "file1.pdf,file2.pdf,file3.pdf" -o merged.pdf
```

**[Full Documentation](docs/tools/pdfmerge.md)**

---

#### PDF Split
Split PDF files into multiple parts using various splitting strategies.

**Key Features**:
- **4 Split Modes**: PAGES, RANGES, PARTS, SPECIFIC_PAGES
- Split into individual pages
- Extract specific page ranges
- Divide into equal parts
- Extract specific page numbers
- Custom output naming

**Quick Start**:
```bash
# Split into individual pages
pdfsplit -i document.pdf -o ./pages/

# Split by ranges
pdfsplit -i book.pdf -m ranges -r "1-10,50-75,100-125" -o ./chapters/

# Split into N parts
pdfsplit -i report.pdf -m parts -p 5 -o ./parts/

# Extract specific pages
pdfsplit -i presentation.pdf -m specific --pages "1,5,10,20" -o ./selected/
```

**[Full Documentation](docs/tools/pdfsplit.md)**

---

#### OCR Utility
Extract text from scanned PDF documents using Tesseract OCR.

**Key Features**:
- Multi-language support (German, English, French, Italian, Spanish)
- 3 output formats: TXT, searchable PDF, JSON
- Page selection (all or specific ranges)
- Quality metrics (confidence scores, word counts)
- Adjustable DPI for quality control
- Performance monitoring

**Quick Start**:
```bash
# Basic OCR (German, TXT output)
ocrutil -f scan.pdf

# Multi-language, searchable PDF
ocrutil -f document.pdf -l deu+eng --output-mode pdf -o searchable.pdf

# Specific pages, JSON output
ocrutil -f contract.pdf --pages "1-5,10" --output-mode json -o data.json
```

**Requirements**: Tesseract OCR must be installed (see [Installation](#installation))

**[Full Documentation](docs/tools/ocrutil.md)**

---

## Installation

> **💡 Einfache Installation:** Für Linux/macOS einfach `./install.sh` ausführen - fertig!
>
> Der Installer installiert automatisch Python, Docker, Git und alle Abhängigkeiten.

### 🚀 Automated Installation (Recommended)

**Linux/macOS** - Nur 3 Befehle:
```bash
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools
./install.sh
```

**Das war's!** Der Installer erledigt den Rest automatisch.

The installer automatically:
- ✅ Detects your platform (Ubuntu, Debian, Fedora, macOS)
- ✅ Installs Python 3.8+ (if not present)
- ✅ Installs Docker (if not present)
- ✅ Installs Git (if not present)
- ✅ Creates Python virtual environment (venv)
- ✅ Installs all dependencies
- ✅ Runs functional tests
- ✅ Configures MCP server (optional, for AI tools)

**Installation takes 5-15 minutes** depending on what's already installed.

**Windows**:
```batch
# Clone repository
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools

# Follow manual instructions
install.bat
```

### Manual Installation (nur falls ./install.sh nicht funktioniert)

<details>
<summary>Klicken Sie hier für manuelle Installations-Schritte</summary>

```bash
# Clone repository
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install package
pip install -r requirements.txt
pip install -e .
```

</details>

### Verify Installation

```bash
pdfmerge --version
pdfsplit --version
ocrutil --help
pdfgettxt --version
pdfprotect --version
pdfthumbnails --version
pdfrename --version
```

All 7 tools should respond with version information.

### Optional: OCR Setup

The automated installer includes Docker for OCR. For native Tesseract:

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-deu
```

**macOS**:
```bash
brew install tesseract tesseract-lang
```

**Windows**:
Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

### 📚 Complete Installation Guide

**[Complete Installation Guide](docs/INSTALLATION.md)** - Detailed instructions, troubleshooting, and platform-specific notes

---

## Usage Examples

### PDF Merge Examples

**Basic Merge**:
```bash
pdfmerge -f "report_part1.pdf,report_part2.pdf" -o complete_report.pdf
```

**Merge Multiple Files**:
```bash
pdfmerge -f "intro.pdf,ch1.pdf,ch2.pdf,ch3.pdf,conclusion.pdf" -o book.pdf
```

**Skip Corrupted Files**:
```bash
pdfmerge -f "file1.pdf,corrupted.pdf,file3.pdf" --skip-on-error -o output.pdf
```

**Merge Without Bookmarks**:
```bash
pdfmerge -f "doc1.pdf,doc2.pdf" --no-bookmarks -o merged.pdf
```

---

### PDF Split Examples

**Split into Individual Pages**:
```bash
pdfsplit -i document.pdf -o ./pages/
```

**Split by Page Ranges**:
```bash
pdfsplit -i book.pdf -m ranges -r "1-10,50-75,100-125" -o ./chapters/
```

**Split into Equal Parts**:
```bash
pdfsplit -i report.pdf -m parts -p 5 -o ./parts/
```

**Extract Specific Pages**:
```bash
pdfsplit -i presentation.pdf -m specific --pages "1,5,10,20" -o ./selected/
```

---

### OCR Examples

**Basic OCR (German)**:
```bash
ocrutil -f rechnung.pdf
# Output: rechnung_ocr.txt
```

**English Document to Searchable PDF**:
```bash
ocrutil -f scan.pdf -l eng --output-mode pdf -o searchable.pdf
```

**Multi-language Processing**:
```bash
ocrutil -f contract.pdf -l deu+eng --output-mode pdf -o contract_searchable.pdf
```

**JSON Output for Processing**:
```bash
ocrutil -f invoice.pdf --output-mode json -o invoice_data.json
```

**High-Quality OCR (600 DPI)**:
```bash
ocrutil -f contract.pdf --dpi 600 -l eng -o contract.txt
```

---

## Common Workflows

### Workflow 1: Archive Scanned Documents

```bash
# 1. OCR scanned documents to make them searchable
ocrutil -f scan1.pdf -l deu --output-mode pdf -o scan1_ocr.pdf
ocrutil -f scan2.pdf -l deu --output-mode pdf -o scan2_ocr.pdf

# 2. Merge into single archive
pdfmerge -f "scan1_ocr.pdf,scan2_ocr.pdf" -o archive_2024_searchable.pdf
```

### Workflow 2: Extract and Process Specific Pages

```bash
# 1. Extract specific pages
pdfsplit -i large.pdf -m specific --pages "1,5,10,15,20" -o ./selected/

# 2. OCR extracted pages
for file in ./selected/*.pdf; do
    ocrutil -f "$file" -l eng --output-mode pdf -o "${file%.pdf}_ocr.pdf"
done

# 3. Merge processed pages
pdfmerge -f "./selected/*_ocr.pdf" -o processed_pages.pdf
```

### Invoice PDF Renaming
Intelligently rename invoice PDFs based on extracted data (invoice number, date, vendor):

```bash
# Rename single invoice with default template
pdfrename -f invoice.pdf

# Custom template
pdfrename -f invoice.pdf -t "{date}_{vendor}_{invoice_nr}.pdf"

# Batch processing with dry-run
pdfrename -f invoices/*.pdf -d

# Custom patterns from JSON file
pdfrename -f invoice.pdf -p patterns.json -o renamed/

# Verbose output
pdfrename -f invoice.pdf --verbose
```

**Template placeholders:**
- `{vendor}` - Vendor/supplier name
- `{invoice_nr}` - Invoice number
- `{date}` - Full date (YYYY-MM-DD)
- `{year}`, `{month}`, `{day}` - Individual date components

The tool extracts invoice data using regex patterns and supports custom patterns for different invoice formats.

### PDF Merging
Combine multiple PDF files:

```bash
# 1. Split by chapters (page ranges)
pdfsplit -i book_scan.pdf -m ranges -r "1-50,51-100,101-150,151-200" -o ./chapters/

# 2. OCR each chapter
for chapter in ./chapters/*.pdf; do
    ocrutil -f "$chapter" -l eng --output-mode pdf -o "${chapter%.pdf}_ocr.pdf" -v
done

# 3. Merge into complete searchable book
pdfmerge -f "./chapters/*_ocr.pdf" -o book_complete_searchable.pdf
```

---

## Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: 2 GB minimum, 4 GB recommended
- **Disk Space**: 100 MB for installation

### Python Dependencies

Automatically installed with `pip install -e .`:

| Package | Version | Purpose |
|---------|---------|---------|
| PyPDF2 | 3.0.1 | PDF merging and manipulation |
| pdfrw | 0.4 | PDF splitting operations |
| PyMuPDF | 1.23.8 | PDF rendering |
| pytesseract | 0.3.10 | OCR wrapper for Tesseract |
| pdf2image | 1.16.3 | PDF to image conversion |
| Pillow | 10.0.0 | Image processing |
| reportlab | 4.0.4 | PDF generation |

### External Dependencies (OCR Only)
- **Tesseract OCR**: System-level installation required
  - See [INSTALLATION.md](docs/INSTALLATION.md) for platform-specific instructions

---

## Documentation

### User Documentation
- **[Installation Guide](docs/INSTALLATION.md)** - Complete setup instructions
- **[PDF Merge](docs/tools/pdfmerge.md)** - Merge tool documentation
- **[PDF Split](docs/tools/pdfsplit.md)** - Split tool documentation
- **[OCR Utility](docs/tools/ocrutil.md)** - OCR tool documentation
- **[Text Extraction](docs/tools/pdfgettxt.md)** - Text extraction with 4 modes
- **[PDF Protection](docs/tools/pdfprotect.md)** - Password & permission protection
- **[Thumbnail Generation](docs/tools/pdfthumbnails.md)** - Thumbnail image generation
- **[Invoice Renaming](docs/tools/pdfrename.md)** - Intelligent invoice renaming

### Developer Documentation
- **[Development Process](docs/DEVELOPMENT_PROCESS.md)** - Team workflow and guidelines
- **[Traceability Matrix](docs/TRACEABILITY_MATRIX.md)** - Requirements tracking
- **[Architecture Guidelines](docs/architecture/ARCHITECTURE_GUIDELINES.md)** - Code standards

### Requirements & Design
- **[Requirements](docs/requirements/)** - Feature specifications
- **[Design Documents](docs/design/)** - Technical designs
- **[Test Reports](docs/test_reports/)** - Quality assurance

---

## Project Structure

```
mcp_pdftools/
├── src/pdftools/              # Source code
│   ├── core/                  # Shared utilities
│   ├── merge/                 # PDF merge module
│   ├── split/                 # PDF split module
│   ├── ocr/                   # OCR module
│   ├── text_extraction/       # Text extraction (planned)
│   ├── protection/            # PDF protection (planned)
│   ├── thumbnails/            # Thumbnail generation (planned)
│   └── renaming/              # Invoice renaming (planned)
│
├── tests/                     # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── e2e/                   # End-to-end tests
│
├── docs/                      # Documentation
│   ├── tools/                 # User documentation
│   ├── requirements/          # Requirements
│   ├── design/                # Design documents
│   └── test_reports/          # Test reports
│
├── docs/
│   ├── INSTALLATION.md        # Installation guide
├── README.md                  # This file
├── requirements.txt           # Python dependencies
└── setup.py                   # Package configuration
```

---

## Performance

### Benchmarks

Tested on standard hardware (Intel i5, 8GB RAM, SSD):

#### PDF Merge
| Files | Total Pages | Time | Pages/sec |
|-------|-------------|------|-----------|
| 2 | 20 | 0.5s | 40 |
| 10 | 100 | 2.3s | 43 |
| 50 | 500 | 11.2s | 45 |

#### PDF Split
| Mode | Pages | Files Created | Time | Pages/sec |
|------|-------|---------------|------|-----------|
| PAGES | 50 | 50 | 2.1s | 24 |
| PAGES | 500 | 500 | 22.5s | 22 |
| RANGES | 100 | 5 | 1.8s | 56 |

#### OCR Processing
| Pages | DPI | Language | Time | Pages/min |
|-------|-----|----------|------|-----------|
| 5 | 300 | eng | 10.2s | 29 |
| 10 | 300 | eng | 19.8s | 30 |
| 5 | 300 | deu+eng | 15.4s | 19 |

---

## Troubleshooting

### Common Issues

**Command not found (pdfmerge, pdfsplit, etc.)**:
```bash
# Activate virtual environment
source pdf-env/bin/activate

# Reinstall package
pip install -e .
```

**Tesseract not found**:
```bash
# Linux
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows - download from official site
# Add to PATH: C:\Program Files\Tesseract-OCR
```

**Module not found errors**:
```bash
pip install -r requirements.txt
```

**Permission denied**:
```bash
# Check directory permissions
chmod +w /path/to/output/

# Or use a directory you own
```

For detailed troubleshooting, see:
- [INSTALLATION.md](docs/INSTALLATION.md#troubleshooting)
- Tool-specific documentation in [docs/tools/](docs/tools/)

---

## Development

### For Contributors

```bash
# Clone repository
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v --cov=src/pdftools

# Code quality checks
black src/
isort src/
flake8 src/
mypy src/
```

### Running Tests

```bash
# All tests
pytest -v

# With coverage
pytest -v --cov=src/pdftools --cov-report=html

# Specific test module
pytest tests/unit/test_merge_core.py -v

# Generate test PDFs
python scripts/generate_test_pdfs.py --all
```

See [DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) for detailed workflow.

---

## MCP Server Integration

### ✅ MCP Server for AI Agents (REQ-010)
**Status**: ✅ Released (v1.0)

The MCP Server enables AI Agents (Claude Code, Claude Desktop, OpenCode, Zed) to use all 7 PDF tools via the Model Context Protocol.

**What it enables:**
- Natural language PDF workflows: "Merge these 3 PDFs and protect with password"
- Automatic tool selection by AI agents
- Seamless integration in Claude Desktop, Claude Code, OpenCode, and other MCP-compatible clients

**Available MCP Tools:**
| MCP Tool Name | CLI Tool | Description |
|---------------|----------|-------------|
| `pdf_merge` | pdfmerge | Merge multiple PDF files into one |
| `pdf_split` | pdfsplit | Split PDF into multiple files |
| `pdf_ocr` | ocrutil | Extract text from scanned PDFs using OCR |
| `pdf_extract_text` | pdfgettxt | Extract text from PDF files |
| `pdf_protect` | pdfprotect | Add password protection to PDFs |
| `pdf_thumbnails` | pdfthumbnails | Generate thumbnail images from PDFs |
| `pdf_rename_invoice` | pdfrename | Intelligently rename invoice PDFs |

### Installation

The MCP server is automatically installed and configured when you run `./install.sh`.

**What the installer does:**
- ✅ Installs MCP server dependencies (Node.js packages)
- ✅ Compiles TypeScript to JavaScript
- ✅ Runs health checks to verify installation
- ✅ Auto-generates configuration for detected AI agents
- ✅ Optionally adds configuration to OpenCode, Claude Desktop, or Zed

**Manual Installation:**
```bash
cd mcp-server
npm install
npm run build
npm test
```

### Configuration

After installation, the MCP server can be used with any MCP-compatible AI agent:

**OpenCode** (`~/.config/opencode/opencode.json`):
```json
{
  "mcp": {
    "pdftools": {
      "type": "local",
      "command": ["node", "/path/to/mcp_pdftools/mcp-server/dist/index.js"],
      "enabled": true,
      "environment": {
        "MCP_PDFTOOLS_VENV": "/path/to/mcp_pdftools/venv/bin/python"
      },
      "timeout": 300000
    }
  }
}
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "pdftools": {
      "command": "node",
      "args": ["/path/to/mcp_pdftools/mcp-server/dist/index.js"]
    }
  }
}
```

The `./install.sh` script can automatically generate and add this configuration for you.

### Health Check

Verify your MCP server installation:
```bash
./scripts/health_check_mcp.sh
```

This checks:
- ✅ MCP server directory exists
- ✅ Dependencies installed
- ✅ TypeScript compiled successfully
- ✅ All 7 tools registered
- ✅ Server starts correctly
- ✅ All tests passing

### Usage Examples

Once configured, you can use natural language with your AI agent:

```
User: "Merge report_part1.pdf and report_part2.pdf into final_report.pdf"
AI Agent: [Uses pdf_merge tool automatically]
AI Agent: "I've successfully merged the two PDF files into final_report.pdf"

User: "Extract text from this scanned invoice: scan.pdf"
AI Agent: [Uses pdf_ocr and pdf_extract_text tools]
AI Agent: "Here's the extracted text from the invoice: [content...]"
```

**Documentation:**
- [REQ-010: MCP Server Requirements](docs/requirements/REQ-010-mcp-server.md)
- [REQ-010.1: Health Check & Auto-Configuration](docs/requirements/REQ-010.1-health-check.md)
- [DESIGN-010: MCP Server Design](docs/design/DESIGN-010-mcp-server.md)

---

## Roadmap

### Future Features

#### Future Enhancements
- GUI application for non-technical users
- Batch processing workflows
- PDF compression and optimization
- Watermarking capabilities
- Digital signature verification

---

## Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/my-feature`
3. **Read the guidelines**: See [DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md)
4. **Make your changes**
5. **Write tests**: Maintain >90% coverage
6. **Run quality checks**: `black`, `isort`, `flake8`, `mypy`
7. **Submit pull request**

### Development Guidelines
- Follow SOLID principles
- Write comprehensive tests
- Use type hints and docstrings
- Follow existing code patterns
- Update documentation

See [DEVELOPMENT_PROCESS.md](docs/DEVELOPMENT_PROCESS.md) for detailed workflow.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

### Getting Help

1. **Check Documentation**:
   - [Installation Guide](docs/INSTALLATION.md)
   - Tool-specific docs in [docs/tools/](docs/tools/)

2. **Search Issues**:
   - Browse existing GitHub issues
   - Check troubleshooting sections

3. **Create New Issue**:
   - Include OS and Python version
   - Provide complete error messages
   - Describe steps to reproduce
   - Attach sample files if possible

---

## Acknowledgments

- **PyPDF2**: PDF manipulation library
- **Tesseract OCR**: Google's OCR engine
- **pdf2image**: PDF to image conversion
- **ReportLab**: PDF generation

---

## Version History

### v2.0.0 (Current)
- Modular architecture with `src/pdftools/` structure
- Released tools: pdfmerge, pdfsplit, ocrutil
- Comprehensive test suite
- Professional documentation
- CLI entry points via setup.py

### v1.0.0 (Legacy)
- Initial standalone scripts
- Basic functionality
- Limited documentation

---

**Built with Python** | **Powered by Tesseract OCR** | **Professional PDF Processing**
