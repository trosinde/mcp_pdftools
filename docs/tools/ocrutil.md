# OCR Utility Tool

Perform Optical Character Recognition (OCR) on scanned PDF documents using Tesseract OCR.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [OCR Languages](#ocr-languages)
- [Output Modes](#output-modes)
- [Options](#options)
- [Examples](#examples)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **ocrutil** tool extracts text from scanned PDF documents using Optical Character Recognition. It converts image-based PDFs into searchable, text-based documents.

### Key Features

- **Multi-language support**: German, English, French, Italian, Spanish
- **3 Output formats**: TXT, searchable PDF, JSON
- **Page selection**: Process all pages or specific ranges
- **Quality control**: Confidence scores and word counts
- **Performance metrics**: Processing time and statistics
- **Flexible DPI settings**: Adjustable image resolution
- **Batch processing**: Process multiple pages efficiently

### Requirements

- Python 3.8+
- Tesseract OCR engine (system-level)
- pytesseract library
- pdf2image library
- Pillow library
- Read access to source PDF
- Write access to output directory

---

## Installation

### Step 1: Install MCP PDF Tools

```bash
pip install -e .
```

### Step 2: Install Tesseract OCR

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr

# Install language packs
sudo apt-get install tesseract-ocr-deu  # German
sudo apt-get install tesseract-ocr-eng  # English
sudo apt-get install tesseract-ocr-fra  # French
sudo apt-get install tesseract-ocr-ita  # Italian
sudo apt-get install tesseract-ocr-spa  # Spanish
```

**macOS**:
```bash
brew install tesseract
brew install tesseract-lang  # All languages
```

**Windows**:
1. Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run installer
3. Select language packs during installation
4. Add to PATH: `C:\Program Files\Tesseract-OCR`

### Step 3: Verify Installation

```bash
tesseract --version
tesseract --list-langs
```

Expected output:
```
tesseract 5.x.x
Available languages:
deu
eng
fra
ita
spa
...
```

See [INSTALLATION.md](../../INSTALLATION.md) for detailed installation instructions.

---

## Usage

### Basic Syntax

```bash
ocrutil -f input.pdf -o output.txt -l LANGUAGE --output-mode MODE
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-f, --file` | Input PDF file to process |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-o, --output` | Output file path | `{filename}_ocr.{ext}` |
| `-l, --language` | OCR language(s) - single or multiple with `+` | `deu` (German) |
| `--output-mode` | Output format: `txt`, `pdf`, `json` | `txt` |
| `--pages` | Page range (e.g., "1-5,7,9-12") | All pages |
| `--dpi` | DPI for PDF to image conversion | 300 |
| `-v, --verbose` | Enable verbose output | Disabled |

---

## OCR Languages

### Supported Languages

| Language | Code | Install Command (Linux) |
|----------|------|-------------------------|
| German | `deu` | `apt-get install tesseract-ocr-deu` |
| English | `eng` | `apt-get install tesseract-ocr-eng` |
| French | `fra` | `apt-get install tesseract-ocr-fra` |
| Italian | `ita` | `apt-get install tesseract-ocr-ita` |
| Spanish | `spa` | `apt-get install tesseract-ocr-spa` |

### Single Language

```bash
ocrutil -f document.pdf -l eng
```

### Multiple Languages

Combine languages using the `+` separator:

```bash
ocrutil -f document.pdf -l deu+eng
```

**When to use multiple languages**:
- Documents with mixed languages
- Technical documents with English terms in German text
- International contracts
- Multilingual forms

**Note**: Using multiple languages may reduce accuracy and increase processing time.

### Check Installed Languages

```bash
tesseract --list-langs
```

---

## Output Modes

### 1. TXT Mode (Default)

Extracts text to a plain text file.

**Usage**:
```bash
ocrutil -f scan.pdf --output-mode txt -o output.txt
```

**Output**: Plain text file with extracted text

**When to use**:
- Need searchable text
- Further text processing
- Copy/paste operations
- Simple text extraction

**Advantages**:
- Smallest file size
- Easy to process programmatically
- Compatible with all text editors

---

### 2. PDF Mode

Creates a searchable PDF with invisible text layer.

**Usage**:
```bash
ocrutil -f scan.pdf --output-mode pdf -o searchable.pdf
```

**Output**: PDF file with searchable text layer (original images preserved)

**When to use**:
- Need searchable PDF
- Preserve original appearance
- PDF workflows
- Archive searchable documents

**Advantages**:
- Maintains original formatting
- Searchable in PDF readers
- Professional appearance
- Standard archive format

---

### 3. JSON Mode

Outputs structured JSON with detailed OCR results.

**Usage**:
```bash
ocrutil -f scan.pdf --output-mode json -o results.json
```

**Output**: JSON file with structured data

**JSON Structure**:
```json
{
  "file": "scan.pdf",
  "total_pages": 5,
  "pages_processed": 5,
  "language": "deu",
  "dpi": 300,
  "processing_time_seconds": 12.34,
  "pages": [
    {
      "page_number": 1,
      "text": "Extracted text from page 1...",
      "confidence": 0.95,
      "word_count": 234
    },
    {
      "page_number": 2,
      "text": "Extracted text from page 2...",
      "confidence": 0.92,
      "word_count": 198
    }
  ],
  "summary": {
    "total_words": 1245,
    "avg_confidence": 0.94,
    "low_confidence_pages": []
  }
}
```

**When to use**:
- API integration
- Automated processing pipelines
- Quality analysis
- Data extraction for databases
- Machine learning training data

**Advantages**:
- Structured data
- Confidence scores
- Per-page statistics
- Easy to parse programmatically

---

## Options

### File (`-f, --file`)

Input PDF file to process.

**Requirements**:
- Must be a valid PDF file
- Can be scanned or image-based
- File must exist and be readable

**Syntax**:
```bash
-f /path/to/scan.pdf
```

### Output (`-o, --output`)

Output file path.

**Default**: `{input_filename}_ocr.{extension}`

**Extension determined by output mode**:
- TXT mode: `.txt`
- PDF mode: `.pdf`
- JSON mode: `.json`

**Syntax**:
```bash
-o /path/to/output.txt
```

### Language (`-l, --language`)

OCR language(s) to use.

**Default**: `deu` (German)

**Single language**:
```bash
-l eng
```

**Multiple languages**:
```bash
-l deu+eng+fra
```

**Notes**:
- Languages must be installed (see [OCR Languages](#ocr-languages))
- Order matters: primary language first
- More languages = slower processing

### Output Mode (`--output-mode`)

Output format.

**Choices**: `txt`, `pdf`, `json`

**Default**: `txt`

**Syntax**:
```bash
--output-mode pdf
```

### Pages (`--pages`)

Specify which pages to process.

**Default**: All pages

**Syntax**:
```bash
--pages "1-5,10,15-20"
```

**Format**:
- Single page: `"5"`
- Range: `"1-10"`
- Multiple ranges: `"1-5,10-15,20-25"`
- Mixed: `"1,3,5-10,15"`

**Examples**:
```bash
# First 5 pages
--pages "1-5"

# Specific pages
--pages "1,5,10,15"

# Multiple ranges
--pages "1-3,10-15,50-55"
```

### DPI (`--dpi`)

Resolution for PDF to image conversion.

**Default**: 300

**Recommended values**:
- **150**: Fast, lower quality (drafts)
- **300**: Standard quality (recommended)
- **600**: High quality (small text)

**Syntax**:
```bash
--dpi 600
```

**Trade-offs**:
- **Higher DPI**: Better accuracy, slower processing, larger memory usage
- **Lower DPI**: Faster processing, lower accuracy

### Verbose (`-v, --verbose`)

Enable detailed output.

**Syntax**:
```bash
-v
```

**Shows**:
- Page-by-page progress
- Confidence scores
- Processing statistics
- Timing information
- Debug messages

---

## Examples

### Example 1: Basic OCR (German, TXT output)

Extract text from a German scanned document:

```bash
ocrutil -f rechnung.pdf
```

**Output**: `rechnung_ocr.txt` with extracted text

### Example 2: English Document to PDF

Create a searchable PDF from English scanned pages:

```bash
ocrutil -f scan.pdf -l eng --output-mode pdf -o searchable.pdf
```

**Output**: `searchable.pdf` with searchable text layer

### Example 3: Multi-language Document

Process a document with German and English text:

```bash
ocrutil -f contract.pdf -l deu+eng --output-mode pdf -o contract_searchable.pdf
```

### Example 4: Specific Pages

OCR only the first 5 pages:

```bash
ocrutil -f large_document.pdf --pages "1-5" -o summary.txt
```

### Example 5: JSON Output for Processing

Extract OCR data as JSON for further processing:

```bash
ocrutil -f invoice.pdf -l deu --output-mode json -o invoice_data.json
```

**Use case**: Extract invoice data for automated processing

### Example 6: High-Quality OCR

Use higher DPI for better accuracy on small text:

```bash
ocrutil -f contract_small_print.pdf -l eng --dpi 600 -o contract.txt
```

### Example 7: Verbose Mode

Monitor processing progress with detailed output:

```bash
ocrutil -f report.pdf -l eng -v
```

**Verbose Output**:
```
INFO: Starting OCR processing: report.pdf
INFO: Processing pages: [1, 2, 3, 4, 5]
DEBUG: Converting page 1 to image (300 DPI)...
DEBUG: Running OCR on page 1...
INFO: Page 1: confidence=95.2%, words=234
DEBUG: Converting page 2 to image (300 DPI)...
DEBUG: Running OCR on page 2...
INFO: Page 2: confidence=93.8%, words=198
...

============================================================
OCR Processing Completed Successfully
============================================================
Output file:      report_ocr.txt
Pages processed:  5/5
Average confidence: 94.35%
Total words:      1245
Processing time:  12.34s
============================================================
```

### Example 8: Multiple Page Ranges

Process selected sections of a document:

```bash
ocrutil -f manual.pdf --pages "1-3,10-15,50-55" -l eng -o selected_sections.txt -v
```

### Example 9: French Document

Process a French scanned document:

```bash
ocrutil -f document_fr.pdf -l fra --output-mode pdf -o document_searchable.pdf
```

### Example 10: Batch Processing Script

Process multiple scanned PDFs:

```bash
#!/bin/bash
for file in scans/*.pdf; do
    echo "Processing: $file"
    ocrutil -f "$file" -l deu --output-mode pdf -o "searchable/$(basename ${file%.pdf})_ocr.pdf"
done
```

---

## Common Use Cases

### 1. Archive Digitization

**Scenario**: Convert scanned archives to searchable PDFs.

```bash
ocrutil -f "Historical Document 1923.pdf" -l deu --output-mode pdf -o "Historical Document 1923 Searchable.pdf"
```

### 2. Invoice Processing

**Scenario**: Extract invoice data for accounting software.

```bash
ocrutil -f invoice.pdf -l deu --output-mode json -o invoice_data.json

# Then process JSON with Python/Node.js
python extract_invoice_fields.py invoice_data.json
```

### 3. Contract Analysis

**Scenario**: Make scanned contracts searchable for legal review.

```bash
ocrutil -f contract_scan.pdf -l eng --output-mode pdf --dpi 600 -o contract_searchable.pdf
```

**Note**: Higher DPI (600) for better accuracy on legal documents.

### 4. Multi-language Form

**Scenario**: Process a form with German and English text.

```bash
ocrutil -f application_form.pdf -l deu+eng --output-mode pdf -o application_searchable.pdf
```

### 5. Book Digitization

**Scenario**: Convert scanned book pages to searchable text.

```bash
# First split the book into chapters
pdfsplit -i book.pdf -m ranges -r "1-50,51-100,101-150" -o ./chapters/

# OCR each chapter
for chapter in ./chapters/*.pdf; do
    ocrutil -f "$chapter" -l eng --output-mode pdf -o "${chapter%.pdf}_searchable.pdf"
done

# Merge back
pdfmerge -f "./chapters/*_searchable.pdf" -o book_complete_searchable.pdf
```

### 6. Receipt Archiving

**Scenario**: Create searchable archive of receipts.

```bash
ocrutil -f receipt_2024_01.pdf -l deu --output-mode pdf -o "receipts_searchable/receipt_2024_01.pdf" -v
```

### 7. Research Paper Processing

**Scenario**: Extract text from scanned research papers for citation analysis.

```bash
ocrutil -f research_paper.pdf -l eng --output-mode txt -o paper_text.txt

# Use text for analysis
grep -i "references" paper_text.txt
```

### 8. Quality Check

**Scenario**: Check OCR quality before batch processing.

```bash
# Test on first page
ocrutil -f document.pdf --pages "1" -l deu -v

# Check confidence score, then process all pages
ocrutil -f document.pdf -l deu --output-mode pdf -o document_ocr.pdf
```

---

## Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | OCR completed successfully |
| 1 | Error | General error (invalid file, processing failed) |
| 2 | Tesseract Not Found | Tesseract OCR not installed or not in PATH |
| 3 | Language Not Available | Requested language pack not installed |
| 130 | Cancelled | Operation cancelled by user (Ctrl+C) |

### Example: Error Handling

```bash
#!/bin/bash

ocrutil -f scan.pdf -l eng -o output.txt

case $? in
    0)
        echo "Success! Processing complete."
        ;;
    2)
        echo "Error: Tesseract not installed. Install it first."
        ;;
    3)
        echo "Error: Language pack not available. Install language pack."
        ;;
    *)
        echo "Error: OCR processing failed."
        ;;
esac
```

---

## Performance

### Benchmarks

Tested on standard hardware (Intel i5, 8GB RAM, SSD):

| Pages | DPI | Language | Mode | Time | Pages/min |
|-------|-----|----------|------|------|-----------|
| 1 | 300 | eng | txt | 2.5s | 24 |
| 5 | 300 | eng | txt | 10.2s | 29 |
| 10 | 300 | eng | txt | 19.8s | 30 |
| 5 | 300 | deu+eng | txt | 15.4s | 19 |
| 1 | 600 | eng | txt | 4.2s | 14 |
| 10 | 300 | eng | pdf | 22.1s | 27 |

### Performance Factors

**Affects Speed**:
- **DPI**: Higher DPI = slower (300 recommended)
- **Languages**: Multiple languages = ~30% slower
- **Page complexity**: Images, tables, complex layouts slower
- **Output mode**: PDF mode slightly slower than TXT
- **System**: RAM, CPU, disk speed

**Optimization Tips**:
1. Use 300 DPI unless you need higher quality
2. Single language when possible
3. Process in batches for large jobs
4. Use SSD for temp files
5. Close other applications during processing

### Memory Usage

**Approximate RAM usage**:
- **300 DPI**: ~100 MB per page
- **600 DPI**: ~400 MB per page

**Recommendations**:
- 4 GB RAM: Process 1-5 pages at a time
- 8 GB RAM: Process 10-20 pages at a time
- 16+ GB RAM: Process 50+ pages at a time

---

## Troubleshooting

### Error: "Tesseract OCR is not installed"

**Exit code**: 2

**Cause**: Tesseract is not installed or not in PATH.

**Solution**:

**Linux**:
```bash
sudo apt-get install tesseract-ocr
tesseract --version
```

**macOS**:
```bash
brew install tesseract
tesseract --version
```

**Windows**:
- Download from [Tesseract Wiki](https://github.com/UB-Mannheim/tesseract/wiki)
- Install and add to PATH

**Verify**:
```bash
tesseract --version
which tesseract  # Linux/macOS
where tesseract  # Windows
```

### Error: "Language 'deu' not available"

**Exit code**: 3

**Cause**: Language pack not installed.

**Solution**:

**Linux**:
```bash
sudo apt-get install tesseract-ocr-deu
tesseract --list-langs
```

**macOS**:
```bash
brew install tesseract-lang
tesseract --list-langs
```

**Windows**:
- Re-run Tesseract installer
- Select additional language packs

### Error: "File not found"

**Cause**: Input PDF doesn't exist.

**Solution**:
```bash
# Check file exists
ls -l scan.pdf

# Use absolute path
ocrutil -f /full/path/to/scan.pdf -o output.txt
```

### Error: "Invalid PDF file"

**Cause**: File is corrupted or not a PDF.

**Solution**:
- Verify file with PDF reader
- Re-scan the document
- Try a different PDF

### Warning: Low Confidence Score

**Symptom**: Output shows confidence < 70%

**Causes**:
- Poor scan quality
- Wrong language
- Complex layout
- Low DPI

**Solutions**:
```bash
# Try higher DPI
ocrutil -f scan.pdf --dpi 600 -o output.txt

# Verify correct language
ocrutil -f scan.pdf -l eng -o output.txt

# Check original scan quality
```

### Issue: Missing Text

**Symptom**: OCR completes but output is incomplete.

**Causes**:
- Scanned images too light/dark
- Wrong language selected
- DPI too low

**Solutions**:
1. Increase DPI to 600
2. Verify correct language
3. Re-scan with better quality
4. Use multiple languages

### Issue: Slow Processing

**Symptom**: Takes much longer than expected.

**Solutions**:
```bash
# Use lower DPI
ocrutil -f scan.pdf --dpi 150 -o output.txt

# Process fewer pages at once
ocrutil -f scan.pdf --pages "1-10" -o part1.txt

# Use single language
ocrutil -f scan.pdf -l eng -o output.txt  # Instead of eng+deu+fra
```

### Issue: Out of Memory

**Error**: "MemoryError" or system freeze

**Cause**: PDF too large or DPI too high.

**Solutions**:
1. Reduce DPI: `--dpi 150`
2. Process fewer pages: `--pages "1-5"`
3. Close other applications
4. Split PDF first:
   ```bash
   pdfsplit -i large.pdf -m parts -p 5 -o ./parts/
   # Then OCR each part separately
   ```

### Issue: Poor Quality Results

**Symptom**: OCR text has many errors.

**Causes**:
- Poor scan quality
- Wrong language
- Complex fonts
- Tables or graphics

**Solutions**:
1. **Rescan at higher quality**
2. **Use correct language**: `-l deu` not `-l eng` for German
3. **Increase DPI**: `--dpi 600`
4. **Try multiple languages**: `-l deu+eng`
5. **Check source**: Some documents may not OCR well (handwriting, complex graphics)

---

## Advanced Usage

### Integration with Other Tools

**OCR then Merge**:
```bash
# OCR multiple scanned documents
ocrutil -f scan1.pdf -l deu --output-mode pdf -o scan1_ocr.pdf
ocrutil -f scan2.pdf -l deu --output-mode pdf -o scan2_ocr.pdf

# Merge searchable PDFs
pdfmerge -f "scan1_ocr.pdf,scan2_ocr.pdf" -o complete_searchable.pdf
```

**Split then OCR**:
```bash
# Split large scanned PDF
pdfsplit -i large_scan.pdf -m parts -p 10 -o ./parts/

# OCR each part
for part in ./parts/*.pdf; do
    ocrutil -f "$part" -l eng --output-mode pdf -o "${part%.pdf}_ocr.pdf"
done

# Merge OCR'd parts
pdfmerge -f "./parts/*_ocr.pdf" -o large_scan_complete_ocr.pdf
```

### Python Integration

```python
import subprocess
import json

# Run OCR with JSON output
result = subprocess.run([
    'ocrutil',
    '-f', 'invoice.pdf',
    '-l', 'deu',
    '--output-mode', 'json',
    '-o', 'invoice.json'
], capture_output=True)

if result.returncode == 0:
    # Parse JSON results
    with open('invoice.json', 'r') as f:
        data = json.load(f)

    print(f"Total words: {data['summary']['total_words']}")
    print(f"Confidence: {data['summary']['avg_confidence']:.2%}")
else:
    print("OCR failed:", result.stderr.decode())
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [PDF Merge Tool](pdfmerge.md)
- [PDF Split Tool](pdfsplit.md)
- [Project README](../../README.md)

---

## Support

For issues and questions:

1. Check this troubleshooting section
2. Verify Tesseract installation: `tesseract --version`
3. Check language packs: `tesseract --list-langs`
4. Review [INSTALLATION.md](../../INSTALLATION.md)
5. Search GitHub issues
6. Create a new issue with:
   - Operating system and version
   - Tesseract version
   - Command you ran
   - Error message
   - Sample PDF (if possible)
