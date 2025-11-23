# MCP PDFTools Server

Model Context Protocol (MCP) server for PDFTools, enabling AI agents to perform PDF operations.

## Features

This MCP server exposes 7 PDF tools:

1. **pdf_merge** - Merge multiple PDF files
2. **pdf_split** - Split PDFs into multiple files
3. **pdf_extract_text** - Extract text from PDFs
4. **pdf_ocr** - OCR for scanned documents
5. **pdf_protect** - Password protect PDFs
6. **pdf_thumbnails** - Generate thumbnail images
7. **pdf_rename_invoice** - Smart invoice renaming

## Installation

### Prerequisites

- Node.js 18+
- Python 3.8+ with PDFTools installed
- PDFTools virtual environment activated

### Install Dependencies

```bash
cd mcp-server
npm install
```

### Build

```bash
npm run build
```

## Usage

### Standalone Mode

```bash
node dist/index.js
```

### As MCP Server

Configure in your AI tool's MCP settings:

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

**Claude Code** (`.claude/mcp_config.json`):
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

**OpenCode** (`~/.opencode/mcp_config.json`):
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

## Development

### Watch Mode

```bash
npm run watch
```

### Linting

```bash
npm run lint
```

### Testing

```bash
npm test
```

## Tool Examples

### Merge PDFs
```typescript
{
  "name": "pdf_merge",
  "arguments": {
    "input_files": ["doc1.pdf", "doc2.pdf"],
    "output_file": "merged.pdf"
  }
}
```

### Split PDF
```typescript
{
  "name": "pdf_split",
  "arguments": {
    "input_file": "document.pdf",
    "output_dir": "pages/",
    "mode": "pages"
  }
}
```

### Extract Text
```typescript
{
  "name": "pdf_extract_text",
  "arguments": {
    "input_file": "document.pdf",
    "mode": "simple"
  }
}
```

## License

MIT
