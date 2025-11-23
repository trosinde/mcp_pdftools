/**
 * Unit Tests for Security Functions
 * CRITICAL: Security module tests
 */

import { describe, it, expect } from '@jest/globals';
import {
  validateToolName,
  sanitizeErrorMessage,
  validatePasswordStrength,
} from '../../src/utils/security.js';

describe('validateToolName', () => {
  it('should accept valid tool names', () => {
    expect(validateToolName('pdf_merge').valid).toBe(true);
    expect(validateToolName('pdf_split').valid).toBe(true);
    expect(validateToolName('pdf_extract_text').valid).toBe(true);
    expect(validateToolName('pdf_ocr').valid).toBe(true);
    expect(validateToolName('pdf_protect').valid).toBe(true);
    expect(validateToolName('pdf_thumbnails').valid).toBe(true);
    expect(validateToolName('pdf_rename_invoice').valid).toBe(true);
  });

  it('should reject invalid tool names', () => {
    expect(validateToolName('malicious_tool').valid).toBe(false);
    expect(validateToolName('../../etc/passwd').valid).toBe(false);
    expect(validateToolName('rm -rf /').valid).toBe(false);
  });

  it('should reject empty or null tool names', () => {
    expect(validateToolName('').valid).toBe(false);
    expect(validateToolName(' ').valid).toBe(false);
  });
});

describe('sanitizeErrorMessage', () => {
  it('should remove absolute Unix paths', () => {
    const error = 'File not found: /home/user/secret.pdf';
    const sanitized = sanitizeErrorMessage(error);
    expect(sanitized).not.toContain('/home/user/secret.pdf');
    expect(sanitized).toContain('<user-path>');
  });

  it('should remove absolute Windows paths', () => {
    const error = 'Error accessing C:\\Users\\Admin\\secret.docx';
    const sanitized = sanitizeErrorMessage(error);
    expect(sanitized).not.toContain('C:\\Users\\Admin');
    expect(sanitized).toContain('<path>');
  });

  it('should remove /etc/ paths specifically', () => {
    const error = 'Cannot read /etc/passwd';
    const sanitized = sanitizeErrorMessage(error);
    expect(sanitized).not.toContain('/etc/passwd');
    expect(sanitized).toContain('<system-path>');
  });

  it('should preserve relative paths', () => {
    const error = 'File not found: document.pdf';
    const sanitized = sanitizeErrorMessage(error);
    expect(sanitized).toContain('document.pdf');
  });

  it('should add contextual hint if provided', () => {
    const error = 'Something failed';
    const sanitized = sanitizeErrorMessage(error, 'PDF merge');
    expect(sanitized).toContain('PDF merge:');
  });
});

describe('validatePasswordStrength', () => {
  it('should accept strong passwords', () => {
    expect(validatePasswordStrength('Password123!').valid).toBe(true);
    expect(validatePasswordStrength('12345678').valid).toBe(true);
  });

  it('should reject weak passwords', () => {
    expect(validatePasswordStrength('12345').valid).toBe(false);
    expect(validatePasswordStrength('short').valid).toBe(false);
    expect(validatePasswordStrength('').valid).toBe(false);
  });
});
