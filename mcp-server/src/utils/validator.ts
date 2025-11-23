/**
 * Input validation utilities for MCP tools
 */

import { access, constants } from 'fs/promises';

export interface ValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validate that a file exists and is readable
 */
export async function validateFileExists(filePath: string): Promise<ValidationResult> {
  try {
    await access(filePath, constants.R_OK);
    return { valid: true };
  } catch {
    return {
      valid: false,
      error: `File not found or not readable: ${filePath}`,
    };
  }
}

/**
 * Validate that multiple files exist
 */
export async function validateFilesExist(filePaths: string[]): Promise<ValidationResult> {
  for (const filePath of filePaths) {
    const result = await validateFileExists(filePath);
    if (!result.valid) {
      return result;
    }
  }
  return { valid: true };
}

/**
 * Validate file extension
 */
export function validateFileExtension(
  filePath: string,
  allowedExtensions: string[]
): ValidationResult {
  const ext = filePath.toLowerCase().split('.').pop();
  if (!ext || !allowedExtensions.includes(`.${ext}`)) {
    return {
      valid: false,
      error: `Invalid file extension. Allowed: ${allowedExtensions.join(', ')}`,
    };
  }
  return { valid: true };
}

/**
 * Validate that a path is safe (no directory traversal)
 * SECURITY: Prevents path traversal attacks (../../etc/passwd)
 */
export function validateSafePath(filePath: string): ValidationResult {
  // Check for directory traversal
  if (filePath.includes('..')) {
    return {
      valid: false,
      error: 'Directory traversal (..) is not allowed for security reasons',
    };
  }

  // Check for absolute paths (Unix)
  if (filePath.startsWith('/')) {
    return {
      valid: false,
      error: 'Absolute paths are not allowed. Use relative paths only.',
    };
  }

  // Check for absolute paths (Windows)
  if (/^[a-zA-Z]:/.test(filePath)) {
    return {
      valid: false,
      error: 'Absolute paths are not allowed. Use relative paths only.',
    };
  }

  // Check for null bytes (path injection)
  if (filePath.includes('\0')) {
    return {
      valid: false,
      error: 'Null bytes in paths are not allowed',
    };
  }

  return { valid: true };
}

/**
 * Validate number range
 */
export function validateNumberRange(
  value: number,
  min: number,
  max: number,
  fieldName: string
): ValidationResult {
  if (value < min || value > max) {
    return {
      valid: false,
      error: `${fieldName} must be between ${min} and ${max}`,
    };
  }
  return { valid: true };
}

/**
 * Validate required parameters
 */
export function validateRequired(
  params: Record<string, unknown>,
  requiredFields: string[]
): ValidationResult {
  for (const field of requiredFields) {
    if (params[field] === undefined || params[field] === null || params[field] === '') {
      return {
        valid: false,
        error: `Required parameter missing: ${field}`,
      };
    }
  }
  return { valid: true };
}
