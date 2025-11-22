# Design Document: MCP Server Integration

**ID**: DESIGN-010
**Version**: 1.0
**Requirement**: [REQ-010](../requirements/REQ-010-mcp-server.md) v1.0
**Status**: Draft
**Architekt**: Architecture Team
**Entwickler**: Node.js Development Team
**Created on**: 2025-11-22
**Last updated**: 2025-11-22

**Traceability**:
- Implements: REQ-010 v1.0
- Tested by: TEST-010 v1.0

---

## 1. Übersicht

### 1.1 Ziel
Implementierung eines MCP (Model Context Protocol) Servers für PDFTools, der es AI Agents ermöglicht, alle 7 PDF-CLI-Tools über ein standardisiertes Interface zu nutzen.

### 1.2 Scope
**In Scope:**
- MCP Server Implementation (Node.js/TypeScript)
- Alle 7 PDFTools als MCP Tools
- Tool Schema Definitionen
- CLI Integration Layer
- Configuration Management
- Error Handling & Logging
- NPM Package Publishing

**Out of Scope:**
- Änderungen an bestehenden Python CLI-Tools
- Web Interface / GUI
- Remote Access / Cloud Deployment
- Multi-User Support
- Database / Persistence

---

## 2. Architektur

### 2.1 Projekt-Struktur

```
mcp_pdftools/
├── mcp-server/                    # MCP Server (Node.js/TypeScript)
│   ├── package.json               # NPM package config
│   ├── tsconfig.json              # TypeScript config
│   ├── src/
│   │   ├── index.ts               # Main entry point
│   │   ├── server.ts              # MCP Server implementation
│   │   ├── tools/                 # Tool definitions
│   │   │   ├── index.ts           # Tool registry
│   │   │   ├── pdf-merge.ts       # pdf_merge tool
│   │   │   ├── pdf-split.ts       # pdf_split tool
│   │   │   ├── pdf-ocr.ts         # pdf_ocr tool
│   │   │   ├── pdf-extract-text.ts # pdf_extract_text tool
│   │   │   ├── pdf-protect.ts     # pdf_protect tool
│   │   │   ├── pdf-thumbnails.ts  # pdf_thumbnails tool
│   │   │   └── pdf-rename.ts      # pdf_rename_invoice tool
│   │   ├── executors/             # CLI execution logic
│   │   │   ├── cli-executor.ts    # Generic CLI executor
│   │   │   └── pdftools-cli.ts    # PDFTools-specific executor
│   │   ├── validators/            # Input validation
│   │   │   └── schema-validator.ts
│   │   ├── config/                # Configuration
│   │   │   └── config-loader.ts
│   │   └── utils/                 # Utilities
│   │       ├── logger.ts
│   │       └── error-handler.ts
│   ├── tests/                     # Test suite
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── scripts/                   # Installation scripts
│   │   ├── install.js             # Post-install config setup
│   │   └── config-generator.js    # Generate MCP configs
│   └── README.md                  # MCP Server documentation
│
└── src/pdftools/                  # Existing Python tools (unchanged)
    ├── merge/
    ├── split/
    ├── ocr/
    └── ...
```

### 2.2 Komponenten-Diagramm

```
┌─────────────────────────────────────────────────────────────┐
│                        LLM Client                            │
│              (Claude Desktop, Claude Code, etc.)             │
└───────────────────────────┬─────────────────────────────────┘
                            │ MCP Protocol (stdio)
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      MCP Server                              │
│                                                              │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Tool Registry │→ │  Schema         │→ │  Validator   │ │
│  │  (7 tools)     │  │  Definitions    │  │              │ │
│  └────────────────┘  └─────────────────┘  └──────────────┘ │
│           ↓                                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            CLI Executor                                │ │
│  │  - Command builder                                     │ │
│  │  - Process spawner                                     │ │
│  │  - Output parser                                       │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────┘
                            │ child_process.spawn()
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   PDFTools CLI (Python)                      │
│  pdfmerge, pdfsplit, ocrutil, pdfgettxt, pdfprotect, ...    │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Datenfluss

```
1. LLM → MCP Request (JSON-RPC)
   ↓
2. Server → Parse & Validate Request
   ↓
