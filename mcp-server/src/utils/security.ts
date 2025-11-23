/**
 * Security utilities for MCP PDFTools
 * CRITICAL: These functions prevent security vulnerabilities
 */

import { validateSafePath } from './validator.js';

/**
 * Validate array of file paths for security
 * SECURITY: Prevents path traversal attacks
 */
export async function validatePathsSecurity(paths: string[]): Promise<{ valid: boolean; error?: string }> {
  for (const path of paths) {
    const result = validateSafePath(path);
    if (!result.valid) {
      return result;
    }
  }
  return { valid: true };
}

/**
 * Sanitize error messages to prevent information disclosure
 * SECURITY: Prevents leaking internal file paths
 */
export function sanitizeErrorMessage(error: string, contextualHint?: string): string {
  // Remove specific file patterns first (more specific patterns before general ones)
  let sanitized = error.replace(/\/etc\/[^\s]+/g, '<system-path>');
  sanitized = sanitized.replace(/\/home\/[^\s]+/g, '<user-path>');

  // Remove general absolute paths
  sanitized = sanitized.replace(/\/[^\s]+/g, '<path>');
  sanitized = sanitized.replace(/[A-Z]:\\[^\s]+/g, '<path>');

  if (contextualHint) {
    sanitized = `${contextualHint}: ${sanitized}`;
  }

  return sanitized;
}

/**
 * List of allowed PDF tool names
 * SECURITY: Prevents arbitrary command execution
 */
const ALLOWED_TOOLS = new Set([
  'pdf_merge',
  'pdf_split',
  'pdf_extract_text',
  'pdf_ocr',
  'pdf_protect',
  'pdf_thumbnails',
  'pdf_rename_invoice',
]);

/**
 * Validate that a tool name is in the whitelist
 * SECURITY: Prevents tool name injection
 */
export function validateToolName(toolName: string): { valid: boolean; error?: string } {
  if (!ALLOWED_TOOLS.has(toolName)) {
    return {
      valid: false,
      error: `Unknown or unauthorized tool: ${toolName}`,
    };
  }
  return { valid: true };
}

/**
 * Validate password strength (basic check)
 * SECURITY: Ensure passwords meet minimum requirements
 */
export function validatePasswordStrength(password: string): { valid: boolean; error?: string } {
  if (password.length < 8) {
    return {
      valid: false,
      error: 'Password must be at least 8 characters long',
    };
  }
  return { valid: true };
}
