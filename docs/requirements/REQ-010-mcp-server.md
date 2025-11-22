# Feature Requirement: MCP Server Integration

**ID**: REQ-010
**Version**: 1.0
**Status**: Draft
**Priority**: High
**Created by**: Requirements Engineer
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Related Documents**:
- Design: DESIGN-010 v1.0
- Test Report: TEST-010 v1.0
- Traceability: See [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

---

## 1. Übersicht

### 1.1 Kurzbeschreibung
MCP (Model Context Protocol) Server für PDFTools, der es AI Agents (Claude Code, Claude Desktop, OpenCode, etc.) ermöglicht, alle 7 PDF-Tools über ein standardisiertes Interface zu nutzen.

### 1.2 Geschäftsziel
AI Assistenten werden zunehmend für Dokumenten-Workflows eingesetzt. Aktuell müssen Benutzer manuell CLI-Befehle aufrufen oder Code schreiben. Mit einem MCP Server können AI Agents direkt auf PDFTools zugreifen und komplexe PDF-Workflows automatisieren. Dies verbessert die User Experience erheblich und macht PDFTools nahtlos in AI-gestützte Workflows integrierbar.

**Beispiel Use Cases:**
- User zu Claude: "Extract text from invoice.pdf" → Claude nutzt pdfgettxt automatisch
- User zu Claude: "Merge these 3 PDFs and protect the result" → Claude nutzt pdfmerge + pdfprotect
- User zu Claude: "Create thumbnails for all PDFs in this folder" → Claude nutzt pdfthumbnails

### 1.3 Betroffene Module
- [ ] PDF Merge → als MCP Tool verfügbar
- [ ] PDF Split → als MCP Tool verfügbar
- [ ] Text Extraction → als MCP Tool verfügbar
- [ ] OCR → als MCP Tool verfügbar
- [ ] PDF Protection → als MCP Tool verfügbar
- [ ] Thumbnails → als MCP Tool verfügbar
- [ ] Invoice Renamer → als MCP Tool verfügbar
- [x] Neues Modul: **MCP Server** (`mcp-server/`)

---

## 2. Funktionale Anforderungen

### 2.1 Hauptfunktionalität
**Als** AI Agent (Claude, OpenCode, etc.)
**möchte ich** alle PDFTools als MCP Tools nutzen können
**damit** ich PDF-Workflows automatisch für Benutzer ausführen kann

**Akzeptanzkriterien:**
1. [ ] MCP Server ist lokal installierbar (`npm install -g @trosinde/mcp-pdftools`)
2. [ ] MCP Server kommuniziert via stdio (Standard MCP)
3. [ ] Alle 7 Tools werden als MCP Tools exponiert
4. [ ] Tools erscheinen automatisch in LLM Tool-Liste
5. [ ] LLM kann alle Tool-Parameter nutzen
6. [ ] Fehler werden klar an LLM zurückgegeben
7. [ ] Automatische Config-Generierung für Claude Desktop/Code/OpenCode

### 2.2 MCP Tools Mapping

| PDFTools CLI | MCP Tool Name | Beschreibung |
|--------------|---------------|--------------|
| `pdfmerge` | `pdf_merge` | Merge multiple PDF files into one |
| `pdfsplit` | `pdf_split` | Split PDF into multiple files |
| `ocrutil` | `pdf_ocr` | Extract text from scanned PDFs using OCR |
| `pdfgettxt` | `pdf_extract_text` | Extract text from PDF files |
| `pdfprotect` | `pdf_protect` | Add password protection to PDFs |
| `pdfthumbnails` | `pdf_thumbnails` | Generate thumbnail images from PDFs |
| `pdfrename` | `pdf_rename_invoice` | Intelligently rename invoice PDFs |

### 2.3 Input/Output

#### 2.3.1 Installation
```bash
# Global installation
npm install -g @trosinde/mcp-pdftools

# Local installation
npm install @trosinde/mcp-pdftools
```

#### 2.3.2 Configuration
**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "pdftools": {
      "command": "mcp-pdftools",
      "args": []
    }
  }
}
```

**Claude Code** (`.claude/mcp_config.json`):
```json
{
  "mcpServers": {
    "pdftools": {
      "command": "mcp-pdftools",
      "args": []
    }
  }
}
```

**OpenCode** (ähnliche Konfiguration):
```json
{
  "mcpServers": {
    "pdftools": {
      "command": "mcp-pdftools",
      "args": []
    }
  }
}
```

#### 2.3.3 Tool Schemas
Jedes MCP Tool muss ein JSON Schema haben, das dem LLM die Parameter erklärt.

**Beispiel: `pdf_merge` Tool Schema:**
```json
{
  "name": "pdf_merge",
  "description": "Merge multiple PDF files into a single document. Preserves bookmarks and metadata.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "files": {
        "type": "array",
        "items": {"type": "string"},
        "description": "List of PDF file paths to merge (minimum 2 files)",
        "minItems": 2
      },
      "output": {
        "type": "string",
        "description": "Output path for merged PDF (optional, defaults to merged.pdf)"
      },
      "keep_bookmarks": {
        "type": "boolean",
        "description": "Preserve bookmarks from source PDFs (default: true)",
        "default": true
      },
      "verbose": {
        "type": "boolean",
        "description": "Enable verbose output (default: false)",
        "default": false
      }
    },
    "required": ["files"]
  }
}
```

### 2.4 Verhalten

#### 2.4.1 Erfolgsszenario
1. LLM sendet Tool-Aufruf an MCP Server: `pdf_merge(files=["a.pdf", "b.pdf"], output="merged.pdf")`
2. MCP Server validiert Parameter
3. MCP Server ruft Python CLI auf: `pdfmerge -f "a.pdf,b.pdf" -o merged.pdf`
4. Python CLI führt Operation aus
5. MCP Server liest Ergebnis (stdout/stderr)
6. MCP Server gibt strukturierte Response an LLM zurück
7. LLM informiert User: "Successfully merged 2 PDFs into merged.pdf"

#### 2.4.2 Fehlerszenarios

**1. Tool nicht gefunden:**
```json
{
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "PDFTools CLI not found. Please ensure PDFTools is installed (pip install pdftools)"
  }
}
```

**2. Ungültige Parameter:**
```json
{
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "At least 2 files required for merging. Got: 1"
  }
}
```

**3. CLI-Fehler:**
```json
{
  "error": {
    "code": "CLI_ERROR",
    "message": "PDF file not found: /path/to/missing.pdf",
    "details": "Exit code: 1"
  }
}
```

### 2.5 Error Handling
- **Klare Fehlermel dungen**: LLM muss verstehen, was schiefgelaufen ist
- **Error Codes**: Strukturierte Fehlercodes für programmatische Verarbeitung
- **Recovery-Hints**: Wenn möglich, Hinweise zur Behebung mitgeben

**Beispiel:**
```json
{
  "error": {
    "code": "PDFTOOLS_NOT_INSTALLED",
    "message": "PDFTools CLI not found in PATH",
    "recovery": "Install PDFTools: pip install pdftools"
  }
}
```

---

## 3. Nicht-Funktionale Anforderungen

### 3.1 Performance
- **Startup Time**: < 500ms (MCP Server bereit)
- **Tool Call Latency**: < 100ms Overhead (zusätzlich zur CLI-Zeit)
- **Memory**: < 50 MB für Server (Python CLI separat)

### 3.2 Qualität
- **Test Coverage**: > 80% (Unit + Integration Tests)
- **Type Safety**: TypeScript mit strikten Types
- **Documentation**: Vollständige Tool Descriptions für LLMs
- **Error Messages**: User-friendly und LLM-parsable

### 3.3 Kompatibilität
- **MCP Protocol**: MCP v1.0 Standard
- **Node.js**: >= 18.0.0
- **Python PDFTools**: >= 2.0.0 (die implementierten CLI-Tools)
- **LLM Clients**:
  - Claude Desktop (macOS, Windows)
  - Claude Code (VSCode Extension)
  - OpenCode
  - Andere MCP-kompatible Clients

### 3.4 Security
- **No Remote Access**: Nur lokale Nutzung (stdio)
- **Path Validation**: Keine Path Traversal Attacks
- **Input Sanitization**: Alle User-Inputs werden validiert
- **No Secrets**: Keine Passwörter/API Keys im Server

---

## 4. Technische Details

### 4.1 Abhängigkeiten

#### 4.1.1 MCP Server (Node.js)
- **@anthropic-ai/sdk**: MCP Protocol Implementation
- **typescript**: Type-safe Development
- **zod**: Runtime Schema Validation

#### 4.1.2 PDFTools (Python)
Voraussetzung: PDFTools muss installiert sein
```bash
pip install pdftools  # oder pip install -e .
```

#### 4.1.3 Keine weiteren externen Tools
- MCP Server kommuniziert via `child_process.spawn()` mit Python CLI
- Keine Datenbank, kein Web Server, kein Docker

### 4.2 Konfiguration

#### 4.2.1 Environment Variables
- `PDFTOOLS_CLI_PATH`: Custom path to PDFTools CLI (optional, defaults to PATH lookup)
- `MCP_PDFTOOLS_LOG_LEVEL`: Logging level (debug, info, warn, error)

#### 4.2.2 Config File (optional)
`~/.mcp-pdftools/config.json`:
```json
{
  "pdftools_path": "/custom/path/to/pdftools",
  "log_level": "info",
  "timeout": 300000
}
```

### 4.3 Communication Flow

```
┌─────────────┐
│ LLM Client  │  (Claude Desktop, Claude Code, OpenCode)
│ (Claude)    │
└──────┬──────┘
       │ MCP Protocol (stdio)
       ↓