3. Tool Registry → Find Tool Handler
   ↓
4. Schema Validator → Validate Parameters
   ↓
5. CLI Executor → Build Command
   ↓
6. child_process.spawn() → Execute Python CLI
   ↓
7. Parser → Parse stdout/stderr/exitCode
   ↓
8. Error Handler → Handle errors if any
   ↓
9. Server → Format MCP Response
   ↓
10. LLM ← MCP Response (JSON-RPC)
```

---

## 3. API Design

### 3.1 MCP Server Interface

#### 3.1.1 Server Initialization
```typescript
// src/server.ts
import { Server } from '@anthropic-ai/sdk/mcp';
import { ToolRegistry } from './tools';
import { PDFToolsCLI } from './executors/pdftools-cli';
import { ConfigLoader } from './config/config-loader';

export class PDFToolsMCPServer {
  private server: Server;
  private toolRegistry: ToolRegistry;
  private cliExecutor: PDFToolsCLI;

  constructor() {
    this.server = new Server({
      name: 'pdftools',
      version: '1.0.0'
    });

    this.cliExecutor = new PDFToolsCLI(
      ConfigLoader.getPDFToolsPath()
    );

    this.toolRegistry = new ToolRegistry(this.cliExecutor);
  }

  async start(): Promise<void> {
    // Register all tools
    this.toolRegistry.registerAll();

    // Setup handlers
    this.server.setToolHandler(async (request) => {
      return await this.toolRegistry.execute(request);
    });

    // Start server (stdio)
    await this.server.connect({
      transport: 'stdio'
    });
  }
}
```

### 3.2 Tool Definitions

#### 3.2.1 Base Tool Interface
```typescript
// src/tools/base-tool.ts
import { z } from 'zod';

export interface MCPTool {
  name: string;
  description: string;
  inputSchema: z.ZodObject<any>;
  execute(params: any): Promise<ToolResult>;
}

export interface ToolResult {
  success: boolean;
  output?: string;
  error?: ToolError;
}

export interface ToolError {
  code: string;
  message: string;
  details?: any;
}
```

#### 3.2.2 Example Tool: pdf_merge
```typescript
// src/tools/pdf-merge.ts
import { z } from 'zod';
import { MCPTool, ToolResult } from './base-tool';
import { PDFToolsCLI } from '../executors/pdftools-cli';

export class PdfMergeTool implements MCPTool {
  name = 'pdf_merge';
  description = 'Merge multiple PDF files into a single document. Preserves bookmarks and metadata.';

  inputSchema = z.object({
    files: z.array(z.string())
      .min(2, 'At least 2 files required')
      .describe('List of PDF file paths to merge'),
    output: z.string()
      .optional()
      .describe('Output path for merged PDF (default: merged.pdf)'),
    keep_bookmarks: z.boolean()
      .default(true)
      .describe('Preserve bookmarks from source PDFs'),
    verbose: z.boolean()
      .default(false)
      .describe('Enable verbose output')
  });

  constructor(private cli: PDFToolsCLI) {}

