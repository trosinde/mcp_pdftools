#!/usr/bin/env node
/**
 * Python CLI Executor for MCP PDFTools
 * Executes Python CLI tools and returns results
 */

import { spawn } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

export interface ExecutionResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exitCode: number;
}

import { loadConfig, getToolPath as getConfigToolPath } from './config.js';

// Cache configuration
let cachedConfig: Awaited<ReturnType<typeof loadConfig>> | null = null;

/**
 * Get or load configuration
 */
async function getConfig() {
  if (!cachedConfig) {
    cachedConfig = await loadConfig();
  }
  return cachedConfig;
}

/**
 * Execute a Python CLI tool
 * @param toolName - Name of the CLI tool (e.g., 'pdfmerge', 'pdfsplit')
 * @param args - Arguments to pass to the tool
 * @param options - Execution options
 */
export async function executeTool(
  toolName: string,
  args: string[],
  options: { timeout?: number } = {}
): Promise<ExecutionResult> {
  const config = await getConfig();
  const timeout = options.timeout || config.timeout;
  const toolPath = getConfigToolPath(config, toolName);
  const maxOutputSize = config.maxOutputSize;

  return new Promise((resolve, reject) => {
    let stdout = '';
    let stderr = '';
    let timedOut = false;

    const child = spawn(toolPath, args, {
      env: {
        ...process.env,
        PYTHONUNBUFFERED: '1', // Disable Python output buffering
      },
    });

    // Timeout handler
    const timeoutId = setTimeout(() => {
      timedOut = true;
      child.kill('SIGTERM');
    }, timeout);

    // Collect stdout (with size limit)
    child.stdout.on('data', (data) => {
      const chunk = data.toString();
      if (stdout.length + chunk.length > maxOutputSize) {
        child.kill('SIGTERM');
        stderr += `\nOutput size limit exceeded (${maxOutputSize} bytes)`;
      } else {
        stdout += chunk;
      }
    });

    // Collect stderr (with size limit)
    child.stderr.on('data', (data) => {
      const chunk = data.toString();
      if (stderr.length + chunk.length > maxOutputSize) {
        child.kill('SIGTERM');
      } else {
        stderr += chunk;
      }
    });

    // Handle process exit
    child.on('close', (exitCode) => {
      clearTimeout(timeoutId);

      if (timedOut) {
        resolve({
          success: false,
          stdout,
          stderr: `Tool execution timed out after ${timeout}ms\n${stderr}`,
          exitCode: -1,
        });
      } else {
        resolve({
          success: exitCode === 0,
          stdout,
          stderr,
          exitCode: exitCode || 0,
        });
      }
    });

    // Handle errors
    child.on('error', (error) => {
      clearTimeout(timeoutId);
      reject(new Error(`Failed to execute ${toolName}: ${error.message}`));
    });
  });
}

/**
 * Validate that a file exists and is accessible
 */
export async function validateFile(filePath: string): Promise<boolean> {
  try {
    const { access } = await import('fs/promises');
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

/**
 * Format error message for MCP response
 */
export function formatError(error: Error | string): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}