┌─────────────┐
│ MCP Server  │  (Node.js, TypeScript)
│ mcp-pdftools│
└──────┬──────┘
       │ child_process.spawn()
       ↓
┌─────────────┐
│ PDFTools CLI│  (Python)
│ pdfmerge    │
│ pdfsplit    │
│ etc.        │
└─────────────┘
```

---

## 5. Testbarkeit

### 5.1 Unit Tests
- [x] Tool Schema Validation
- [x] Parameter Mapping (MCP → CLI)
- [x] Error Parsing (CLI → MCP)
- [x] Path Validation
- [x] Command Construction

### 5.2 Integration Tests
- [x] MCP Server startet erfolgreich
- [x] Tool-Liste wird exponiert
- [x] Tool-Aufruf funktioniert (Mock CLI)
- [x] Fehlerbehandlung End-to-End

### 5.3 E2E Tests
- [x] Real CLI-Aufruf (pdf_merge)
- [x] Real CLI-Aufruf (pdf_split)
- [x] Real CLI-Aufruf (pdf_ocr)
- [x] Error Cases (fehlende Datei, etc.)

### 5.4 Test-Daten
- [x] Mock PDFs für CLI-Tests
- [x] Sample MCP Requests (JSON)
- [x] Expected Responses (JSON)

---

## 6. Beispiele

### 6.1 LLM Conversation Examples

#### Beispiel 1: PDF Merge
```
User: "Merge report_part1.pdf and report_part2.pdf into final_report.pdf"

