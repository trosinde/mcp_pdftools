# PDF Split Tool

Split PDF files into multiple parts using various splitting modes.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Split Modes](#split-modes)
- [Options](#options)
- [Examples](#examples)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **pdfsplit** tool divides PDF files into multiple smaller PDF files. It supports four different splitting modes to handle various use cases.

### Key Features

- **4 Split Modes**: PAGES, RANGES, PARTS, SPECIFIC_PAGES
- Split by individual pages
- Split by page ranges
- Split into equal parts
- Extract specific pages
- Customizable output filenames
- Verbose progress reporting
- Support for large PDFs

### Requirements

- Python 3.8+
- pdfrw library
- Read access to source PDF
- Write access to output directory

---

## Installation

Install MCP PDF Tools package:

```bash
pip install -e .
```

Or install just the dependencies:

```bash
pip install pdfrw>=0.4
```

See [INSTALLATION.md](../../INSTALLATION.md) for detailed installation instructions.

---

## Usage

### Basic Syntax

```bash
pdfsplit -i input.pdf -o ./output/ -m MODE [mode-specific options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-i, --input` | Input PDF file to split |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-o, --output-dir` | Output directory for split files | Current directory (`.`) |
| `-m, --mode` | Split mode: `pages`, `ranges`, `parts`, `specific` | `pages` |
| `-r, --ranges` | Page ranges for RANGES mode | - |
| `-p, --parts` | Number of parts for PARTS mode | - |
| `--pages` | Specific pages for SPECIFIC mode | - |
| `--prefix` | Custom prefix for output files | Input filename |
| `-v, --verbose` | Enable verbose output | Disabled |
| `--version` | Show version and exit | - |

---

## Split Modes

### 1. PAGES Mode (Default)

Splits PDF into individual pages, one page per file.

**Usage**:
```bash
pdfsplit -i document.pdf -m pages
```

**Output**:
```
document_page_1.pdf
document_page_2.pdf
document_page_3.pdf
...
```

**When to use**:
- Need individual pages as separate files
- Processing pages independently
- Extracting all pages for review

---

### 2. RANGES Mode

Splits PDF into multiple files based on specified page ranges.

**Usage**:
```bash
pdfsplit -i document.pdf -m ranges -r "1-5,10-15,20-25"
```

**Output**:
```
document_range_1-5.pdf    (pages 1-5)
document_range_10-15.pdf  (pages 10-15)
document_range_20-25.pdf  (pages 20-25)
```

**When to use**:
- Extracting specific chapters
- Splitting by logical sections
- Custom page groupings

**Range Syntax**:
- Single range: `"1-10"`
- Multiple ranges: `"1-5,10-15,20-25"`
- Spaces allowed: `"1-5, 10-15, 20-25"`

---

### 3. PARTS Mode

Splits PDF into N equal parts (or as equal as possible).

**Usage**:
```bash
pdfsplit -i document.pdf -m parts -p 5
```

**Example**: 23-page PDF split into 5 parts:
```
document_part_1.pdf  (pages 1-5,   5 pages)
document_part_2.pdf  (pages 6-10,  5 pages)
document_part_3.pdf  (pages 11-15, 5 pages)
document_part_4.pdf  (pages 16-19, 4 pages)
document_part_5.pdf  (pages 20-23, 4 pages)
```

**When to use**:
- Distributing work among team members
- Splitting for parallel processing
- Creating equal-sized chunks

**Note**: If pages don't divide evenly, later parts will have fewer pages.

---

### 4. SPECIFIC_PAGES Mode

Extracts only specified page numbers into separate files.

**Usage**:
```bash
pdfsplit -i document.pdf -m specific --pages "1,5,10,15"
```

**Output**:
```
document_page_1.pdf   (only page 1)
document_page_5.pdf   (only page 5)
document_page_10.pdf  (only page 10)
document_page_15.pdf  (only page 15)
```

**When to use**:
- Extracting specific important pages
- Creating a subset of pages
- Removing unnecessary pages

**Page Syntax**:
- Comma-separated: `"1,5,10,15"`
- Spaces allowed: `"1, 5, 10, 15"`

---

## Options

### Input (`-i, --input`)

Path to the PDF file to split.

**Requirements**:
- File must exist
- File must be a valid PDF
- Read permission required

**Syntax**:
```bash
-i /path/to/document.pdf
```

### Output Directory (`-o, --output-dir`)

Directory where split files will be saved.

**Default**: Current directory (`.`)

**Syntax**:
```bash
-o /path/to/output/
```

**Notes**:
- Directory will be created if it doesn't exist
- Existing files with same names will be overwritten

### Mode (`-m, --mode`)

Splitting mode to use.

**Choices**: `pages`, `ranges`, `parts`, `specific`

**Default**: `pages`

**Syntax**:
```bash
-m ranges
```

### Ranges (`-r, --ranges`)

Page ranges for RANGES mode.

**Required**: Only for `ranges` mode

**Syntax**:
```bash
-r "1-5,10-15,20-25"
```

**Format**:
- Ranges: `start-end`
- Multiple ranges: separated by commas
- Spaces are optional

### Parts (`-p, --parts`)

Number of parts for PARTS mode.

**Required**: Only for `parts` mode

**Syntax**:
```bash
-p 5
```

**Constraints**:
- Must be a positive integer
- Must be ≤ total number of pages

### Pages (`--pages`)

Specific page numbers for SPECIFIC mode.

**Required**: Only for `specific` mode

**Syntax**:
```bash
--pages "1,5,10,15"
```

**Format**:
- Comma-separated page numbers
- Spaces are optional
- Page numbers must exist in PDF

### Prefix (`--prefix`)

Custom prefix for output filenames.

**Default**: Input filename (without extension)

**Syntax**:
```bash
--prefix "chapter"
```

**Example**:
```bash
pdfsplit -i book.pdf -m pages --prefix "chapter"
# Output: chapter_page_1.pdf, chapter_page_2.pdf, ...
```

### Verbose (`-v, --verbose`)

Enable detailed progress output.

**Syntax**:
```bash
-v
```

**Shows**:
- Processing progress
- File-by-file status
- Total pages and files created

---

## Examples

### Example 1: Split into Individual Pages

Split each page into a separate file:

```bash
pdfsplit -i report.pdf -o ./pages/
```

**Output** (for 10-page PDF):
```
./pages/report_page_1.pdf
./pages/report_page_2.pdf
...
./pages/report_page_10.pdf
```

### Example 2: Split by Page Ranges

Extract specific page ranges:

```bash
pdfsplit -i book.pdf -m ranges -r "1-10,50-75,100-125" -o ./chapters/
```

**Output**:
```
./chapters/book_range_1-10.pdf
./chapters/book_range_50-75.pdf
./chapters/book_range_100-125.pdf
```

**Use case**: Extracting chapters from a book.

### Example 3: Split into Equal Parts

Divide a 100-page document into 4 parts:

```bash
pdfsplit -i document.pdf -m parts -p 4 -o ./parts/
```

**Output**:
```
./parts/document_part_1.pdf  (pages 1-25)
./parts/document_part_2.pdf  (pages 26-50)
./parts/document_part_3.pdf  (pages 51-75)
./parts/document_part_4.pdf  (pages 76-100)
```

### Example 4: Extract Specific Pages

Extract only pages 1, 5, 10, and 20:

```bash
pdfsplit -i presentation.pdf -m specific --pages "1,5,10,20" -o ./selected/
```

**Output**:
```
./selected/presentation_page_1.pdf
./selected/presentation_page_5.pdf
./selected/presentation_page_10.pdf
./selected/presentation_page_20.pdf
```

### Example 5: Custom Output Prefix

Use a custom prefix for output files:

```bash
pdfsplit -i contract.pdf -m pages --prefix "contract_section" -o ./sections/
```

**Output**:
```
./sections/contract_section_page_1.pdf
./sections/contract_section_page_2.pdf
...
```

### Example 6: Verbose Output

Monitor progress with verbose mode:

```bash
pdfsplit -i large_document.pdf -m pages -v
```

**Verbose Output**:
```
Processing: large_document.pdf
Total pages: 250
Mode: PAGES

Created: large_document_page_1.pdf
Created: large_document_page_2.pdf
...
Created: large_document_page_250.pdf

✓ Split successful: 250 files created
```

### Example 7: Complex Range Split

Split with multiple non-contiguous ranges:

```bash
pdfsplit -i manual.pdf -m ranges -r "1-3,10-25,50-55,100-150" -o ./sections/ -v
```

### Example 8: Single Range

Extract just one range of pages:

```bash
pdfsplit -i thesis.pdf -m ranges -r "25-50" -o ./chapter2/
```

**Output**:
```
./chapter2/thesis_range_25-50.pdf
```

### Example 9: Many Parts

Split a 500-page document into 20 parts:

```bash
pdfsplit -i large.pdf -m parts -p 20 -o ./parts/
```

**Each part**: ~25 pages

### Example 10: Current Directory Output

Output to current directory (default):

```bash
pdfsplit -i document.pdf -m pages
```

**Output** (in current directory):
```
./document_page_1.pdf
./document_page_2.pdf
...
```

---

## Common Use Cases

### 1. Chapter Extraction

**Scenario**: Extract chapters from a book.

```bash
pdfsplit -i textbook.pdf -m ranges -r "1-25,26-50,51-75,76-100" --prefix "chapter" -o ./chapters/
```

**Output**:
```
./chapters/chapter_range_1-25.pdf
./chapters/chapter_range_26-50.pdf
./chapters/chapter_range_51-75.pdf
./chapters/chapter_range_76-100.pdf
```

### 2. Distribute Work

**Scenario**: Split a document for parallel processing by 5 team members.

```bash
pdfsplit -i project.pdf -m parts -p 5 -o ./team_assignments/
```

### 3. Extract Cover and Summary

**Scenario**: Extract first and last pages of a report.

```bash
pdfsplit -i report.pdf -m specific --pages "1,50" -o ./summary/
```

### 4. Page-by-Page Review

**Scenario**: Review each page individually.

```bash
pdfsplit -i contract.pdf -m pages -o ./review/
```

### 5. Section Extraction

**Scenario**: Extract specific sections from a manual.

```bash
pdfsplit -i manual.pdf -m ranges -r "1-10,45-60,100-120" --prefix "section" -o ./extracted/
```

### 6. Batch Processing Preparation

**Scenario**: Split large PDF for OCR processing in batches.

```bash
# Split into parts
pdfsplit -i scanned.pdf -m parts -p 10 -o ./batches/

# OCR each part separately
for file in ./batches/*.pdf; do
    ocrutil -f "$file" -o "${file%.pdf}_ocr.pdf"
done
```

### 7. Quality Check

**Scenario**: Extract every 10th page for quality verification.

```bash
pdfsplit -i document.pdf -m specific --pages "10,20,30,40,50" -o ./qc/
```

---

## Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | Split completed successfully |
| 1 | Error | Error occurred (invalid input, file not found, etc.) |
| 130 | Cancelled | Operation cancelled by user (Ctrl+C) |

---

## Performance

### Benchmarks

Tested on standard hardware (Intel i5, 8GB RAM, SSD):

| Mode | Pages | Output Files | Time | Pages/sec |
|------|-------|--------------|------|-----------|
| PAGES | 50 | 50 | 2.1s | 24 |
| PAGES | 100 | 100 | 4.3s | 23 |
| PAGES | 500 | 500 | 22.5s | 22 |
| RANGES | 100 | 5 | 1.8s | 56 |
| PARTS | 100 | 10 | 2.0s | 50 |
| SPECIFIC | 100 | 10 | 1.5s | 67 |

### Performance Tips

1. **Use RANGES or PARTS** instead of PAGES for fewer output files
2. **SSD storage** significantly faster than HDD
3. **Verbose mode** adds minimal overhead
4. **Network drives** can be slow - use local storage
5. **Large PDFs** (1000+ pages) may take several minutes

---

## Troubleshooting

### Error: "Input file not found"

**Cause**: The specified PDF file doesn't exist.

**Solution**:
```bash
# Check file exists
ls -l document.pdf

# Use absolute path
pdfsplit -i /full/path/to/document.pdf -o ./output/
```

### Error: "Invalid PDF file"

**Cause**: The file is corrupted or not a valid PDF.

**Solution**:
- Open the file in a PDF reader to verify
- Try repairing the PDF
- Use a different PDF file

### Error: "--ranges required for RANGES mode"

**Cause**: RANGES mode selected but no ranges specified.

**Solution**:
```bash
pdfsplit -i doc.pdf -m ranges -r "1-10,20-30"
```

### Error: "--parts required for PARTS mode"

**Cause**: PARTS mode selected but number of parts not specified.

**Solution**:
```bash
pdfsplit -i doc.pdf -m parts -p 5
```

### Error: "--pages required for SPECIFIC mode"

**Cause**: SPECIFIC mode selected but no pages specified.

**Solution**:
```bash
pdfsplit -i doc.pdf -m specific --pages "1,5,10"
```

### Error: "Invalid page numbers"

**Cause**: Page numbers are not valid integers.

**Solution**:
```bash
# Correct format
pdfsplit -i doc.pdf -m specific --pages "1,5,10,15"

# NOT: "1-5" (that's for ranges mode)
# NOT: "1.5,2.3" (must be integers)
```

### Error: "Invalid range format"

**Cause**: Range syntax is incorrect.

**Solution**:
```bash
# Correct formats
-r "1-10"
-r "1-10,20-30,40-50"

# Incorrect formats (will fail)
-r "10-1"     # Start > End
-r "abc-def"  # Not numbers
```

### Error: "Permission denied"

**Cause**: No write permission for output directory.

**Solution**:
```bash
# Check directory permissions
ls -ld ./output/

# Create directory first
mkdir -p ./output/

# Or use a directory you own
pdfsplit -i doc.pdf -o ~/Documents/output/
```

### Warning: "Output directory created"

**Not an error**: The output directory didn't exist and was created automatically.

### Issue: Output Files Not Created

**Possible causes**:
1. Insufficient disk space
2. Permission issues
3. Invalid page ranges

**Solution**:
```bash
# Check disk space
df -h

# Check permissions
ls -ld ./output/

# Use verbose mode to see what's happening
pdfsplit -i doc.pdf -o ./output/ -v
```

### Issue: Slow Performance

**Symptoms**: Processing takes longer than expected.

**Solutions**:
1. Use SSD instead of HDD
2. Don't output to network drives
3. Process smaller files or fewer pages
4. Close other applications

### Issue: Wrong Page Range

**Symptom**: Got different pages than expected.

**Cause**: Page numbers in PDFs are 1-indexed.

**Example**:
```bash
# Pages 1-10 means pages 1, 2, 3, ..., 10
pdfsplit -i doc.pdf -m ranges -r "1-10"

# NOT pages 0-9 (page 0 doesn't exist)
```

---

## Advanced Usage

### Workflow Integration

**Extract and Merge**:
```bash
# Extract specific ranges
pdfsplit -i large.pdf -m ranges -r "1-10,50-60" -o ./temp/

# Merge them back in different order
pdfmerge -f "./temp/large_range_50-60.pdf,./temp/large_range_1-10.pdf" -o reordered.pdf
```

**Split and OCR**:
```bash
# Split into parts
pdfsplit -i scanned.pdf -m parts -p 5 -o ./parts/

# OCR each part
for file in ./parts/*.pdf; do
    ocrutil -f "$file" -l deu
done
```

### Bash Script Example

```bash
#!/bin/bash
# Split all PDFs in a directory

for pdf in *.pdf; do
    echo "Processing: $pdf"
    pdfsplit -i "$pdf" -m pages -o "./split_${pdf%.pdf}/"
done

echo "All PDFs split successfully!"
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [PDF Merge Tool](pdfmerge.md)
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
   - PDF file details (pages, size)
   - Error messages
