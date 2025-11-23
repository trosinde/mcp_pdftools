/**
 * PDF OCR Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFileExists, validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfOcrTool = {
  name: 'pdf_ocr',
  description: 'Extract text from scanned PDFs using OCR (Optical Character Recognition)',
  inputSchema: {
    type: 'object',
    properties: {
      input_file: {
        type: 'string',
        description: 'Input PDF file (scanned document)',
      },
      output_file: {
        type: 'string',
        description: 'Output file path',
      },
      language: {
        type: 'string',
        description: 'OCR language code (e.g., "eng" for English, "deu" for German)',
        default: 'eng',
      },
      output_mode: {
        type: 'string',
        description: 'Output format: txt (plain text), pdf (searchable PDF), or json (structured)',
        enum: ['txt', 'pdf', 'json'],
        default: 'txt',
      },
    },
    required: ['input_file', 'output_file'],
  },
};

export async function handlePdfOcr(params: {
  input_file: string;
  output_file: string;
  language?: string;
  output_mode?: string;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  const requiredValidation = validateRequired(params, ['input_file', 'output_file']);
  if (!requiredValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${requiredValidation.error}` }],
    };
  }

  // SECURITY: Validate input file path
  const inputPathValidation = validateSafePath(params.input_file);
  if (!inputPathValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${inputPathValidation.error}` }],
    };
  }

  // SECURITY: Validate output file path
  const outputPathValidation = validateSafePath(params.output_file);
  if (!outputPathValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${outputPathValidation.error}` }],
    };
  }

  const fileValidation = await validateFileExists(params.input_file);
  if (!fileValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${fileValidation.error}` }],
    };
  }

  const args: string[] = ['-f', params.input_file, '-o', params.output_file];

  if (params.language) {
    args.push('-l', params.language);
  }

  if (params.output_mode) {
    args.push('--output-mode', params.output_mode);
  }

  try {
    const result = await executeTool('ocrutil', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Successfully performed OCR on ${params.input_file}\nOutput: ${params.output_file}\nLanguage: ${params.language || 'eng'}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error performing OCR:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing ocrutil: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