Claude (internal): Calls pdf_merge tool with:
{
  "files": ["report_part1.pdf", "report_part2.pdf"],
  "output": "final_report.pdf"
}

MCP Server: Executes pdfmerge CLI
CLI Output: "Successfully merged 2 PDFs (total: 25 pages)"

Claude to User: "I've successfully merged the two PDF files into final_report.pdf. The combined document has 25 pages."
```

#### Beispiel 2: OCR + Text Extraction
```
User: "Extract text from this scanned invoice: scan_invoice.pdf"

Claude (internal):
1. Calls pdf_ocr tool:
   {"file": "scan_invoice.pdf", "language": "eng", "output_mode": "pdf"}
2. Then calls pdf_extract_text tool:
   {"file": "scan_invoice_ocr.pdf", "mode": "simple"}

Claude to User: "I've processed the scanned invoice using OCR and extracted the text. Here's what it contains: [invoice text...]"
```

#### Beispiel 3: Complex Workflow
```
User: "Merge all PDFs in the ./invoices/ folder, protect with password 'secret123', and create thumbnails"

Claude (internal):
1. Lists files in ./invoices/ → ["inv1.pdf", "inv2.pdf", "inv3.pdf"]
2. Calls pdf_merge: {"files": [...], "output": "all_invoices.pdf"}
3. Calls pdf_protect: {"file": "all_invoices.pdf", "password": "secret123"}
4. Calls pdf_thumbnails: {"file": "all_invoices_protected.pdf"}

