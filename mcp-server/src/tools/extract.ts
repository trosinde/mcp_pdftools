/**
 * PDF Text Extraction Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFileExists, validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfExtractTextTool = {
  name: 'pdf_extract_text',
  description: 'Extract text content from PDF files',
  inputSchema: {
    type: 'object',
    properties: {
      input_file: {
        type: 'string',
        description: 'Input PDF file',
      },
      output_file: {
        type: 'string',
        description: 'Output text file (optional, prints to stdout if not specified)',
      },
      mode: {
        type: 'string',
        description: 'Extraction mode: simple, layout, per_page, or structured',
        enum: ['simple', 'layout', 'per_page', 'structured'],
        default: 'simple',
      },
    },
    required: ['input_file'],
  },
};

export async function handlePdfExtractText(params: {
  input_file: string;
  output_file?: string;
  mode?: string;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  const requiredValidation = validateRequired(params, ['input_file']);
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

  // SECURITY: Validate output file path if provided
  if (params.output_file) {
    const outputPathValidation = validateSafePath(params.output_file);
    if (!outputPathValidation.valid) {
      return {
        content: [{ type: 'text', text: `Error: ${outputPathValidation.error}` }],
      };
    }
  }

  const fileValidation = await validateFileExists(params.input_file);
  if (!fileValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${fileValidation.error}` }],
    };
  }

  const args: string[] = ['-i', params.input_file];

  if (params.output_file) {
    args.push('-o', params.output_file);
  }

  if (params.mode) {
    args.push('-m', params.mode);
  }

  try {
    const result = await executeTool('pdfgettxt', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: params.output_file
              ? `Successfully extracted text to ${params.output_file}\n\n${result.stdout}`
              : `Extracted text:\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error extracting text:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfgettxt: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