  async execute(params: z.infer<typeof this.inputSchema>): Promise<ToolResult> {
    const { files, output, keep_bookmarks, verbose } = params;

    // Build CLI arguments
    const args = [
      '-f', files.join(',')
    ];

    if (output) {
      args.push('-o', output);
    }

    if (!keep_bookmarks) {
      args.push('--no-bookmarks');
    }

    if (verbose) {
      args.push('--verbose');
    }

    // Execute CLI
    try {
      const result = await this.cli.execute('pdfmerge', args);

      if (result.exitCode === 0) {
        return {
          success: true,
          output: result.stdout
        };
      } else {
        return {
          success: false,
          error: {
            code: 'CLI_ERROR',
            message: result.stderr || 'Unknown error',
            details: { exitCode: result.exitCode }
          }
        };
      }
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'EXECUTION_ERROR',
          message: error.message,
          details: error
        }
      };
    }
  }
}
```

#### 3.2.3 All Tool Definitions

**1. pdf_merge**
```typescript
{
  name: 'pdf_merge',
  description: 'Merge multiple PDF files into one',
  inputSchema: {
    files: string[],      // min 2
    output?: string,
    keep_bookmarks?: boolean,
    verbose?: boolean
  }
}
```

**2. pdf_split**
```typescript
{
  name: 'pdf_split',
  description: 'Split PDF into multiple files',
  inputSchema: {
    input: string,        // required
    output_dir: string,   // required
    mode?: 'pages' | 'ranges' | 'parts' | 'specific',
    ranges?: string,      // for mode=ranges
    parts?: number,       // for mode=parts
    pages?: string,       // for mode=specific
    verbose?: boolean
  }
}
```

**3. pdf_ocr**
```typescript
{
  name: 'pdf_ocr',
  description: 'Extract text from scanned PDFs using OCR',
  inputSchema: {
    file: string,         // required
    language?: string,    // default: 'eng'
    output_mode?: 'txt' | 'pdf' | 'json',
    output?: string,
    pages?: string,
    dpi?: number,
    verbose?: boolean
  }
}
```

**4. pdf_extract_text**
```typescript
{
  name: 'pdf_extract_text',
  description: 'Extract text from PDF files',
  inputSchema: {
    file: string,         // required
    mode?: 'simple' | 'layout' | 'raw' | 'blocks',
    output?: string,
    pages?: string,
    format?: 'txt' | 'json',
    verbose?: boolean
  }
}
```

**5. pdf_protect**
```typescript
{
  name: 'pdf_protect',
  description: 'Add password protection to PDFs',
  inputSchema: {
    file: string,         // required
    output?: string,
    user_password?: string,
    owner_password?: string,
    permissions?: string[],
    verbose?: boolean
  }
}
```

**6. pdf_thumbnails**
```typescript
{
  name: 'pdf_thumbnails',
  description: 'Generate thumbnail images from PDFs',
  inputSchema: {
    file: string,         // required
    output_dir: string,   // required
    size?: number,        // default: 200
    format?: 'png' | 'jpg',
    pages?: string,
    verbose?: boolean
  }
}
```

**7. pdf_rename_invoice**
```typescript
{
  name: 'pdf_rename_invoice',
  description: 'Intelligently rename invoice PDFs based on content',
  inputSchema: {
    file: string,         // required
    template?: string,    // default: '{date}_{vendor}_{invoice_nr}.pdf'
    patterns?: string,    // path to custom patterns JSON
    output_dir?: string,
    dry_run?: boolean,
    verbose?: boolean
  }
}
```

### 3.3 CLI Executor

```typescript
// src/executors/pdftools-cli.ts
import { spawn } from 'child_process';
import { Logger } from '../utils/logger';

export interface CLIResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}

export class PDFToolsCLI {
  constructor(
    private pdftoolsPath: string = 'pdftools',
    private timeout: number = 300000  // 5 minutes
  ) {}

  async execute(command: string, args: string[]): Promise<CLIResult> {
    Logger.debug(`Executing: ${command} ${args.join(' ')}`);

    return new Promise((resolve, reject) => {
      const process = spawn(command, args, {
        timeout: this.timeout,
        env: { ...process.env }
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
        Logger.debug(`stdout: ${data}`);
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        Logger.debug(`stderr: ${data}`);
      });

      process.on('close', (code) => {
        resolve({
          exitCode: code ?? 0,
          stdout: stdout.trim(),
          stderr: stderr.trim()
        });
      });

      process.on('error', (error) => {
        reject(new Error(`Failed to execute ${command}: ${error.message}`));
      });
    });
  }

  async checkInstallation(): Promise<boolean> {
    try {
      const result = await this.execute('pdfmerge', ['--version']);
      return result.exitCode === 0;
    } catch {
      return false;
    }
  }
}
```

### 3.4 Tool Registry

```typescript
// src/tools/index.ts
import { MCPTool } from './base-tool';
import { PdfMergeTool } from './pdf-merge';
import { PdfSplitTool } from './pdf-split';
import { PdfOcrTool } from './pdf-ocr';
import { PdfExtractTextTool } from './pdf-extract-text';
import { PdfProtectTool } from './pdf-protect';
import { PdfThumbnailsTool } from './pdf-thumbnails';
import { PdfRenameTool } from './pdf-rename';
import { PDFToolsCLI } from '../executors/pdftools-cli';

