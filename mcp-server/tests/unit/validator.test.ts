/**
 * Unit Tests for Validators
 * CRITICAL: Security validation tests
 */

import { describe, it, expect } from '@jest/globals';
import {
  validateSafePath,
  validateRequired,
  validateNumberRange,
} from '../../src/utils/validator.js';

describe('validateSafePath', () => {
  it('should accept relative paths', () => {
    expect(validateSafePath('document.pdf').valid).toBe(true);
    expect(validateSafePath('folder/document.pdf').valid).toBe(true);
    expect(validateSafePath('./document.pdf').valid).toBe(true);
  });

  it('should reject directory traversal attempts', () => {
    expect(validateSafePath('../etc/passwd').valid).toBe(false);
    expect(validateSafePath('../../secret.pdf').valid).toBe(false);
    expect(validateSafePath('folder/../../../etc/passwd').valid).toBe(false);
  });

  it('should reject absolute paths (Unix)', () => {
    expect(validateSafePath('/etc/passwd').valid).toBe(false);
    expect(validateSafePath('/home/user/file.pdf').valid).toBe(false);
  });

  it('should reject absolute paths (Windows)', () => {
    expect(validateSafePath('C:\\Windows\\System32').valid).toBe(false);
    expect(validateSafePath('D:\\secret.pdf').valid).toBe(false);
  });

  it('should reject null byte injection', () => {
    expect(validateSafePath('file\0.pdf').valid).toBe(false);
  });
});

describe('validateRequired', () => {
  it('should pass when all required fields present', () => {
    const params = { name: 'test', value: 123 };
    expect(validateRequired(params, ['name', 'value']).valid).toBe(true);
  });

  it('should fail when required field missing', () => {
    const params = { name: 'test' };
    expect(validateRequired(params, ['name', 'value']).valid).toBe(false);
  });

  it('should fail when field is null', () => {
    const params = { name: null };
    expect(validateRequired(params, ['name']).valid).toBe(false);
  });

  it('should fail when field is empty string', () => {
    const params = { name: '' };
    expect(validateRequired(params, ['name']).valid).toBe(false);
  });
});

describe('validateNumberRange', () => {
  it('should pass when number in range', () => {
    expect(validateNumberRange(5, 1, 10, 'value').valid).toBe(true);
    expect(validateNumberRange(1, 1, 10, 'value').valid).toBe(true);
    expect(validateNumberRange(10, 1, 10, 'value').valid).toBe(true);
  });

  it('should fail when number below minimum', () => {
    expect(validateNumberRange(0, 1, 10, 'value').valid).toBe(false);
  });

  it('should fail when number above maximum', () => {
    expect(validateNumberRange(11, 1, 10, 'value').valid).toBe(false);
  });
});
