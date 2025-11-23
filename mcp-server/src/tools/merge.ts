/**
 * PDF Merge Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFilesExist, validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfMergeTool = {
  name: 'pdf_merge',
  description: 'Merge multiple PDF files into a single PDF file',
  inputSchema: {
    type: 'object',
    properties: {
      input_files: {
        type: 'array',
        description: 'List of PDF files to merge (in order)',
        items: {
          type: 'string',
        },
        minItems: 2,
      },
      output_file: {
        type: 'string',
        description: 'Output PDF file path',
      },
      add_bookmarks: {
        type: 'boolean',
        description: 'Add bookmarks for each merged file',
        default: false,
      },
    },
    required: ['input_files', 'output_file'],
  },
};

export async function handlePdfMerge(params: {
  input_files: string[];
  output_file: string;
  add_bookmarks?: boolean;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  // Validate required parameters
  const requiredValidation = validateRequired(params, ['input_files', 'output_file']);
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

  // SECURITY: Validate all paths for safety
  for (const file of params.input_files) {
    const pathValidation = validateSafePath(file);
    if (!pathValidation.valid) {
      return {
        content: [{ type: 'text', text: `Error: ${pathValidation.error}` }],
      };
    }
  }

  const outputPathValidation = validateSafePath(params.output_file);
  if (!outputPathValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${outputPathValidation.error}` }],
    };
  }

  // Validate input files exist
  const filesValidation = await validateFilesExist(params.input_files);
  if (!filesValidation.valid) {
    return {
      content: [
        {
          type: 'text',
          text: `Error: ${filesValidation.error}`,
        },
      ],
    };
  }

  // Build arguments for pdfmerge
  const args: string[] = [...params.input_files, '-o', params.output_file];

  if (params.add_bookmarks) {
    args.push('--add-bookmarks');
  }

  try {
    const result = await executeTool('pdfmerge', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Successfully merged ${params.input_files.length} PDF files into ${params.output_file}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error merging PDFs:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfmerge: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