Claude to User: "Done! I've merged 3 invoices, protected the result with a password, and generated thumbnails."
```

### 6.2 MCP Server Usage (Programmatic)

```typescript
// MCP Server Tool Definition
import { Tool } from '@anthropic-ai/sdk/mcp';

const pdfMergeTool: Tool = {
  name: 'pdf_merge',
  description: 'Merge multiple PDF files into a single document',
  inputSchema: {
    type: 'object',
    properties: {
      files: {
        type: 'array',
        items: { type: 'string' },
        description: 'List of PDF file paths',
        minItems: 2
      },
      output: {
        type: 'string',
        description: 'Output path (optional)'
      }
    },
    required: ['files']
  }
};

// Tool Execution
async function executePdfMerge(params: any) {
  const { files, output, keep_bookmarks, verbose } = params;

  // Build CLI command
  const args = ['-f', files.join(',')];
  if (output) args.push('-o', output);
  if (keep_bookmarks) args.push('--keep-bookmarks');
  if (verbose) args.push('--verbose');

  // Execute Python CLI
  const result = await executeCliTool('pdfmerge', args);

  return {
    success: result.exitCode === 0,
    output: result.stdout,
    error: result.stderr
  };
}
```

---

## 7. Offene Fragen

1. **Installation**: NPM Package oder nur GitHub? → **NPM Package bevorzugt**
2. **Streaming**: Sollen große Outputs gestreamt werden? → **Später (v2.0)**
3. **Progress**: Soll Progress-Callback unterstützt werden? → **Nice-to-have**
4. **Config Auto-Detect**: Automatische Config-Generierung? → **Ja, per Install-Script**

---

## 8. Review

### Team Review
- [ ] Requirements Engineer: Content complete?
- [ ] Architekt: MCP Protocol korrekt?
- [ ] Node.js Entwickler: Implementation feasible?
- [ ] Python Entwickler: CLI-Integration OK?
- [ ] Tester: Test strategy clear?
- [ ] DevOps: Deployment/Installation OK?

### Änderungshistorie
| Datum | Version | Änderung | Von | Auswirkung |
|-------|---------|----------|-----|------------|
| 2025-11-22 | 1.0 | Initiale Erstellung | Requirements Engineer | Neu |

**Versions-Semantik**:
- **MAJOR.x.x**: Breaking Changes, grundlegende Änderung der Anforderung
- **x.MINOR.x**: Neue Anforderungen, backwards compatible
- **x.x.PATCH**: Kleinere Klarstellungen, Korrekturen

---

## 9. Freigabe

**Freigegeben durch**: TBD (Team Review ausstehend)
**Datum**: TBD
**Nächster Schritt**: Design-Phase (DESIGN-010)

---

## 10. Anhang

### 10.1 Referenzen
- **MCP Protocol**: https://modelcontextprotocol.io/
- **Claude Desktop Config**: https://docs.anthropic.com/claude/docs/model-context-protocol
- **PDFTools Documentation**: [README.md](../../README.md)
- **Traceability Matrix**: [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md)

### 10.2 Glossar
- **MCP**: Model Context Protocol - Standard für AI Agent Tool Integration
- **stdio**: Standard Input/Output - Communication Channel für MCP
- **Tool Schema**: JSON Schema Definition für LLM Tool Parameters
- **LLM**: Large Language Model (Claude, GPT, etc.)
