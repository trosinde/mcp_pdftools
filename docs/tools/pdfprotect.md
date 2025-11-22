# PDF Protection Tool

Protect PDF files with password encryption and granular permissions using 128-bit AES encryption.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Encryption](#encryption)
- [Permissions](#permissions)
- [Options](#options)
- [Examples](#examples)
- [Security Best Practices](#security-best-practices)
- [Common Use Cases](#common-use-cases)
- [Exit Codes](#exit-codes)
- [Troubleshooting](#troubleshooting)

---

## Overview

The **pdfprotect** tool secures PDF files by adding password protection and controlling document permissions. It uses industry-standard 128-bit AES encryption to protect sensitive documents.

### Key Features

- **Password Protection**: User password (open) and owner password (permissions)
- **128-bit AES Encryption**: Industry-standard security
- **Granular Permissions**: PRINT, COPY, MODIFY, ANNOTATE
- **Flexible Security**: Set permissions without user password
- **Batch Processing Compatible**: Integrate into workflows
- **Original File Preservation**: Creates new protected file

### Requirements

- Python 3.8+
- PyPDF2 library with encryption support
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
pip install PyPDF2>=3.0.1
```

See [INSTALLATION.md](../../INSTALLATION.md) for detailed installation instructions.

---

## Usage

### Basic Syntax

```bash
pdfprotect -i input.pdf [-o output.pdf] -u USER_PASSWORD [-w OWNER_PASSWORD] [-p PERMISSIONS]
```

### Required Arguments

| Argument | Description |
|----------|-------------|
| `-i, --input` | Input PDF file to protect |
| `-u, --user-password` OR `-w, --owner-password` | At least one password required |

### Optional Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `-o, --output` | Output file path | `{input}_protected.pdf` |
| `-u, --user-password` | Password required to open the PDF | None |
| `-w, --owner-password` | Password required to change permissions | None |
| `-p, --permissions` | Comma-separated list of allowed permissions | All denied |
| `--verbose` | Enable verbose output | Disabled |
| `--version` | Show version and exit | - |

---

## Encryption

### 128-bit AES Encryption

The tool uses **128-bit AES encryption**, the industry standard for PDF security.

**Features**:
- Strong encryption algorithm
- Compatible with all modern PDF readers
- Adobe Acrobat/Reader compatible
- Standards-compliant (PDF 1.6+)

**Encryption Strength**:
- 128-bit key length
- 2^128 possible keys
- Virtually impossible to brute force
- FIPS 140-2 compliant

---

### Password Types

#### 1. User Password (Open Password)

**Purpose**: Controls who can open and view the PDF.

**Usage**:
```bash
-u secret123
```

**Behavior**:
- User must enter this password to open the PDF
- Without correct password, PDF cannot be viewed
- Most restrictive type of protection

**When to use**:
- Confidential documents
- Sensitive information
- Need-to-know access

---

#### 2. Owner Password (Permissions Password)

**Purpose**: Controls who can change document permissions and security settings.

**Usage**:
```bash
-w admin456
```

**Behavior**:
- PDF can be opened without password (if no user password set)
- Content is viewable but restricted by permissions
- Only owner password can remove restrictions

**When to use**:
- Distributing documents with restrictions
- Preventing editing/copying
- Protecting intellectual property
- Forms that shouldn't be modified

---

#### 3. Both Passwords

**Combined Protection**: Maximum security.

**Usage**:
```bash
-u user123 -w admin456
```

**Behavior**:
- User password required to open PDF
- Owner password required to change permissions
- Two layers of protection

**When to use**:
- Highly sensitive documents
- Legal documents
- Contracts with strict access control

**Best Practice**: Use different passwords for user and owner.

---

## Permissions

### Available Permissions

The tool supports four granular permissions:

| Permission | Code | Description |
|------------|------|-------------|
| **PRINT** | `print` | Allow printing the document |
| **COPY** | `copy` | Allow copying text and graphics |
| **MODIFY** | `modify` | Allow editing document content |
| **ANNOTATE** | `annotate` | Allow adding comments and annotations |

### Permission Syntax

**Single permission**:
```bash
-p print
```

**Multiple permissions** (comma-separated):
```bash
-p print,copy
```

**All permissions**:
```bash
-p print,copy,modify,annotate
```

**No permissions** (most restrictive):
```bash
# Don't specify -p flag
pdfprotect -i doc.pdf -u pass123
```

---

### Permission Details

#### PRINT Permission

**Allows**: Printing the PDF to paper or PDF printer

**Usage**:
```bash
pdfprotect -i document.pdf -u pass123 -p print
```

**When to allow**:
- Documents meant for physical distribution
- Reports that may need hard copies
- Presentations for meetings

**When to deny**:
- Strictly digital-only documents
- Preventing physical copies
- Confidential materials

---

#### COPY Permission

**Allows**: Selecting and copying text and images

**Usage**:
```bash
pdfprotect -i report.pdf -w admin123 -p copy
```

**When to allow**:
- Research documents
- Reference materials
- Educational content

**When to deny**:
- Copyrighted content
- Preventing plagiarism
- Proprietary information

---

#### MODIFY Permission

**Allows**: Editing document content (text, images, pages)

**Usage**:
```bash
pdfprotect -i contract.pdf -w owner456 -p modify
```

**When to allow**:
- Collaborative documents
- Templates
- Draft documents

**When to deny**:
- Final contracts
- Legal documents
- Signed agreements
- Official forms

---

#### ANNOTATE Permission

**Allows**: Adding comments, highlights, and markup

**Usage**:
```bash
pdfprotect -i draft.pdf -u read123 -p annotate
```

**When to allow**:
- Review documents
- Collaborative editing
- Feedback processes

**When to deny**:
- Final published documents
- Official records
- Archived documents

---

## Options

### Input (`-i, --input`)

Path to the PDF file to protect.

**Requirements**:
- File must exist
- File must be a valid PDF
- Read permission required

**Syntax**:
```bash
-i /path/to/document.pdf
```

### Output (`-o, --output`)

Path for the protected PDF file.

**Default**: `{input_filename}_protected.pdf` in same directory

**Syntax**:
```bash
-o /path/to/protected.pdf
```

**Notes**:
- Parent directory must exist
- Existing files will be overwritten
- Original file is never modified

### User Password (`-u, --user-password`)

Password required to open the PDF.

**Syntax**:
```bash
-u secret123
```

**Requirements**:
- String value
- No length restriction (but 8+ recommended)
- Case-sensitive

**Security Tips**:
- Use at least 8 characters
- Mix letters, numbers, symbols
- Avoid dictionary words
- Don't reuse passwords

### Owner Password (`-w, --owner-password`)

Password required to change permissions.

**Syntax**:
```bash
-w admin456
```

**Requirements**:
- String value
- Should differ from user password
- Case-sensitive

**Note**: At least one of `-u` or `-w` must be provided.

### Permissions (`-p, --permissions`)

Comma-separated list of allowed permissions.

**Syntax**:
```bash
-p print,copy
```

**Valid values**: `print`, `copy`, `modify`, `annotate`

**Default**: All permissions denied (empty list)

### Verbose (`--verbose`)

Enable detailed output and logging.

**Syntax**:
```bash
--verbose
```

**Shows**:
- Input/output file paths
- Permissions being set
- Processing steps
- Success/error details

**Note**: Passwords are NEVER logged, even in verbose mode.

---

## Examples

### Example 1: Basic Protection with User Password

Protect with password required to open:

```bash
pdfprotect -i confidential.pdf -u secret123
```

**Output**: `confidential_protected.pdf`

**Result**:
- Requires password "secret123" to open
- All permissions denied

### Example 2: Owner Password Only

Restrict permissions but allow viewing:

```bash
pdfprotect -i report.pdf -w admin456
```

**Result**:
- PDF opens without password
- All permissions denied
- Need owner password to change restrictions

### Example 3: Both Passwords

Maximum security with both passwords:

```bash
pdfprotect -i contract.pdf -u open123 -w admin456
```

**Result**:
- User password required to open
- Owner password required to change permissions

### Example 4: Allow Printing Only

Protect but allow printing:

```bash
pdfprotect -i invoice.pdf -u read123 -p print
```

**Result**:
- Password required to open
- Can print but cannot copy/edit

### Example 5: Allow Printing and Copying

Enable read-only access with printing:

```bash
pdfprotect -i manual.pdf -w owner789 -p print,copy
```

**Result**:
- Opens without password
- Can print and copy text
- Cannot modify or annotate

### Example 6: Full Permissions with Password

Protect with password but allow all operations:

```bash
pdfprotect -i shared_doc.pdf -u team123 -p print,copy,modify,annotate
```

**Use case**: Team document with controlled access

### Example 7: Custom Output Path

Specify custom output location:

```bash
pdfprotect -i document.pdf -o /secure/protected_doc.pdf -u pass123
```

### Example 8: Protect for Distribution

Protect document for public distribution:

```bash
pdfprotect -i whitepaper.pdf -w company456 -p print,copy -o whitepaper_final.pdf
```

**Result**:
- Viewable by anyone
- Can print and copy
- Cannot modify or annotate

### Example 9: Read-Only Contract

Create read-only contract that can be printed:

```bash
pdfprotect -i contract.pdf -u client123 -w lawyer456 -p print -o contract_final.pdf
```

**Result**:
- Client needs password to view
- Can print for signing
- Cannot edit content

### Example 10: Annotate-Only Document

Allow annotations but prevent editing:

```bash
pdfprotect -i review_draft.pdf -u team123 -p annotate -o review_draft_protected.pdf
```

**Use case**: Document review process

### Example 11: Verbose Output

Monitor protection process:

```bash
pdfprotect -i document.pdf -u pass123 --verbose
```

**Verbose Output**:
```
INFO: Input PDF: document.pdf
INFO: Output PDF: document_protected.pdf
INFO: Permissions: All denied (most restrictive)
INFO: Success: PDF protected successfully: document_protected.pdf
Protected PDF created: document_protected.pdf
```

### Example 12: No Permissions (Most Restrictive)

Maximum restriction:

```bash
pdfprotect -i sensitive.pdf -u secret123 -w admin456
```

**Result**:
- Password required to open
- No printing, copying, editing, or annotations allowed

---

## Security Best Practices

### 1. Password Strength

**Strong Passwords**:
- Minimum 12 characters
- Mix uppercase, lowercase, numbers, symbols
- Avoid dictionary words
- Use unique passwords

**Examples**:
```bash
# Weak (DON'T USE)
-u password123
-u company2024

# Strong (BETTER)
-u Tr0ng!P@ssw0rd#2024
-u My$ecur3-PDF_2024
```

### 2. Password Management

**Best Practices**:
- Never share user and owner passwords together
- Store passwords securely (password manager)
- Use different passwords for different documents
- Change passwords periodically for sensitive docs
- Never commit passwords to version control

**Example**:
```bash
# Read password from environment variable
pdfprotect -i doc.pdf -u "$PDF_USER_PASS" -w "$PDF_OWNER_PASS"

# Or read from file (ensure file permissions are secure!)
pdfprotect -i doc.pdf -u "$(cat ~/.pdf_pass)" -w "$(cat ~/.pdf_owner_pass)"
```

### 3. Permission Guidelines

**Choose permissions based on use case**:

| Use Case | Permissions | Passwords |
|----------|-------------|-----------|
| Public whitepaper | `print,copy` | Owner only |
| Internal report | `print` | User only |
| Contract for signing | `print` | Both |
| Review draft | `annotate` | User only |
| Read-only archive | None | Owner only |
| Confidential document | None | Both |

### 4. Distribution Security

**When distributing protected PDFs**:
- Send password separately (different channel)
- Use secure channels (encrypted email, secure file transfer)
- Verify recipient before sharing password
- Set expiration for time-sensitive documents
- Document who received password and when

### 5. Regular Security Audits

**Recommendations**:
- Review who has access to protected documents
- Update passwords regularly
- Re-protect documents if security compromised
- Monitor for unauthorized access

### 6. Compliance Considerations

**For regulated industries**:
- GDPR: Encryption required for personal data
- HIPAA: Protect health information
- PCI DSS: Secure payment card data
- SOX: Protect financial records

**Example** (HIPAA-compliant):
```bash
pdfprotect -i patient_record.pdf -u "$STRONG_PASSWORD" -w "$ADMIN_PASSWORD"
# No permissions = most restrictive
```

---

## Common Use Cases

### 1. Confidential Business Documents

**Scenario**: Protect sensitive business plans.

```bash
pdfprotect -i business_plan.pdf -u Secret2024! -w Admin2024! -o business_plan_secure.pdf
```

**Distribution**: Share password via separate secure channel.

### 2. Client Deliverables

**Scenario**: Send reports to clients that can be read and printed but not edited.

```bash
pdfprotect -i client_report.pdf -w CompanyPass456 -p print,copy -o client_report_final.pdf
```

### 3. Contract Distribution

**Scenario**: Distribute contracts that can be printed for signing.

```bash
pdfprotect -i contract.pdf -u ClientPass123 -p print -o contract_for_signature.pdf
```

### 4. Internal Documentation

**Scenario**: Protect internal manuals from unauthorized editing.

```bash
pdfprotect -i employee_handbook.pdf -w HR_Pass789 -p print,copy -o handbook_protected.pdf
```

### 5. Review Process

**Scenario**: Allow reviewers to annotate but not modify.

```bash
pdfprotect -i draft_v1.pdf -u ReviewTeam123 -p annotate -o draft_v1_review.pdf
```

### 6. Public Whitepapers

**Scenario**: Distribute publicly but prevent unauthorized modifications.

```bash
pdfprotect -i whitepaper.pdf -w CompanyOwner456 -p print,copy -o whitepaper_public.pdf
```

### 7. Legal Documents

**Scenario**: Maximum protection for legal contracts.

```bash
pdfprotect -i legal_contract.pdf -u Party1_Pass -w Lawyer_Pass -o contract_protected.pdf
```

### 8. Educational Materials

**Scenario**: Protect course materials from copying.

```bash
pdfprotect -i course_materials.pdf -u Student123 -p print -o course_materials_protected.pdf
```

### 9. Batch Protection

**Scenario**: Protect multiple files with same settings.

```bash
#!/bin/bash
for pdf in *.pdf; do
    echo "Protecting: $pdf"
    pdfprotect -i "$pdf" -u "$USER_PASS" -w "$OWNER_PASS" -p print -o "protected/${pdf}"
done
```

### 10. Invoice Protection

**Scenario**: Protect invoices for customers.

```bash
pdfprotect -i invoice_12345.pdf -w Company2024 -p print,copy -o invoice_12345_protected.pdf
```

---

## Exit Codes

| Code | Status | Description |
|------|--------|-------------|
| 0 | Success | PDF protected successfully |
| 1 | Error | Error occurred (invalid input, protection failed, etc.) |
| 130 | Cancelled | Operation cancelled by user (Ctrl+C) |

### Example: Error Handling

```bash
#!/bin/bash

pdfprotect -i document.pdf -u "$PASSWORD" -w "$OWNER_PASS"

if [ $? -eq 0 ]; then
    echo "PDF protected successfully!"
else
    echo "Failed to protect PDF"
    exit 1
fi
```

---

## Troubleshooting

### Error: "At least one password must be provided"

**Cause**: Neither `-u` nor `-w` specified.

**Solution**:
```bash
# Provide at least one password
pdfprotect -i doc.pdf -u secret123

# Or owner password
pdfprotect -i doc.pdf -w admin456

# Or both
pdfprotect -i doc.pdf -u secret123 -w admin456
```

### Error: "Input file not found"

**Cause**: The specified PDF file doesn't exist.

**Solution**:
```bash
# Check file exists
ls -l document.pdf

# Use absolute path
pdfprotect -i /full/path/to/document.pdf -u pass123
```

### Error: "Invalid PDF file"

**Cause**: File is corrupted or not a valid PDF.

**Solution**:
- Open file in PDF reader to verify
- Re-export from original source
- Try repairing the PDF

### Error: "Invalid permission"

**Cause**: Invalid permission name in `-p` argument.

**Solution**:
```bash
# Valid permissions only
pdfprotect -i doc.pdf -u pass123 -p print,copy,modify,annotate

# Invalid (will fail)
pdfprotect -i doc.pdf -u pass123 -p edit,delete  # Wrong!
```

**Valid permissions**: `print`, `copy`, `modify`, `annotate`

### Error: "Permission denied"

**Cause**: No write permission for output directory.

**Solution**:
```bash
# Check directory permissions
ls -ld ./

# Use directory you own
pdfprotect -i doc.pdf -o ~/Documents/protected.pdf -u pass123
```

### Error: "PDF is already encrypted"

**Cause**: Source PDF is already password-protected.

**Solution**:
1. Remove existing protection first (requires current password)
2. Or work with decrypted version

### Warning: User and Owner Passwords Are Same

**Symptom**: Using same password for both.

**Security Risk**: Reduces security effectiveness.

**Solution**:
```bash
# Use different passwords
pdfprotect -i doc.pdf -u UserPass123 -w OwnerPass456
```

### Issue: Protected PDF Cannot Be Opened

**Symptom**: Even with correct password, PDF won't open.

**Possible Causes**:
1. PDF reader doesn't support 128-bit encryption
2. Password entered incorrectly (case-sensitive)
3. Corruption during protection

**Solutions**:
- Try different PDF reader (Adobe Acrobat, Foxit)
- Verify password (check caps lock)
- Re-protect the original file

### Issue: Permissions Not Enforced

**Symptom**: Users can perform restricted actions.

**Possible Causes**:
1. PDF reader ignoring restrictions
2. Only owner password set (user can open freely)
3. PDF reader with "bypass" features

**Notes**:
- Permissions are enforced by PDF readers
- Some readers may not honor all restrictions
- User password provides stronger protection
- Consider both passwords for critical documents

---

## Advanced Usage

### Environment Variables for Passwords

**Store passwords securely**:

```bash
# Set environment variables
export PDF_USER_PASS="SecurePass123!"
export PDF_OWNER_PASS="AdminPass456!"

# Use in command
pdfprotect -i document.pdf -u "$PDF_USER_PASS" -w "$PDF_OWNER_PASS"
```

### Integration with Other Tools

**Protect after merging**:
```bash
# Merge PDFs
pdfmerge -f "file1.pdf,file2.pdf,file3.pdf" -o merged.pdf

# Protect merged file
pdfprotect -i merged.pdf -u pass123 -p print -o merged_protected.pdf
```

**Protect after text extraction**:
```bash
# Extract text for indexing
pdfgettxt -i original.pdf -o text.txt

# Protect original
pdfprotect -i original.pdf -w owner456 -p print,copy
```

### Batch Protection Script

```bash
#!/bin/bash
# Protect all PDFs in directory

USER_PASS="ReadAccess123!"
OWNER_PASS="AdminControl456!"

for pdf in *.pdf; do
    if [[ "$pdf" != *"_protected.pdf" ]]; then
        echo "Protecting: $pdf"

        pdfprotect -i "$pdf" \
                   -u "$USER_PASS" \
                   -w "$OWNER_PASS" \
                   -p print,copy \
                   -o "protected/${pdf%.pdf}_protected.pdf"

        if [ $? -eq 0 ]; then
            echo "  ✓ Success"
        else
            echo "  ✗ Failed"
        fi
    fi
done
```

---

## See Also

- [Installation Guide](../../INSTALLATION.md)
- [PDF Merge Tool](pdfmerge.md)
- [PDF Split Tool](pdfsplit.md)
- [Text Extraction Tool](pdfgettxt.md)
- [Project README](../../README.md)

---

## Support

For issues and questions:

1. Check this troubleshooting section
2. Review [INSTALLATION.md](../../INSTALLATION.md)
3. Search GitHub issues
4. Create a new issue with:
   - Command you ran (WITHOUT passwords!)
   - Expected vs actual behavior
   - PDF file details
   - Error messages
   - Operating system

**Security Note**: NEVER share actual passwords in issue reports!
