/**
 * Configuration Management for MCP PDFTools
 * Supports environment variables and automatic discovery
 */

import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import { access, constants } from 'fs/promises';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface MCPConfig {
  venvPath: string;
  toolsPath: string;
  timeout: number;
  maxOutputSize: number;
}

/**
 * Discover the Python virtual environment path
 * Tries multiple locations in order of preference
 */
async function discoverVenvPath(): Promise<string | null> {
  const candidates = [
    // 1. Environment variable (highest priority)
    process.env.MCP_PDFTOOLS_VENV,

    // 2. Repository root venv (development)
    resolve(__dirname, '../../../venv/bin/python'),

    // 3. System-wide installation
    resolve(process.env.HOME || '/root', 'mcp_pdftools/venv/bin/python'),

    // 4. Current directory venv
    resolve(process.cwd(), 'venv/bin/python'),

    // 5. Parent directory venv
    resolve(process.cwd(), '../venv/bin/python'),
  ].filter((p): p is string => p !== undefined);

  for (const candidate of candidates) {
    try {
      await access(candidate, constants.X_OK);
      return candidate;
    } catch {
      // Try next candidate
    }
  }

  return null;
}

/**
 * Discover CLI tools path
 * Returns the directory containing pdfmerge, pdfsplit, etc.
 */
async function discoverToolsPath(): Promise<string | null> {
  const venvPath = await discoverVenvPath();
  if (!venvPath) {
    return null;
  }

  // Tools should be in same directory as python
  const toolsDir = dirname(venvPath);

  // Verify at least one tool exists
  try {
    await access(resolve(toolsDir, 'pdfmerge'), constants.X_OK);
    return toolsDir;
  } catch {
    return null;
  }
}

/**
 * Load configuration with automatic discovery
 */
export async function loadConfig(): Promise<MCPConfig> {
  const venvPath = await discoverVenvPath();
  const toolsPath = await discoverToolsPath();

  if (!venvPath || !toolsPath) {
    throw new Error(
      'Could not find PDFTools installation. ' +
        'Please set MCP_PDFTOOLS_VENV environment variable or ensure venv exists.'
    );
  }

  return {
    venvPath,
    toolsPath,
    timeout: parseInt(process.env.MCP_PDFTOOLS_TIMEOUT || '300000', 10), // 5 min default
    maxOutputSize: parseInt(process.env.MCP_PDFTOOLS_MAX_OUTPUT || '10485760', 10), // 10MB default
  };
}

/**
 * Get path to a specific CLI tool
 */
export function getToolPath(config: MCPConfig, toolName: string): string {
  return resolve(config.toolsPath, toolName);
}