export class ToolRegistry {
  private tools: Map<string, MCPTool> = new Map();

  constructor(private cli: PDFToolsCLI) {}

  registerAll(): void {
    this.register(new PdfMergeTool(this.cli));
    this.register(new PdfSplitTool(this.cli));
    this.register(new PdfOcrTool(this.cli));
    this.register(new PdfExtractTextTool(this.cli));
    this.register(new PdfProtectTool(this.cli));
    this.register(new PdfThumbnailsTool(this.cli));
    this.register(new PdfRenameTool(this.cli));
  }

  private register(tool: MCPTool): void {
    this.tools.set(tool.name, tool);
  }

  async execute(request: any): Promise<any> {
    const { name, parameters } = request;

    const tool = this.tools.get(name);
    if (!tool) {
      throw new Error(`Tool not found: ${name}`);
    }

    // Validate parameters
    const validatedParams = tool.inputSchema.parse(parameters);

    // Execute tool
    return await tool.execute(validatedParams);
  }

  listTools(): MCPTool[] {
    return Array.from(this.tools.values());
  }
}
```

---

## 4. Konfiguration

### 4.1 NPM Package Config

```json
// mcp-server/package.json
{
  "name": "@trosinde/mcp-pdftools",
  "version": "1.0.0",
  "description": "MCP Server for PDFTools - AI Agent Integration",
  "main": "dist/index.js",
  "bin": {
    "mcp-pdftools": "dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "ts-node src/index.ts",
    "test": "jest",
    "test:coverage": "jest --coverage",
    "postinstall": "node scripts/install.js"
  },
  "keywords": [
    "mcp",
    "pdf",
    "claude",
    "ai",
    "tools",
    "model-context-protocol"
  ],
  "author": "Thomas Rosinde",
  "license": "MIT",
  "dependencies": {
    "@anthropic-ai/sdk": "^0.10.0",
    "zod": "^3.22.4"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0",
    "ts-node": "^10.9.0",
    "jest": "^29.7.0",
    "@types/jest": "^29.5.0"
  },
  "peerDependencies": {
    "pdftools": ">=2.0.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 4.2 TypeScript Config

```json
// mcp-server/tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "tests"]
}
```

### 4.3 MCP Config Auto-Generation

```javascript
// scripts/config-generator.js
const fs = require('fs');
const os = require('os');
const path = require('path');

class MCPConfigGenerator {
  static generateClaudeDesktopConfig() {
    const configPath = path.join(
      os.homedir(),
      'Library/Application Support/Claude/claude_desktop_config.json'
    );

    const config = {
      mcpServers: {
        pdftools: {
          command: 'mcp-pdftools',
          args: []
        }
      }
    };

    // Merge with existing config if present
    if (fs.existsSync(configPath)) {
      const existing = JSON.parse(fs.readFileSync(configPath, 'utf-8'));
      existing.mcpServers = existing.mcpServers || {};
      existing.mcpServers.pdftools = config.mcpServers.pdftools;
      fs.writeFileSync(configPath, JSON.stringify(existing, null, 2));
    } else {
      fs.mkdirSync(path.dirname(configPath), { recursive: true });
      fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    }

    console.log('✅ Claude Desktop config updated');
  }

  static generateClaudeCodeConfig() {
    const config = {
      mcpServers: {
        pdftools: {
          command: 'mcp-pdftools',
          args: []
        }
      }
    };

    console.log('📋 Add this to your .claude/mcp_config.json:');
    console.log(JSON.stringify(config, null, 2));
  }
}

// Run on post-install
if (require.main === module) {
  try {
    MCPConfigGenerator.generateClaudeDesktopConfig();
    MCPConfigGenerator.generateClaudeCodeConfig();
  } catch (error) {
    console.warn('⚠️  Could not auto-configure. See README for manual setup.');
  }
}

module.exports = { MCPConfigGenerator };
```

---

## 5. Fehlerbehandlung

### 5.1 Error Types

```typescript
// src/utils/error-handler.ts
export enum ErrorCode {
  TOOL_NOT_FOUND = 'TOOL_NOT_FOUND',
  INVALID_PARAMETERS = 'INVALID_PARAMETERS',
  CLI_ERROR = 'CLI_ERROR',
  PDFTOOLS_NOT_INSTALLED = 'PDFTOOLS_NOT_INSTALLED',
  TIMEOUT = 'TIMEOUT',
  EXECUTION_ERROR = 'EXECUTION_ERROR'
}

export class MCPError extends Error {
  constructor(
    public code: ErrorCode,
    message: string,
    public details?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
        details: this.details
      }
    };
  }
}

export class ErrorHandler {
  static handle(error: any): MCPError {
    if (error instanceof MCPError) {
      return error;
    }

    if (error.name === 'ZodError') {
      return new MCPError(
        ErrorCode.INVALID_PARAMETERS,
        'Invalid parameters: ' + error.message,
        error.errors
      );
    }

    if (error.code === 'ENOENT') {
      return new MCPError(
        ErrorCode.PDFTOOLS_NOT_INSTALLED,
        'PDFTools CLI not found. Please install: pip install pdftools'
      );
    }

    if (error.killed) {
      return new MCPError(
        ErrorCode.TIMEOUT,
        'Command timed out'
      );
    }

    return new MCPError(
      ErrorCode.EXECUTION_ERROR,
      error.message,
      error
    );
  }
}
```

### 5.2 Error Response Format

```typescript
// MCP Error Response
{
  "jsonrpc": "2.0",
  "id": "request-123",
  "error": {
    "code": "CLI_ERROR",
    "message": "PDF file not found: /path/to/missing.pdf",
    "details": {
      "exitCode": 1,
      "stderr": "Error: File not found..."
    }
  }
}
```

---

## 6. Logging

### 6.1 Logger Implementation

```typescript
// src/utils/logger.ts
export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3
}

export class Logger {
  private static level: LogLevel = LogLevel.INFO;

  static setLevel(level: LogLevel): void {
    this.level = level;
  }

  static debug(message: string, meta?: any): void {
    if (this.level <= LogLevel.DEBUG) {
      console.error('[DEBUG]', message, meta || '');
    }
  }

  static info(message: string, meta?: any): void {
    if (this.level <= LogLevel.INFO) {
      console.error('[INFO]', message, meta || '');
    }
  }

  static warn(message: string, meta?: any): void {
    if (this.level <= LogLevel.WARN) {
      console.error('[WARN]', message, meta || '');
    }
  }

  static error(message: string, meta?: any): void {
    if (this.level <= LogLevel.ERROR) {
      console.error('[ERROR]', message, meta || '');
    }
  }
}

// Initialize from env
const logLevel = process.env.MCP_PDFTOOLS_LOG_LEVEL || 'info';
Logger.setLevel(LogLevel[logLevel.toUpperCase()] || LogLevel.INFO);
```

### 6.2 Log Examples

```typescript
// Startup
Logger.info('MCP Server starting...', { version: '1.0.0' });
Logger.info('PDFTools CLI found', { path: '/usr/local/bin/pdfmerge' });

// Tool execution
Logger.debug('Executing tool', { name: 'pdf_merge', params: {...} });
Logger.info('Tool executed successfully', { tool: 'pdf_merge', duration: 1234 });

// Errors
Logger.error('Tool execution failed', {
  tool: 'pdf_merge',
  error: 'File not found',
  exitCode: 1
});
```

---

## 7. Testing

### 7.1 Test Structure

```
tests/
├── unit/
│   ├── tools/
│   │   ├── pdf-merge.test.ts
│   │   ├── pdf-split.test.ts
│   │   └── ...
│   ├── executors/
│   │   └── cli-executor.test.ts
│   └── validators/
│       └── schema-validator.test.ts
│
├── integration/
│   ├── tool-registry.test.ts
│   ├── cli-integration.test.ts
│   └── error-handling.test.ts
│
└── e2e/
    ├── pdf-merge.e2e.test.ts
    ├── pdf-split.e2e.test.ts
    └── full-workflow.e2e.test.ts
```

### 7.2 Unit Test Examples

```typescript
// tests/unit/tools/pdf-merge.test.ts
import { PdfMergeTool } from '../../../src/tools/pdf-merge';
import { PDFToolsCLI } from '../../../src/executors/pdftools-cli';

describe('PdfMergeTool', () => {
  let tool: PdfMergeTool;
  let mockCLI: jest.Mocked<PDFToolsCLI>;

  beforeEach(() => {
    mockCLI = {
      execute: jest.fn()
    } as any;

    tool = new PdfMergeTool(mockCLI);
  });

  it('should validate parameters correctly', async () => {
    const params = {
      files: ['a.pdf', 'b.pdf'],
      output: 'merged.pdf'
    };

    expect(() => tool.inputSchema.parse(params)).not.toThrow();
  });

  it('should reject less than 2 files', () => {
    const params = { files: ['a.pdf'] };

    expect(() => tool.inputSchema.parse(params)).toThrow('At least 2 files');
  });

  it('should execute CLI with correct arguments', async () => {
    mockCLI.execute.mockResolvedValue({
      exitCode: 0,
      stdout: 'Success',
      stderr: ''
    });

    const result = await tool.execute({
      files: ['a.pdf', 'b.pdf'],
      output: 'out.pdf',
      keep_bookmarks: true
    });

    expect(mockCLI.execute).toHaveBeenCalledWith('pdfmerge', [
      '-f', 'a.pdf,b.pdf',
      '-o', 'out.pdf'
    ]);

    expect(result.success).toBe(true);
  });

  it('should handle CLI errors', async () => {
    mockCLI.execute.mockResolvedValue({
      exitCode: 1,
      stdout: '',
      stderr: 'File not found'
    });

    const result = await tool.execute({
      files: ['missing.pdf', 'b.pdf']
    });

    expect(result.success).toBe(false);
    expect(result.error?.code).toBe('CLI_ERROR');
  });
});
```

### 7.3 Integration Test Example

```typescript
// tests/integration/cli-integration.test.ts
import { PDFToolsCLI } from '../../src/executors/pdftools-cli';

describe('CLI Integration', () => {
  let cli: PDFToolsCLI;

  beforeAll(async () => {
    cli = new PDFToolsCLI();

    // Check if PDFTools is installed
    const installed = await cli.checkInstallation();
    if (!installed) {
      console.warn('PDFTools not installed, skipping integration tests');
    }
  });

  it('should execute pdfmerge successfully', async () => {
    const result = await cli.execute('pdfmerge', ['--version']);

    expect(result.exitCode).toBe(0);
    expect(result.stdout).toContain('1.0');
  }, 10000);

  it('should handle non-existent command', async () => {
    await expect(
      cli.execute('nonexistent', [])
    ).rejects.toThrow('Failed to execute');
  });
});
```

### 7.4 E2E Test Example

```typescript
// tests/e2e/pdf-merge.e2e.test.ts
import { PDFToolsMCPServer } from '../../src/server';
import * as fs from 'fs';
import * as path from 'path';

describe('PDF Merge E2E', () => {
  let server: PDFToolsMCPServer;
  const testDir = path.join(__dirname, '../fixtures');

  beforeAll(async () => {
    server = new PDFToolsMCPServer();
    await server.start();
  });

  it('should merge two PDFs', async () => {
    const request = {
      name: 'pdf_merge',
      parameters: {
        files: [
          path.join(testDir, 'test1.pdf'),
          path.join(testDir, 'test2.pdf')
        ],
        output: path.join(testDir, 'merged.pdf')
      }
    };

    const result = await server.handleToolCall(request);

    expect(result.success).toBe(true);
    expect(fs.existsSync(path.join(testDir, 'merged.pdf'))).toBe(true);

    // Cleanup
    fs.unlinkSync(path.join(testDir, 'merged.pdf'));
  }, 30000);
});
```

---

## 8. Performance

### 8.1 Performance-Ziele
- **Server Startup**: < 500ms
- **Tool Call Overhead**: < 100ms
- **Memory**: < 50 MB (Server nur, ohne CLI)

### 8.2 Optimierungen
- Lazy Loading von Tools
- Connection Pooling (falls später benötigt)
- Streaming für große Outputs (v2.0)

---

## 9. Security

### 9.1 Security Measures
- **Input Validation**: Zod schemas
- **Path Traversal Prevention**: Path normalization
- **No Shell Injection**: spawn() mit array args
- **Environment Isolation**: Separate process für CLI

---

## 10. Deployment

### 10.1 NPM Publishing

```bash
# Build
npm run build

# Test
npm test

# Publish
npm publish --access public
```

### 10.2 Installation

```bash
# Global
npm install -g @trosinde/mcp-pdftools

# Local (project-specific)
npm install @trosinde/mcp-pdftools
```

---

## 11. Documentation

### 11.1 MCP Server README

```markdown
# MCP PDFTools

MCP Server for PDFTools - AI Agent Integration

## Installation

\`\`\`bash
npm install -g @trosinde/mcp-pdftools
\`\`\`

## Configuration

### Claude Desktop

Config will be auto-generated at:
\`~/Library/Application Support/Claude/claude_desktop_config.json\`

### Claude Code

Add to \`.claude/mcp_config.json\`:
\`\`\`json
{
  "mcpServers": {
    "pdftools": {
      "command": "mcp-pdftools",
      "args": []
    }
  }
}
\`\`\`

## Available Tools

1. **pdf_merge** - Merge PDFs
2. **pdf_split** - Split PDFs
3. **pdf_ocr** - OCR extraction
4. **pdf_extract_text** - Text extraction
5. **pdf_protect** - Password protection
6. **pdf_thumbnails** - Generate thumbnails
7. **pdf_rename_invoice** - Rename invoices

## Requirements

- Node.js >= 18.0.0
- PDFTools Python package: \`pip install pdftools\`
\`\`\`

---

## 12. Implementation Plan

### Phase 1: Core Infrastructure (3-4h)
- [x] Project setup (package.json, tsconfig.json)
- [x] Base types & interfaces
- [x] CLI Executor
- [x] Logger & Error Handler

### Phase 2: Tool Implementation (6-8h)
- [x] pdf_merge tool
- [x] pdf_split tool
- [x] pdf_ocr tool
- [x] pdf_extract_text tool
- [x] pdf_protect tool
- [x] pdf_thumbnails tool
- [x] pdf_rename_invoice tool

### Phase 3: MCP Integration (4-5h)
- [x] MCP Server setup
- [x] Tool Registry
- [x] Schema Validator
- [x] Request/Response handling

### Phase 4: Testing (4-6h)
- [x] Unit tests (all tools)
- [x] Integration tests
- [x] E2E tests

### Phase 5: Packaging & Deployment (2-3h)
- [x] NPM package config
- [x] Build pipeline
- [x] Config auto-generation script
- [x] Documentation

**Total Estimate**: 19-26 hours

---

## 13. Review & Approval

### Architecture Review
**Reviewer**: Architecture Team
**Datum**: TBD
**Status**: Draft

**Checkpoints**:
- [ ] MCP Protocol korrekt implementiert
- [ ] Tool Schemas vollständig
- [ ] CLI Integration robust
- [ ] Error Handling klar
- [ ] Security Considerations beachtet
- [ ] Performance-Ziele erreichbar
- [ ] Test-Coverage ausreichend
- [ ] Documentation vollständig

### Team Review
- [ ] Node.js Entwickler: Implementation feasible?
- [ ] Python Entwickler: CLI-Integration OK?
- [ ] Tester: Test strategy clear?
- [ ] DevOps: NPM Publishing OK?

---

## 14. Änderungshistorie

| Datum | Version | Änderung | Von | Requirement Version |
|-------|---------|----------|-----|---------------------|
| 2025-11-22 | 1.0 | Initiales Design | Architecture Team | REQ-010 v1.0 |

---

## 15. Anhang

### 15.1 Referenzen
- Requirement: [REQ-010 v1.0](../requirements/REQ-010-mcp-server.md)
- MCP Protocol: https://modelcontextprotocol.io/
- Anthropic MCP SDK: https://github.com/anthropics/anthropic-sdk-typescript
- PDFTools: [README.md](../../README.md)

### 15.2 Offene Fragen
1. NPM Package Scope: @trosinde oder @pdftools? → **@trosinde**
2. Streaming Support: In v1.0 oder später? → **v2.0**
3. Progress Callbacks: Wie implementieren? → **TBD**
