# PDF Text Extraction Tool

Extract text from PDF files with multiple extraction modes and output formats.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Extraction Modes](#extraction-modes)
- [Output Formats](#output-formats)
- [Options](#options)
- [Examples](#examples)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **pdfgettxt** tool extracts text content from PDF files using various extraction modes and formats. It supports simple text extraction, layout preservation, per-page extraction, and structured output.

### Key Features

- **4 Extraction Modes**: SIMPLE, LAYOUT, PER_PAGE, STRUCTURED
- **3 Output Formats**: TXT, JSON, MARKDOWN
- **Page Selection**: Extract specific pages or ranges
- **Metadata Support**: Include PDF metadata in output
- **Encoding Options**: Configurable output encoding
- **Flexible Output**: Write to file or stdout
- **Batch Processing**: Process multiple pages efficiently

### Requirements

- Python 3.8+
- PyPDF2 or pdfplumber library
- Read access to source PDF
- Write access to output directory (if saving to file)

---

## Installation

Install MCP PDF Tools package:

```bash
pip install -e .
```

Or install just the dependencies:

```bash
pip install PyPDF2>=3.0.1 pdfplumber>=0.9.0
```

See [INSTALLATION.md](../../INSTALLATION.md) for detailed installation instructions.

---

## Usage

### Basic Syntax

```bash
pdfgettxt -i input.pdf [-o output.txt] [-m MODE] [-f FORMAT] [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-i, --input` | Input PDF file to extract text from |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-o, --output` | Output file or directory path | stdout |
| `-m, --mode` | Extraction mode: `simple`, `layout`, `per_page`, `structured` | `simple` |
| `-f, --format` | Output format: `txt`, `json`, `markdown` | `txt` |
| `-p, --pages` | Specific pages to extract (e.g., "1,3,5-10") | All pages |
| `-e, --encoding` | Output encoding | `utf-8` |
| `--include-metadata` | Include PDF metadata in output | Disabled |
| `-v, --verbose` | Enable verbose output | Disabled |

---

## Extraction Modes

### 1. SIMPLE Mode (Default)

Extracts plain text without preserving layout.

**Usage**:
```bash
pdfgettxt -i document.pdf -m simple
```

**When to use**:
- Basic text extraction
- Content analysis
- Search indexing
- Copy/paste operations

**Characteristics**:
- Fastest extraction
- No layout preservation
- Continuous text flow
- Minimal formatting

---

### 2. LAYOUT Mode

Preserves the original layout and spacing of the PDF.

**Usage**:
```bash
pdfgettxt -i document.pdf -m layout -o output.txt
```

**When to use**:
- Preserving tables and columns
- Maintaining visual structure
- Forms and structured documents
- Reports with formatting

**Characteristics**:
- Layout preservation
- Spacing maintained
- Column alignment preserved
- Table structure retained

---

### 3. PER_PAGE Mode

Extracts text into separate files, one per page.

**Usage**:
```bash
pdfgettxt -i document.pdf -m per_page -o ./pages/
```

**Output**:
```
./pages/document_page_1.txt
./pages/document_page_2.txt
./pages/document_page_3.txt
...
```

**When to use**:
- Page-by-page analysis
- Parallel processing
- Individual page editing
- Selective content extraction

**Note**: Output path must be a directory.

---

### 4. STRUCTURED Mode

Extracts text with metadata and structure information.

**Usage**:
```bash
pdfgettxt -i document.pdf -m structured -f json -o output.json
```

**Output**: JSON with page-by-page text and metadata

**When to use**:
- Data extraction for databases
- API integration
- Automated processing
- Quality analysis

**Best used with**: JSON or MARKDOWN format

---

## Output Formats

### 1. TXT Format (Default)

Plain text output.

**Usage**:
```bash
pdfgettxt -i document.pdf -f txt -o output.txt
```

**Advantages**:
- Simple and universal
- Smallest file size
- Easy to process
- Compatible with all text editors

---

### 2. JSON Format

Structured JSON output with metadata.

**Usage**:
```bash
pdfgettxt -i document.pdf -f json -o output.json
```

**JSON Structure**:
```json
{
  "metadata": {
    "title": "Document Title",
    "author": "Author Name",
    "pages": 10,
    "created": "2024-01-15"
  },
  "pages": [
    {
      "page_num": 1,
      "text": "Page 1 content...",
      "char_count": 1234
    },
    {
      "page_num": 2,
      "text": "Page 2 content...",
      "char_count": 1456
    }
  ],
  "total_chars": 12345
}
```

**Advantages**:
- Structured data
- Per-page information
- Metadata included
- Easy parsing

---

### 3. MARKDOWN Format

Markdown-formatted output.

**Usage**:
```bash
pdfgettxt -i document.pdf -f markdown -o output.md
```

**Output**:
```markdown
# Document Title

**Pages**: 10 | **Author**: John Doe

---

## Page 1

Page 1 content...

---

## Page 2

Page 2 content...
```

**Advantages**:
- Human-readable
- Preserves structure
- Easy to edit
- Compatible with documentation tools

---

## Options

### Input (`-i, --input`)

Path to the PDF file to extract text from.

**Requirements**:
- File must exist
- File must be a valid PDF
- Read permission required

**Syntax**:
```bash
-i /path/to/document.pdf
```

### Output (`-o, --output`)

Output file path or directory.

**Default**: stdout (prints to console)

**For most modes**: Specify a file path
```bash
-o /path/to/output.txt
```

**For PER_PAGE mode**: Specify a directory
```bash
-o /path/to/pages/
```

**Notes**:
- Parent directory must exist (or will be created)
- Existing files will be overwritten
- Use quotes for paths with spaces

### Mode (`-m, --mode`)

Extraction mode to use.

**Choices**: `simple`, `layout`, `per_page`, `structured`

**Default**: `simple`

**Syntax**:
```bash
-m layout
```

### Format (`-f, --format`)

Output format.

**Choices**: `txt`, `json`, `markdown`

**Default**: `txt`

**Syntax**:
```bash
-f json
```

### Pages (`-p, --pages`)

Specific pages to extract.

**Default**: All pages

**Syntax**:
```bash
-p "1,3,5-10"
```

**Format**:
- Single page: `"5"`
- Multiple pages: `"1,3,5"`
- Range: `"1-10"`
- Mixed: `"1,3,5-10,15"`

**Examples**:
```bash
# First 5 pages
-p "1-5"

# Specific pages
-p "1,5,10,15"

# Multiple ranges
-p "1-3,10-15,50-55"
```

### Encoding (`-e, --encoding`)

Output text encoding.

**Default**: `utf-8`

**Syntax**:
```bash
-e utf-8
```

**Common encodings**:
- `utf-8`: Unicode (recommended)
- `ascii`: ASCII only
- `latin-1`: Western European
- `cp1252`: Windows encoding

### Include Metadata (`--include-metadata`)

Include PDF metadata in output.

**Syntax**:
```bash
--include-metadata
```

**Metadata includes**:
- Title
- Author
- Subject
- Keywords
- Creation date
- Modification date
- Page count

**Best used with**: JSON or MARKDOWN format

### Verbose (`-v, --verbose`)

Enable detailed logging.

**Syntax**:
```bash
-v
```

**Shows**:
- Processing progress
- Page-by-page status
- Character counts
- Performance metrics
- Debug information

---

## Examples

### Example 1: Basic Text Extraction

Extract all text to stdout:

```bash
pdfgettxt -i document.pdf
```

**Output**: Text printed to console

### Example 2: Extract to File

Extract text to a file:

```bash
pdfgettxt -i report.pdf -o report.txt
```

**Output**: `report.txt` with extracted text

### Example 3: Layout-Preserving Extraction

Preserve layout and formatting:

```bash
pdfgettxt -i invoice.pdf -m layout -o invoice.txt
```

**Use case**: Extracting tables and structured data

### Example 4: Extract Specific Pages

Extract only pages 1-5:

```bash
pdfgettxt -i manual.pdf -p "1-5" -o introduction.txt
```

### Example 5: Per-Page Extraction

Extract each page to separate files:

```bash
pdfgettxt -i book.pdf -m per_page -o ./chapters/
```

**Output**:
```
./chapters/book_page_1.txt
./chapters/book_page_2.txt
./chapters/book_page_3.txt
...
```

### Example 6: JSON Output with Metadata

Extract structured data as JSON:

```bash
pdfgettxt -i contract.pdf -f json --include-metadata -o contract.json
```

**Output**: `contract.json` with text and metadata

### Example 7: Markdown Output

Convert PDF to Markdown:

```bash
pdfgettxt -i presentation.pdf -f markdown -o presentation.md
```

**Use case**: Converting presentations to documentation

### Example 8: Multiple Page Ranges

Extract selected sections:

```bash
pdfgettxt -i thesis.pdf -p "1-3,10-25,50-55" -o selected_chapters.txt
```

### Example 9: Verbose Processing

Monitor extraction progress:

```bash
pdfgettxt -i large_document.pdf -v -o output.txt
```

**Verbose Output**:
```
INFO: Processing document: large_document.pdf
INFO: Mode: SIMPLE | Format: TXT
INFO: Extracting page 1/250...
INFO: Extracting page 2/250...
...
INFO: Extraction complete
✓ Successfully extracted 125,432 characters
  Pages processed: 250
  Output: output.txt
```

### Example 10: Structured JSON Extraction

Extract with full structure:

```bash
pdfgettxt -i report.pdf -m structured -f json --include-metadata -o report_data.json
```

**Use case**: Data extraction for databases or APIs

### Example 11: Custom Encoding

Extract with specific encoding:

```bash
pdfgettxt -i german_document.pdf -e iso-8859-1 -o output.txt
```

### Example 12: Extract Single Page

Extract just page 10:

```bash
pdfgettxt -i manual.pdf -p "10" -o page10.txt
```

---

## Common Use Cases

### 1. Content Indexing

**Scenario**: Index PDF content for search.

```bash
pdfgettxt -i document.pdf -m simple -o indexed_content.txt
```

### 2. Data Extraction from Forms

**Scenario**: Extract data from filled PDF forms.

```bash
pdfgettxt -i application_form.pdf -m layout -f json -o form_data.json
```

### 3. Invoice Processing

**Scenario**: Extract invoice text for automated processing.

```bash
pdfgettxt -i invoice.pdf -m layout --include-metadata -f json -o invoice_data.json
```

### 4. Book Digitization

**Scenario**: Convert PDF book to text files per chapter.

```bash
# Extract each page separately
pdfgettxt -i book.pdf -m per_page -o ./book_pages/

# Or extract specific chapters
pdfgettxt -i book.pdf -p "1-25" -o chapter1.txt
pdfgettxt -i book.pdf -p "26-50" -o chapter2.txt
```

### 5. Contract Analysis

**Scenario**: Extract contract text for review.

```bash
pdfgettxt -i contract.pdf -m layout -f markdown -o contract.md
```

### 6. Research Paper Text Mining

**Scenario**: Extract text from research papers for analysis.

```bash
pdfgettxt -i research_paper.pdf -m simple -o paper_text.txt

# Then analyze
grep -i "methodology" paper_text.txt
```

### 7. Report Conversion

**Scenario**: Convert PDF reports to Markdown.

```bash
pdfgettxt -i annual_report.pdf -m layout -f markdown --include-metadata -o report.md
```

### 8. Batch Processing

**Scenario**: Extract text from multiple PDFs.

```bash
#!/bin/bash
for pdf in *.pdf; do
    echo "Processing: $pdf"
    pdfgettxt -i "$pdf" -o "${pdf%.pdf}.txt"
done
```

---

## Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | Text extracted successfully |
| 1 | Error | Error occurred (file not found, invalid PDF, etc.) |
| 130 | Cancelled | Operation cancelled by user (Ctrl+C) |

### Example: Checking Exit Code

```bash
pdfgettxt -i document.pdf -o output.txt
if [ $? -eq 0 ]; then
    echo "Extraction successful!"
else
    echo "Extraction failed!"
fi
```

---

## Performance

### Benchmarks

Tested on standard hardware (Intel i5, 8GB RAM, SSD):

| Pages | Mode | Format | Time | Pages/sec |
|-------|------|--------|------|-----------|
| 10 | SIMPLE | TXT | 0.8s | 12.5 |
| 50 | SIMPLE | TXT | 3.2s | 15.6 |
| 100 | SIMPLE | TXT | 6.1s | 16.4 |
| 10 | LAYOUT | TXT | 1.2s | 8.3 |
| 50 | LAYOUT | TXT | 5.8s | 8.6 |
| 100 | SIMPLE | JSON | 7.5s | 13.3 |
| 100 | PER_PAGE | TXT | 8.2s | 12.2 |

### Performance Tips

1. **Use SIMPLE mode** for fastest extraction (if layout not needed)
2. **Extract specific pages** instead of full document when possible
3. **Use TXT format** for best performance
4. **SSD storage** significantly faster than HDD
5. **Close other applications** to free up RAM
6. **Batch process** multiple files sequentially

### Performance Factors

**Affects Speed**:
- **Mode**: SIMPLE fastest, LAYOUT slower
- **Format**: TXT fastest, JSON/MARKDOWN slower
- **Page count**: More pages = more time (linear)
- **PDF complexity**: Images, fonts, encryption slow down extraction
- **Output destination**: Local disk faster than network drives

---

## Troubleshooting

### Error: "Input file not found"

**Cause**: The specified PDF file doesn't exist.

**Solution**:
```bash
# Check file exists
ls -l document.pdf

# Use absolute path
pdfgettxt -i /full/path/to/document.pdf -o output.txt
```

### Error: "Invalid PDF file"

**Cause**: The file is corrupted or not a valid PDF.

**Solution**:
- Open the file in a PDF reader to verify
- Try repairing the PDF
- Re-export the PDF from the original source

### Error: "Permission denied"

**Cause**: No read permission for input file or write permission for output.

**Solution**:
```bash
# Check file permissions
ls -l document.pdf

# Check output directory permissions
ls -ld ./output/

# Use a directory you own
pdfgettxt -i document.pdf -o ~/Documents/output.txt
```

### Error: "Invalid page numbers"

**Cause**: Page specification is invalid.

**Solution**:
```bash
# Correct formats
-p "1-10"
-p "1,5,10"
-p "1-5,10-15"

# Incorrect formats (will fail)
-p "10-1"     # Start > End
-p "abc"      # Not numbers
```

### Error: "Output must be a directory for PER_PAGE mode"

**Cause**: PER_PAGE mode requires a directory, not a file path.

**Solution**:
```bash
# Correct usage
pdfgettxt -i doc.pdf -m per_page -o ./pages/

# Incorrect usage
pdfgettxt -i doc.pdf -m per_page -o output.txt  # Wrong!
```

### Warning: "No text found"

**Symptom**: Extraction completes but output is empty.

**Causes**:
- PDF contains only images (scanned document)
- PDF is encrypted
- Text is embedded as graphics

**Solutions**:
```bash
# For scanned PDFs, use OCR first
ocrutil -f scan.pdf -l eng --output-mode pdf -o scan_ocr.pdf
pdfgettxt -i scan_ocr.pdf -o output.txt

# Check if PDF is encrypted
pdfinfo document.pdf | grep Encrypted
```

### Issue: Garbled Text

**Symptom**: Extracted text has strange characters.

**Causes**:
- Encoding mismatch
- Embedded fonts
- Special characters

**Solutions**:
```bash
# Try different encoding
pdfgettxt -i document.pdf -e utf-8 -o output.txt
pdfgettxt -i document.pdf -e latin-1 -o output.txt

# Use verbose mode to see what's happening
pdfgettxt -i document.pdf -v -o output.txt
```

### Issue: Layout Lost

**Symptom**: Tables and columns are jumbled.

**Solution**:
```bash
# Use LAYOUT mode
pdfgettxt -i document.pdf -m layout -o output.txt
```

### Issue: Slow Performance

**Symptoms**: Extraction takes longer than expected.

**Solutions**:
1. Use SIMPLE mode instead of LAYOUT
2. Extract only needed pages: `-p "1-10"`
3. Use TXT format instead of JSON/MARKDOWN
4. Process on SSD instead of HDD
5. Close other applications

### Issue: Out of Memory

**Error**: "MemoryError" or system freeze

**Cause**: PDF too large for available RAM.

**Solutions**:
1. Extract in smaller chunks:
   ```bash
   pdfgettxt -i large.pdf -p "1-50" -o part1.txt
   pdfgettxt -i large.pdf -p "51-100" -o part2.txt
   ```
2. Use PER_PAGE mode for very large PDFs
3. Close other applications
4. Upgrade system RAM

---

## Advanced Usage

### Integration with Other Tools

**Extract then Search**:
```bash
# Extract text
pdfgettxt -i document.pdf -o text.txt

# Search for keywords
grep -i "important" text.txt
```

**OCR then Extract**:
```bash
# OCR scanned PDF
ocrutil -f scan.pdf -l eng --output-mode pdf -o scan_ocr.pdf

# Extract text
pdfgettxt -i scan_ocr.pdf -o text.txt
```

**Split then Extract**:
```bash
# Split PDF
pdfsplit -i large.pdf -m parts -p 5 -o ./parts/

# Extract text from each part
for part in ./parts/*.pdf; do
    pdfgettxt -i "$part" -o "${part%.pdf}.txt"
done
```

### Python Integration

```python
import subprocess
import json

# Extract as JSON
result = subprocess.run([
    'pdfgettxt',
    '-i', 'document.pdf',
    '-f', 'json',
    '-o', 'output.json'
], capture_output=True)

if result.returncode == 0:
    # Parse JSON
    with open('output.json', 'r') as f:
        data = json.load(f)

    print(f"Total characters: {data['total_chars']}")
    print(f"Pages: {len(data['pages'])}")
else:
    print("Extraction failed:", result.stderr.decode())
```

### Bash Script Example

```bash
#!/bin/bash
# Extract text from all PDFs in a directory

for pdf in *.pdf; do
    echo "Processing: $pdf"

    # Extract to text file
    pdfgettxt -i "$pdf" -o "${pdf%.pdf}.txt"

    # Check result
    if [ $? -eq 0 ]; then
        echo "  ✓ Success"
    else
        echo "  ✗ Failed"
    fi
done

echo "All PDFs processed!"
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [PDF Merge Tool](pdfmerge.md)
- [PDF Split Tool](pdfsplit.md)
- [OCR Tool](ocrutil.md)
- [Project README](../../README.md)

---

## Support

For issues and questions:

1. Check this troubleshooting section
2. Review [INSTALLATION.md](../../INSTALLATION.md)
3. Search GitHub issues
4. Create a new issue with:
   - Command you ran
   - Expected vs actual output
   - PDF file details (pages, size, source)
   - Error messages
   - Verbose output (`-v` flag)
