# PDF Merge Tool

Merge multiple PDF files into a single document with preserved bookmarks and metadata.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Options](#options)
- [Examples](#examples)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **pdfmerge** tool combines multiple PDF files into a single PDF document. It preserves:
- All pages from source documents
- Bookmarks (optional)
- Document metadata
- Original page formatting and quality

### Key Features

- Merge 2 or more PDF files
- Preserve or discard bookmarks
- Skip corrupted files with `--skip-on-error`
- Performance: < 5s for 10 PDFs with 10 pages each
- Detailed output with page counts and timing
- Support for files with spaces in names

### Requirements

- Python 3.8+
- PyPDF2 library
- Read access to source PDF files
- Write access to output directory

---

## Installation

### Quick Install (Recommended)

**Linux/macOS** - Automated installation:
```bash
git clone https://github.com/yourusername/mcp_pdftools.git
cd mcp_pdftools
./install.sh
```

**Windows** - Follow manual instructions:
```batch
git clone https://github.com/yourusername/mcp_pdftools.git
cd mcp_pdftools
install.bat
```

### Manual Install

If you already have Python and dependencies:

```bash
pip install -e .
```

Or install just the required library:

```bash
pip install PyPDF2>=3.0.1
```

### Complete Guide

See **[Installation Guide](../INSTALLATION.md)** for detailed instructions, troubleshooting, and platform-specific notes.

---

## Usage

### Basic Syntax

```bash
pdfmerge -f "file1.pdf,file2.pdf,file3.pdf" -o output.pdf
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-f, --files` | Comma-separated list of PDF files to merge (minimum 2 files) |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-o, --output` | Output file path | `merged.pdf` in first file's directory |
| `--no-bookmarks` | Don't preserve bookmarks from source PDFs | Bookmarks preserved |
| `--skip-on-error` | Skip corrupted files instead of aborting | Abort on error |
| `-v, --verbose` | Enable detailed output | Disabled |
| `--version` | Show version and exit | - |

---

## Options

### Files (`-f, --files`)

Specify the PDF files to merge as a comma-separated list.

**Requirements**:
- Minimum 2 files
- Files must exist and be readable
- Files must be valid PDF format

**Syntax**:
```bash
-f "file1.pdf,file2.pdf,file3.pdf"
```

**Notes**:
- Use quotes if filenames contain spaces
- Paths can be absolute or relative
- Files are merged in the order specified

### Output (`-o, --output`)

Specify the output file path.

**Default**: `merged.pdf` in the directory of the first input file

**Syntax**:
```bash
-o /path/to/output.pdf
```

**Notes**:
- Parent directory must exist
- Existing files will be overwritten
- Use quotes for paths with spaces

### No Bookmarks (`--no-bookmarks`)

Skip bookmark preservation from source PDFs.

**Use when**:
- Bookmarks are not needed
- Bookmarks cause processing issues
- Reducing output file size

**Syntax**:
```bash
--no-bookmarks
```

### Skip on Error (`--skip-on-error`)

Continue processing if a file is corrupted or unreadable.

**Default behavior**: Abort on first error

**With flag**: Skip problematic files and continue

**Syntax**:
```bash
--skip-on-error
```

**Exit code**: 2 (partial success) when files are skipped

### Verbose (`-v, --verbose`)

Enable detailed logging and output.

**Shows**:
- Processing steps
- File-by-file progress
- Detailed error messages
- Performance metrics

**Syntax**:
```bash
-v
```

---

## Examples

### Example 1: Basic Merge (2 files)

Merge two PDF files into one:

```bash
pdfmerge -f "report_part1.pdf,report_part2.pdf" -o complete_report.pdf
```

**Output**:
```
✓ Successfully merged 2 files
  Output: complete_report.pdf
  Pages: 25
  Time: 0.85s
```

### Example 2: Merge Multiple Files

Combine five PDF documents:

```bash
pdfmerge -f "intro.pdf,chapter1.pdf,chapter2.pdf,chapter3.pdf,conclusion.pdf" -o book.pdf
```

**Output**:
```
✓ Successfully merged 5 files
  Output: book.pdf
  Pages: 342
  Time: 2.14s
```

### Example 3: Files with Spaces in Names

Use quotes for filenames containing spaces:

```bash
pdfmerge -f "Q1 Report.pdf,Q2 Report.pdf,Q3 Report.pdf,Q4 Report.pdf" -o "Annual Report 2024.pdf"
```

### Example 4: Skip Corrupted Files

Continue processing even if some files are corrupted:

```bash
pdfmerge -f "good1.pdf,corrupted.pdf,good2.pdf" --skip-on-error -o output.pdf -v
```

**Output**:
```
⚠ Partial success: Merged 2 files, skipped 1 file
  Output: output.pdf
  Pages: 15
  Skipped: 1 files
    - corrupted.pdf
```

**Exit code**: 2 (partial success)

### Example 5: Merge Without Bookmarks

Merge files without preserving bookmarks:

```bash
pdfmerge -f "doc1.pdf,doc2.pdf,doc3.pdf" --no-bookmarks -o merged.pdf
```

### Example 6: Verbose Output

Enable detailed logging for debugging:

```bash
pdfmerge -f "file1.pdf,file2.pdf" -o output.pdf -v
```

**Verbose Output**:
```
DEBUG: Processing file 1/2: file1.pdf (12 pages)
DEBUG: Processing file 2/2: file2.pdf (8 pages)
DEBUG: Merging bookmarks...
DEBUG: Writing output file: output.pdf
✓ Successfully merged 2 files
  Output: output.pdf
  Pages: 20
  Time: 0.92s
```

### Example 7: Default Output Path

Let the tool choose the output filename:

```bash
pdfmerge -f "invoice_jan.pdf,invoice_feb.pdf,invoice_mar.pdf"
```

**Output**: Creates `merged.pdf` in the directory of `invoice_jan.pdf`

### Example 8: Absolute Paths

Use absolute paths for files in different directories:

```bash
pdfmerge -f "/home/user/docs/file1.pdf,/tmp/file2.pdf,/opt/data/file3.pdf" -o /home/user/output.pdf
```

### Example 9: Large File Merge

Merge many large PDF files:

```bash
pdfmerge -f "annual_report_2020.pdf,annual_report_2021.pdf,annual_report_2022.pdf,annual_report_2023.pdf" -o reports_2020-2023.pdf -v
```

### Example 10: Workflow Integration

Use in a shell script for batch processing:

```bash
#!/bin/bash
# Merge all PDFs in current directory

FILES=$(ls -1 *.pdf | tr '\n' ',' | sed 's/,$//')
pdfmerge -f "$FILES" -o all_merged.pdf
```

---

## Common Use Cases

### 1. Report Consolidation

**Scenario**: Combine multiple report sections into one document.

```bash
pdfmerge -f "executive_summary.pdf,methodology.pdf,results.pdf,conclusions.pdf,appendix.pdf" -o final_report.pdf
```

### 2. Invoice Archiving

**Scenario**: Merge monthly invoices into a quarterly archive.

```bash
pdfmerge -f "invoice_jan.pdf,invoice_feb.pdf,invoice_mar.pdf" -o Q1_2024_invoices.pdf
```

### 3. Document Assembly

**Scenario**: Assemble contract documents with exhibits.

```bash
pdfmerge -f "contract.pdf,exhibit_a.pdf,exhibit_b.pdf,signatures.pdf" -o complete_contract.pdf
```

### 4. Presentation Merging

**Scenario**: Combine presentations from multiple speakers.

```bash
pdfmerge -f "intro.pdf,speaker1.pdf,speaker2.pdf,speaker3.pdf,qa.pdf" -o conference_2024.pdf
```

### 5. Book Compilation

**Scenario**: Merge book chapters into a complete manuscript.

```bash
pdfmerge -f "cover.pdf,toc.pdf,chapter1.pdf,chapter2.pdf,chapter3.pdf,references.pdf" -o manuscript.pdf
```

### 6. Scanned Document Assembly

**Scenario**: Merge scanned pages into a single document.

```bash
pdfmerge -f "scan_001.pdf,scan_002.pdf,scan_003.pdf" --skip-on-error -o document.pdf
```

---

## Exit Codes

The tool returns standard exit codes:

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | All files merged successfully |
| 1 | Error | Critical error occurred (file not found, invalid PDF, etc.) |
| 2 | Partial | Some files merged, some skipped (with `--skip-on-error`) |

### Example: Checking Exit Code

```bash
pdfmerge -f "file1.pdf,file2.pdf" -o output.pdf
if [ $? -eq 0 ]; then
    echo "Merge successful!"
else
    echo "Merge failed!"
fi
```

---

## Performance

### Benchmarks

Tested on standard hardware (Intel i5, 8GB RAM, SSD):

| Files | Total Pages | Time | Pages/sec |
|-------|-------------|------|-----------|
| 2 | 20 | 0.5s | 40 |
| 5 | 50 | 1.2s | 42 |
| 10 | 100 | 2.3s | 43 |
| 20 | 200 | 4.5s | 44 |
| 50 | 500 | 11.2s | 45 |

### Performance Tips

1. **Use SSD storage** for faster I/O
2. **Process in batches** for very large jobs
3. **Disable bookmarks** if not needed (`--no-bookmarks`)
4. **Use verbose mode** (`-v`) to monitor progress on large jobs
5. **Close other applications** to free up RAM

---

## Troubleshooting

### Error: "No files specified"

**Cause**: The `-f` argument is missing or empty.

**Solution**:
```bash
# Correct usage
pdfmerge -f "file1.pdf,file2.pdf" -o output.pdf
```

### Error: "File not found"

**Cause**: One or more input files don't exist.

**Solution**:
```bash
# Check if files exist
ls -l file1.pdf file2.pdf

# Use absolute paths
pdfmerge -f "/full/path/to/file1.pdf,/full/path/to/file2.pdf" -o output.pdf
```

### Error: "Minimum 2 files required"

**Cause**: Only one file specified in `-f` argument.

**Solution**:
```bash
# Provide at least 2 files
pdfmerge -f "file1.pdf,file2.pdf" -o output.pdf
```

### Error: "Invalid PDF file"

**Cause**: One or more files are corrupted or not valid PDFs.

**Solution**:
```bash
# Use --skip-on-error to skip bad files
pdfmerge -f "file1.pdf,corrupted.pdf,file3.pdf" --skip-on-error -o output.pdf

# Or fix the corrupted PDF first
```

### Error: "Permission denied"

**Cause**: No write permission for output directory.

**Solution**:
```bash
# Check directory permissions
ls -ld /path/to/output/

# Choose a different output directory
pdfmerge -f "file1.pdf,file2.pdf" -o ~/Documents/output.pdf
```

### Error: "Out of memory"

**Cause**: PDFs are too large for available RAM.

**Solution**:
- Close other applications
- Process files in smaller batches
- Upgrade system RAM

### Warning: Slow Performance

**Symptoms**: Merge takes longer than expected.

**Solutions**:
1. Check disk I/O (move files to SSD)
2. Reduce concurrent processes
3. Use `--no-bookmarks` flag
4. Process in smaller batches

### Issue: Bookmarks Not Preserved

**Cause**: Bookmarks were removed or corrupted.

**Solutions**:
```bash
# Make sure you're NOT using --no-bookmarks
pdfmerge -f "file1.pdf,file2.pdf" -o output.pdf

# Check if source PDFs actually have bookmarks
```

### Issue: Output File is Too Large

**Cause**: Merged PDF contains high-resolution images or uncompressed content.

**Solutions**:
- Use a PDF compression tool after merging
- Optimize source PDFs before merging
- Consider using `--no-bookmarks` to reduce size slightly

---

## Advanced Usage

### Integration with Other Tools

**Combine with pdfsplit**:
```bash
# Split a PDF
pdfsplit -i large.pdf -o ./pages/

# Merge specific pages
pdfmerge -f "./pages/large_page_1.pdf,./pages/large_page_5.pdf,./pages/large_page_10.pdf" -o selected.pdf
```

**Combine with OCR**:
```bash
# OCR multiple scanned PDFs
ocrutil -f scan1.pdf -o scan1_ocr.pdf
ocrutil -f scan2.pdf -o scan2_ocr.pdf

# Merge OCR'd PDFs
pdfmerge -f "scan1_ocr.pdf,scan2_ocr.pdf" -o combined_searchable.pdf
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [PDF Split Tool](pdfsplit.md)
- [OCR Tool](ocrutil.md)
- [Project README](../../README.md)

---

## Support

For issues and questions:

1. Check this troubleshooting section
2. Review [INSTALLATION.md](../../INSTALLATION.md)
3. Search GitHub issues
4. Create a new issue with details
