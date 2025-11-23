/**
 * Integration Tests for MCP Server
 * Tests server startup, tool registration, and basic functionality
 */

import { describe, it, expect, beforeAll, afterAll } from '@jest/globals';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

describe('MCP Server Integration', () => {
  // Note: We don't actually start the server in these tests
  // These are file existence and import tests only

  beforeAll(() => {
    // Tests run after build, so dist/index.js should exist
  });

  afterAll(() => {
    // Cleanup if needed
  });

  it('should have built server files', async () => {
    const { access } = await import('fs/promises');
    const serverPath = resolve(__dirname, '../../dist/index.js');

    await expect(access(serverPath)).resolves.not.toThrow();
  });

  it('should have all required tool files', async () => {
    const { access } = await import('fs/promises');
    const distPath = resolve(__dirname, '../../dist');

    const requiredFiles = [
      'index.js',
      'server.js',
      'tools/merge.js',
      'tools/split.js',
      'tools/extract.js',
      'tools/ocr.js',
      'tools/protect.js',
      'tools/thumbnails.js',
      'tools/rename.js',
      'utils/validator.js',
      'utils/security.js',
      'utils/executor.js',
      'utils/config.js',
    ];

    for (const file of requiredFiles) {
      const filePath = resolve(distPath, file);
      await expect(access(filePath)).resolves.not.toThrow();
    }
  });

  it('should export all 7 tool definitions', async () => {
    const merge = await import('../../dist/tools/merge.js');
    const split = await import('../../dist/tools/split.js');
    const extract = await import('../../dist/tools/extract.js');
    const ocr = await import('../../dist/tools/ocr.js');
    const protect = await import('../../dist/tools/protect.js');
    const thumbnails = await import('../../dist/tools/thumbnails.js');
    const rename = await import('../../dist/tools/rename.js');

    expect(merge.pdfMergeTool).toBeDefined();
    expect(merge.pdfMergeTool.name).toBe('pdf_merge');

    expect(split.pdfSplitTool).toBeDefined();
    expect(split.pdfSplitTool.name).toBe('pdf_split');

    expect(extract.pdfExtractTextTool).toBeDefined();
    expect(extract.pdfExtractTextTool.name).toBe('pdf_extract_text');

    expect(ocr.pdfOcrTool).toBeDefined();
    expect(ocr.pdfOcrTool.name).toBe('pdf_ocr');

    expect(protect.pdfProtectTool).toBeDefined();
    expect(protect.pdfProtectTool.name).toBe('pdf_protect');

    expect(thumbnails.pdfThumbnailsTool).toBeDefined();
    expect(thumbnails.pdfThumbnailsTool.name).toBe('pdf_thumbnails');

    expect(rename.pdfRenameTool).toBeDefined();
    expect(rename.pdfRenameTool.name).toBe('pdf_rename_invoice');
  });

  it('should have security utilities available', async () => {
    const security = await import('../../dist/utils/security.js');

    expect(security.validateToolName).toBeDefined();
    expect(security.sanitizeErrorMessage).toBeDefined();
    expect(security.validatePasswordStrength).toBeDefined();
  });

  it('should validate tool names correctly', async () => {
    const { validateToolName } = await import('../../dist/utils/security.js');

    // Valid tools
    expect(validateToolName('pdf_merge').valid).toBe(true);
    expect(validateToolName('pdf_split').valid).toBe(true);
    expect(validateToolName('pdf_extract_text').valid).toBe(true);
    expect(validateToolName('pdf_ocr').valid).toBe(true);
    expect(validateToolName('pdf_protect').valid).toBe(true);
    expect(validateToolName('pdf_thumbnails').valid).toBe(true);
    expect(validateToolName('pdf_rename_invoice').valid).toBe(true);

    // Invalid tools
    expect(validateToolName('malicious_tool').valid).toBe(false);
    expect(validateToolName('').valid).toBe(false);
  });

  it('should have configuration management available', async () => {
    const config = await import('../../dist/utils/config.js');

    expect(config.loadConfig).toBeDefined();
    expect(config.getToolPath).toBeDefined();
  });

  it('should validate safe paths correctly', async () => {
    const { validateSafePath } = await import('../../dist/utils/validator.js');

    // Safe paths
    expect(validateSafePath('document.pdf').valid).toBe(true);
    expect(validateSafePath('folder/file.pdf').valid).toBe(true);

    // Unsafe paths
    expect(validateSafePath('../etc/passwd').valid).toBe(false);
    expect(validateSafePath('/etc/passwd').valid).toBe(false);
    expect(validateSafePath('C:\\Windows\\System32').valid).toBe(false);
    expect(validateSafePath('file\0.pdf').valid).toBe(false);
  });
});

describe('MCP Server Configuration Health Check', () => {
  it('should have package.json with correct metadata', async () => {
    const { readFile } = await import('fs/promises');
    const packagePath = resolve(__dirname, '../../package.json');
    const packageContent = await readFile(packagePath, 'utf-8');
    const pkg = JSON.parse(packageContent);

    expect(pkg.name).toBe('@trosinde/mcp-pdftools');
    expect(pkg.version).toBeDefined();
    expect(pkg.main).toBe('dist/index.js');
    expect(pkg.bin['mcp-pdftools']).toBe('./dist/index.js');
    expect(pkg.dependencies['@modelcontextprotocol/sdk']).toBeDefined();
  });

  it('should have TypeScript configuration', async () => {
    const { access } = await import('fs/promises');
    const tsconfigPath = resolve(__dirname, '../../tsconfig.json');

    await expect(access(tsconfigPath)).resolves.not.toThrow();
  });

  it('should have Jest configuration', async () => {
    const { access } = await import('fs/promises');
    const jestConfigPath = resolve(__dirname, '../../jest.config.js');

    await expect(access(jestConfigPath)).resolves.not.toThrow();
  });

  it('should have all required npm scripts', async () => {
    const { readFile } = await import('fs/promises');
    const packagePath = resolve(__dirname, '../../package.json');
    const packageContent = await readFile(packagePath, 'utf-8');
    const pkg = JSON.parse(packageContent);

    expect(pkg.scripts.build).toBeDefined();
    expect(pkg.scripts.test).toBeDefined();
    expect(pkg.scripts.watch).toBeDefined();
    expect(pkg.scripts.prepare).toBeDefined();
  });
});
