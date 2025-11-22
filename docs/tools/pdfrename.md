# PDF Invoice Renaming Tool

Intelligently rename invoice PDFs based on extracted data (vendor, invoice number, date) using pattern-based extraction.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Template System](#template-system)
- [Pattern-Based Extraction](#pattern-based-extraction)
- [Options](#options)
- [Examples](#examples)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **pdfrename** tool automatically renames invoice PDF files using intelligent data extraction. It reads the PDF content, extracts key information (vendor name, invoice number, date), and renames the file according to a customizable template.

### Key Features

- **Intelligent Extraction**: Automatically detects vendor, invoice number, and date
- **Template System**: Flexible naming templates with placeholders
- **Pattern-Based**: Uses regex patterns for data extraction
- **Vendor-Specific Patterns**: Built-in support for Amazon, PayPal, eBay, Stripe
- **Custom Patterns**: Load custom extraction patterns from JSON
- **Batch Processing**: Rename multiple files with wildcard support
- **Dry-Run Mode**: Preview renames without actually renaming files
- **Duplicate Handling**: Automatic suffix for duplicate filenames
- **Verbose Logging**: Detailed extraction and renaming information

### Requirements

- Python 3.8+
- PyPDF2 or pdfplumber library
- Read/write access to PDF files
- Valid PDF invoices with extractable text

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

### Complete Guide

See **[Installation Guide](../INSTALLATION.md)** for detailed instructions, troubleshooting, and platform-specific notes.

---

## Usage

### Basic Syntax

```bash
pdfrename -f invoice.pdf [-t TEMPLATE] [-o OUTPUT_DIR] [options]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-f, --files` | PDF file(s) to rename (supports wildcards like `*.pdf`) |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-t, --template` | Naming template with placeholders | `{vendor}_{invoice_nr}_{date}.pdf` |
| `-p, --patterns` | Path to custom patterns JSON file | Built-in patterns |
| `-o, --output-dir` | Output directory | Same as input |
| `-d, --dry-run` | Simulate rename without actually renaming | Disabled |
| `--no-duplicates` | Error on duplicate filenames instead of adding suffix | Add suffix |
| `--verbose` | Enable verbose output | Disabled |

---

## Template System

### Template Placeholders

The renaming template supports the following placeholders:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{vendor}` | Vendor/supplier name | `Amazon`, `PayPal` |
| `{invoice_nr}` | Invoice/order number | `INV-12345`, `123-4567890-1234567` |
| `{date}` | Full date (YYYY-MM-DD) | `2024-03-15` |
| `{year}` | Year only | `2024` |
| `{month}` | Month only (01-12) | `03` |
| `{day}` | Day only (01-31) | `15` |

### Default Template

```
{vendor}_{invoice_nr}_{date}.pdf
```

**Example**: `Amazon_123-4567890-1234567_2024-03-15.pdf`

---

### Template Examples

#### Business Format

```bash
-t "{vendor}_{invoice_nr}_{date}.pdf"
```

**Output**: `PayPal_AB123456789012345_2024-03-15.pdf`

---

#### Accounting Format

```bash
-t "{date}_{vendor}_{invoice_nr}.pdf"
```

**Output**: `2024-03-15_Amazon_123-4567890-1234567.pdf`

**Use case**: Chronological filing

---

#### Compact Format

```bash
-t "{year}{month}{day}_{vendor}_{invoice_nr}.pdf"
```

**Output**: `20240315_eBay_12-34567-89012.pdf`

**Use case**: Sortable filenames

---

#### Vendor-First Format

```bash
-t "{vendor}/{year}/{invoice_nr}.pdf"
```

**Output**: `Amazon/2024/123-4567890-1234567.pdf`

**Note**: Creates directory structure

---

#### Simple Format

```bash
-t "{vendor}_{invoice_nr}.pdf"
```

**Output**: `Stripe_inv_ABC123DEF456.pdf`

**Use case**: When date is not needed

---

### Date Formatting

The tool automatically converts various date formats to `YYYY-MM-DD`:

| Input Format | Example | Output |
|--------------|---------|--------|
| ISO 8601 | `2024-03-15` | `2024-03-15` |
| German | `15.03.2024` | `2024-03-15` |
| US | `03/15/2024` | `2024-03-15` |
| Named month | `15 March 2024` | `2024-03-15` |

---

## Pattern-Based Extraction

### Built-in Patterns

The tool includes default regex patterns for:

#### Invoice Number Patterns

Matches various formats:
- `Invoice Number: 12345`
- `Rechnung Nr. ABC-123`
- `Bill #: 001`
- `Faktura ID: INV-2024-001`

**Pattern**:
```regex
(?:Invoice|Rechnung|Bill|Faktura)\s*
(?:Number|Nr\.?|#|ID)?\s*:?\s*
([A-Z0-9][A-Z0-9\-_/.]{2,30})
```

---

#### Date Patterns

Supports multiple formats:
- ISO: `2024-03-15`
- German: `15.03.2024`
- US: `03/15/2024`
- Named: `15 March 2024`

**Pattern**:
```regex
(?:Date|Datum|Invoice\s+Date)\s*:?\s*
(\d{4}-\d{2}-\d{2}|
 \d{2}\.\d{2}\.\d{4}|
 \d{2}/\d{2}/\d{4}|
 \d{1,2}\s+(?:Jan|Feb|...|Dec)[a-z]*\s+\d{4})
```

---

#### Vendor Patterns

Extracts vendor names:
- `From: Amazon`
- `Vendor: PayPal Inc.`
- `Supplier: Acme Corp`

**Pattern**:
```regex
(?:From|Von|Vendor|Supplier|Seller)\s*:?\s*
([A-Z][a-zA-Z0-9\s&\.,\-]{2,40})
```

---

### Vendor-Specific Patterns

Built-in support for popular platforms:

#### Amazon

```bash
# Automatically detects Amazon invoices
pdfrename -f amazon_invoice.pdf
```

**Patterns**:
- Invoice Nr: `123-4567890-1234567`
- Date: Various Amazon formats
- Vendor: `Amazon.com`, `Amazon.de`, etc.

---

#### PayPal

**Patterns**:
- Transaction ID: `AB123456789012345` (17 chars)
- Date: PayPal date formats
- Vendor: `PayPal`

---

#### eBay

**Patterns**:
- Order number: `12-34567-89012`
- Date: eBay date formats
- Vendor: `eBay`

---

#### Stripe

**Patterns**:
- Invoice/Receipt: `inv_ABC123DEF456`
- Date: Stripe date formats
- Vendor: `Stripe`

---

### Custom Patterns

Create a JSON file with custom extraction patterns:

**patterns.json**:
```json
{
  "invoice_nr": "Order\\s+#?\\s*:?\\s*(\\d{5,10})",
  "date": "Invoice\\s+Date\\s*:?\\s*(\\d{4}-\\d{2}-\\d{2})",
  "vendor": "Company\\s+Name\\s*:?\\s*([A-Z][a-zA-Z\\s]+)"
}
```

**Usage**:
```bash
pdfrename -f invoice.pdf -p patterns.json
```

**Note**: Patterns use Python regex syntax. Backslashes must be escaped in JSON.

---

## Options

### Files (`-f, --files`)

PDF file(s) to rename.

**Syntax**:
```bash
-f invoice.pdf
-f "invoices/*.pdf"
-f "2024_*.pdf"
```

**Wildcard Support**:
- `*.pdf`: All PDFs in current directory
- `invoices/*.pdf`: All PDFs in invoices directory
- `2024_*.pdf`: PDFs starting with "2024_"
- `**/*.pdf`: Recursive search (all subdirectories)

### Template (`-t, --template`)

Naming template with placeholders.

**Default**: `{vendor}_{invoice_nr}_{date}.pdf`

**Syntax**:
```bash
-t "{date}_{vendor}_{invoice_nr}.pdf"
```

**Notes**:
- Must include `.pdf` extension
- Use quotes if template contains spaces
- At least one placeholder recommended

### Patterns (`-p, --patterns`)

Path to custom patterns JSON file.

**Syntax**:
```bash
-p patterns.json
-p /path/to/custom_patterns.json
```

**JSON Structure**:
```json
{
  "invoice_nr": "regex_pattern",
  "date": "regex_pattern",
  "vendor": "regex_pattern"
}
```

### Output Directory (`-o, --output-dir`)

Directory for renamed files.

**Default**: Same directory as input file

**Syntax**:
```bash
-o /path/to/renamed/
-o ./organized/
```

**Notes**:
- Directory created if doesn't exist
- Preserves subdirectory structure for wildcards

### Dry-Run (`-d, --dry-run`)

Preview renames without actually renaming files.

**Syntax**:
```bash
-d
```

**Output**:
```
Processing 5 files...
invoice_march.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
paypal_receipt.pdf -> PayPal_AB123456789012345_2024-03-10.pdf
...
[DRY RUN - No files were renamed]
```

**Use case**: Verify renaming before committing

### No Duplicates (`--no-duplicates`)

Error on duplicate filenames instead of adding suffix.

**Default behavior**: Add suffix `_1`, `_2`, etc.

**With flag**: Fail on duplicate

**Syntax**:
```bash
--no-duplicates
```

### Verbose (`--verbose`)

Enable detailed logging.

**Syntax**:
```bash
--verbose
```

**Shows**:
- Extracted data per file
- Pattern matching details
- Renaming steps
- Error details

---

## Examples

### Example 1: Basic Rename (Single File)

Rename a single invoice with default template:

```bash
pdfrename -f invoice_march_2024.pdf
```

**Output**:
```
invoice_march_2024.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
```

### Example 2: Custom Template

Use custom naming format:

```bash
pdfrename -f invoice.pdf -t "{date}_{vendor}_{invoice_nr}.pdf"
```

**Output**:
```
invoice.pdf -> 2024-03-15_PayPal_AB123456789012345.pdf
```

### Example 3: Batch Processing

Rename all PDFs in directory:

```bash
pdfrename -f "invoices/*.pdf"
```

**Output**:
```
Processing 15 files...
invoice_001.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
invoice_002.pdf -> PayPal_AB123456789012345_2024-03-10.pdf
...
Summary:
  Total files:      15
  Successful:       14
  Failed:           1
```

### Example 4: Dry-Run Mode

Preview renames before executing:

```bash
pdfrename -f "*.pdf" -d
```

**Output**:
```
Processing 5 files...
invoice_1.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
invoice_2.pdf -> eBay_12-34567-89012_2024-03-14.pdf
invoice_3.pdf -> Stripe_inv_ABC123_2024-03-13.pdf

[DRY RUN - No files were renamed]

Summary:
  Total files:      3
  Successful:       3
  Failed:           0
```

### Example 5: Custom Output Directory

Move renamed files to organized directory:

```bash
pdfrename -f "downloads/*.pdf" -o "./organized_invoices/"
```

**Result**: Renames and moves files to `./organized_invoices/`

### Example 6: Custom Patterns

Use custom extraction patterns:

```bash
pdfrename -f company_invoice.pdf -p patterns.json
```

**patterns.json**:
```json
{
  "invoice_nr": "PO\\s+Number\\s*:?\\s*(\\d{6})",
  "date": "Date\\s+Issued\\s*:?\\s*(\\d{4}-\\d{2}-\\d{2})",
  "vendor": "Vendor\\s+Name\\s*:?\\s*([A-Z][a-zA-Z\\s]+)"
}
```

### Example 7: Verbose Output

Monitor extraction process:

```bash
pdfrename -f invoice.pdf --verbose
```

**Verbose Output**:
```
DEBUG: Processing file: invoice.pdf
DEBUG: Extracting text from PDF...
DEBUG: Text extracted: 523 characters
DEBUG: Searching for invoice number...
DEBUG: Found invoice_nr: 123-4567890-1234567
DEBUG: Searching for date...
DEBUG: Found date: 2024-03-15
DEBUG: Searching for vendor...
DEBUG: Found vendor: Amazon
DEBUG: Applying template: {vendor}_{invoice_nr}_{date}.pdf
DEBUG: New filename: Amazon_123-4567890-1234567_2024-03-15.pdf
DEBUG: Renaming file...

invoice.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
```

### Example 8: Date-First Format

Organize by date:

```bash
pdfrename -f "*.pdf" -t "{year}/{month}/{vendor}_{invoice_nr}.pdf" -o "./archive/"
```

**Output** (creates directory structure):
```
./archive/2024/03/Amazon_123-4567890-1234567.pdf
./archive/2024/03/PayPal_AB123456789012345.pdf
./archive/2024/02/eBay_12-34567-89012.pdf
```

### Example 9: Simple Vendor-Number Format

Minimal naming:

```bash
pdfrename -f invoice.pdf -t "{vendor}_{invoice_nr}.pdf"
```

**Output**:
```
invoice.pdf -> Stripe_inv_ABC123DEF456.pdf
```

### Example 10: Batch with Error Handling

Process multiple files with error reporting:

```bash
pdfrename -f "invoices/*.pdf" --verbose
```

**Output**:
```
Processing 10 files...
invoice_1.pdf -> Amazon_123-4567890-1234567_2024-03-15.pdf
invoice_2.pdf: ERROR - Could not extract invoice number
invoice_3.pdf -> PayPal_AB123456789012345_2024-03-10.pdf
...

Summary:
  Total files:      10
  Successful:       9
  Failed:           1

Failed files:
  invoice_2.pdf: Could not extract invoice number
```

### Example 11: Wildcard Pattern Matching

Rename specific pattern:

```bash
pdfrename -f "invoice_2024_*.pdf" -t "{vendor}_{invoice_nr}_{date}.pdf"
```

### Example 12: No Duplicate Suffix

Fail on duplicates instead of adding suffix:

```bash
pdfrename -f "*.pdf" --no-duplicates
```

**Behavior**: If duplicate filename detected, reports error instead of adding `_1`, `_2`, etc.

---

## Common Use Cases

### 1. Accounting Invoice Organization

**Scenario**: Organize downloaded invoices for accounting.

```bash
pdfrename -f "~/Downloads/*.pdf" -t "{date}_{vendor}_{invoice_nr}.pdf" -o "./invoices/2024/"
```

**Result**: Chronologically organized invoices

### 2. Vendor-Based Filing

**Scenario**: Organize by vendor with date.

```bash
pdfrename -f "*.pdf" -t "{vendor}/{year}/{invoice_nr}_{date}.pdf" -o "./organized/"
```

**Result**:
```
./organized/Amazon/2024/123-4567890-1234567_2024-03-15.pdf
./organized/PayPal/2024/AB123456789012345_2024-03-10.pdf
./organized/eBay/2024/12-34567-89012_2024-03-08.pdf
```

### 3. Monthly Batch Processing

**Scenario**: Process all invoices from a month.

```bash
#!/bin/bash
pdfrename -f "~/Downloads/invoice*.pdf" \
          -t "{vendor}_{invoice_nr}_{date}.pdf" \
          -o "./invoices/$(date +%Y-%m)/" \
          --verbose
```

### 4. Tax Preparation

**Scenario**: Organize invoices for tax filing.

```bash
pdfrename -f "*.pdf" -t "{year}/{vendor}_{invoice_nr}_{month}_{day}.pdf" -o "./taxes/2024/"
```

### 5. E-commerce Order Management

**Scenario**: Rename Amazon, eBay, PayPal orders.

```bash
pdfrename -f "order_*.pdf" -t "{vendor}_{invoice_nr}_{date}.pdf" -o "./orders/"
```

**Automatic vendor detection**: Uses vendor-specific patterns

### 6. Custom Company Invoices

**Scenario**: Company uses custom invoice format.

**patterns.json**:
```json
{
  "invoice_nr": "Reference\\s+No\\.\\s*:?\\s*(REF-\\d{6})",
  "date": "Billing\\s+Date\\s*:?\\s*(\\d{2}/\\d{2}/\\d{4})",
  "vendor": "Client\\s+Name\\s*:?\\s*([A-Z][a-zA-Z\\s&]+)"
}
```

```bash
pdfrename -f "client_invoice.pdf" -p patterns.json -t "{vendor}_{invoice_nr}_{date}.pdf"
```

### 7. Dry-Run Verification

**Scenario**: Test renaming before committing.

```bash
# Test first
pdfrename -f "*.pdf" -d --verbose

# If looks good, execute
pdfrename -f "*.pdf"
```

### 8. Archive Migration

**Scenario**: Rename old invoices to new naming scheme.

```bash
pdfrename -f "./old_invoices/*.pdf" \
          -t "{date}_{vendor}_{invoice_nr}.pdf" \
          -o "./new_archive/" \
          --verbose
```

### 9. Automated Download Processing

**Scenario**: Cron job to process new downloads.

```bash
#!/bin/bash
# Run daily to process downloaded invoices

pdfrename -f ~/Downloads/invoice*.pdf \
          -t "{vendor}_{invoice_nr}_{date}.pdf" \
          -o ~/Documents/Invoices/$(date +%Y)/

# Clean up originals after successful rename
if [ $? -eq 0 ]; then
    echo "Invoices processed successfully"
fi
```

### 10. Multi-Vendor Bulk Processing

**Scenario**: Process invoices from multiple vendors.

```bash
# Process all invoice PDFs with appropriate patterns
pdfrename -f "invoices_2024/*.pdf" \
          -t "{vendor}_{date}_{invoice_nr}.pdf" \
          -o "./sorted/" \
          --verbose

# Results organized automatically by vendor
```

---

## Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | All files renamed successfully |
| 1 | Error | One or more files failed to rename |

### Example: Error Handling

```bash
#!/bin/bash

pdfrename -f "*.pdf" -o "./renamed/"

if [ $? -eq 0 ]; then
    echo "All invoices renamed successfully!"
else
    echo "Some invoices failed to rename. Check verbose output."
    exit 1
fi
```

---

## Troubleshooting

### Error: "No PDF files found matching pattern"

**Cause**: File pattern doesn't match any files.

**Solution**:
```bash
# Check files exist
ls -l *.pdf

# Try absolute path
pdfrename -f /full/path/to/*.pdf

# Escape special characters
pdfrename -f "invoices (2024)/*.pdf"
```

### Error: "Could not extract invoice number"

**Cause**: Invoice number pattern doesn't match PDF content.

**Solution**:
```bash
# Use verbose mode to see extracted text
pdfrename -f invoice.pdf --verbose

# Check what text is extracted
pdfgettxt -i invoice.pdf -o text.txt
cat text.txt

# Create custom pattern
# patterns.json with correct pattern
pdfrename -f invoice.pdf -p patterns.json
```

### Error: "Could not extract date"

**Cause**: Date pattern doesn't match PDF content.

**Solution**:
```bash
# View extracted text
pdfrename -f invoice.pdf --verbose

# Check date format in PDF
pdfgettxt -i invoice.pdf | grep -i date

# Add custom date pattern to patterns.json
```

### Error: "Could not extract vendor"

**Cause**: Vendor pattern doesn't match PDF content.

**Solution**:
```bash
# Check PDF content
pdfgettxt -i invoice.pdf | grep -i -E "(vendor|from|supplier)"

# Create custom vendor pattern
# patterns.json
```

### Error: "Invalid template"

**Cause**: Template syntax is incorrect.

**Solution**:
```bash
# Correct templates
-t "{vendor}_{invoice_nr}_{date}.pdf"
-t "{date}_{vendor}.pdf"

# Incorrect (missing .pdf)
-t "{vendor}_{invoice_nr}"

# Incorrect (no placeholders)
-t "invoice.pdf"
```

### Error: "Duplicate filename"

**Cause**: Multiple files would be renamed to same name (with `--no-duplicates`).

**Solution**:
```bash
# Allow duplicate handling (default)
pdfrename -f "*.pdf"  # Adds _1, _2 suffix

# Or use more specific template
pdfrename -f "*.pdf" -t "{vendor}_{invoice_nr}_{date}_{time}.pdf"
```

### Error: "Permission denied"

**Cause**: No write permission for output directory or files.

**Solution**:
```bash
# Check file permissions
ls -l invoice.pdf

# Check directory permissions
ls -ld ./output/

# Use directory you own
pdfrename -f invoice.pdf -o ~/Documents/invoices/
```

### Warning: "Failed to load custom patterns"

**Cause**: Invalid JSON in patterns file.

**Solution**:
```bash
# Validate JSON
python -m json.tool patterns.json

# Check for syntax errors (commas, quotes, backslashes)
```

### Issue: Incorrect Date Format

**Symptom**: Date extracted but in wrong format.

**Cause**: Date parsing not recognizing format.

**Solution**:
- Check verbose output to see extracted date
- Verify date format in PDF
- Add custom date pattern if needed

### Issue: Vendor Name Too Long

**Symptom**: Vendor name truncated or wrong.

**Solution**:
```bash
# Adjust vendor pattern length in custom patterns
# Default: {2,40} characters
# Custom: {2,60} for longer names
```

### Issue: Special Characters in Filename

**Symptom**: Renamed file has invalid characters.

**Solution**:
- Tool automatically sanitizes filenames
- Replaces `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|` with `_`
- If issues persist, check template for special chars

---

## Advanced Usage

### Integration with Other Tools

**Extract then rename**:
```bash
# Extract to verify content
pdfgettxt -i invoice.pdf -o text.txt

# Check what can be extracted
cat text.txt

# Rename based on content
pdfrename -f invoice.pdf
```

**Batch download and organize**:
```bash
#!/bin/bash
# Download invoices (example with wget)
wget -P downloads/ https://example.com/invoices/*.pdf

# Rename and organize
pdfrename -f downloads/*.pdf -o organized/ --verbose
```

### Python Integration

```python
import subprocess
import json

# Rename invoice
result = subprocess.run([
    'pdfrename',
    '-f', 'invoice.pdf',
    '-t', '{vendor}_{invoice_nr}_{date}.pdf',
    '--verbose'
], capture_output=True, text=True)

if result.returncode == 0:
    print("Rename successful")
    print(result.stdout)
else:
    print("Rename failed")
    print(result.stderr)
```

### Bash Automation Script

```bash
#!/bin/bash
# Automated invoice processing script

DOWNLOAD_DIR=~/Downloads
INVOICE_DIR=~/Documents/Invoices
YEAR=$(date +%Y)
MONTH=$(date +%m)

# Process new invoices
echo "Processing invoices from $DOWNLOAD_DIR..."

pdfrename -f "$DOWNLOAD_DIR/invoice*.pdf" \
          -t "{vendor}_{invoice_nr}_{date}.pdf" \
          -o "$INVOICE_DIR/$YEAR/$MONTH/" \
          --verbose

if [ $? -eq 0 ]; then
    echo "Invoices processed successfully"

    # Optional: Remove originals
    # rm "$DOWNLOAD_DIR/invoice*.pdf"
else
    echo "Some invoices failed. Check logs."
    exit 1
fi
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [Text Extraction Tool](pdfgettxt.md)
- [PDF Merge Tool](pdfmerge.md)
- [PDF Split Tool](pdfsplit.md)
- [Project README](../../README.md)

---

## Support

For issues and questions:

1. Check this troubleshooting section
2. Use `--verbose` to see extraction details
3. Extract text with `pdfgettxt` to verify content
4. Review [INSTALLATION.md](../../INSTALLATION.md)
5. Search GitHub issues
6. Create a new issue with:
   - Command you ran
   - Verbose output
   - Sample PDF (if possible)
   - Expected vs actual filename
   - Extracted text from PDF
