/**
 * PDF Split Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFileExists, validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfSplitTool = {
  name: 'pdf_split',
  description: 'Split a PDF file into multiple files',
  inputSchema: {
    type: 'object',
    properties: {
      input_file: {
        type: 'string',
        description: 'Input PDF file to split',
      },
      output_dir: {
        type: 'string',
        description: 'Output directory for split files',
      },
      mode: {
        type: 'string',
        description: 'Split mode: pages (individual pages), ranges (page ranges), parts (N equal parts), or specific (specific pages)',
        enum: ['pages', 'ranges', 'parts', 'specific'],
        default: 'pages',
      },
      ranges: {
        type: 'array',
        description: 'Page ranges for "ranges" mode (e.g., ["1-3", "4-6"])',
        items: {
          type: 'string',
        },
      },
      num_parts: {
        type: 'integer',
        description: 'Number of parts for "parts" mode',
        minimum: 2,
      },
      pages: {
        type: 'array',
        description: 'Specific page numbers for "specific" mode',
        items: {
          type: 'integer',
        },
      },
    },
    required: ['input_file', 'output_dir', 'mode'],
  },
};

export async function handlePdfSplit(params: {
  input_file: string;
  output_dir: string;
  mode: 'pages' | 'ranges' | 'parts' | 'specific';
  ranges?: string[];
  num_parts?: number;
  pages?: number[];
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  // Validate required parameters
  const requiredValidation = validateRequired(params, ['input_file', 'output_dir', 'mode']);
  if (!requiredValidation.valid) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${requiredValidation.error}`,
        },
      ],
    };
  }

  // SECURITY: Validate input file path
  const inputPathValidation = validateSafePath(params.input_file);
  if (!inputPathValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${inputPathValidation.error}` }],
    };
  }

  // SECURITY: Validate output directory path
  const outputPathValidation = validateSafePath(params.output_dir);
  if (!outputPathValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${outputPathValidation.error}` }],
    };
  }

  // Validate input file exists
  const fileValidation = await validateFileExists(params.input_file);
  if (!fileValidation.valid) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${fileValidation.error}`,
        },
      ],
    };
  }

  // Build arguments for pdfsplit
  const args: string[] = [params.input_file, '-o', params.output_dir, '-m', params.mode];

  if (params.mode === 'ranges' && params.ranges) {
    args.push('-r', params.ranges.join(','));
  } else if (params.mode === 'parts' && params.num_parts) {
    args.push('-n', String(params.num_parts));
  } else if (params.mode === 'specific' && params.pages) {
    args.push('-p', params.pages.join(','));
  }

  try {
    const result = await executeTool('pdfsplit', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Successfully split PDF using mode "${params.mode}"\nOutput directory: ${params.output_dir}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error splitting PDF:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfsplit: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
