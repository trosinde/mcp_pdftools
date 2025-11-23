/**
 * PDF Rename (Invoice) Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfRenameTool = {
  name: 'pdf_rename_invoice',
  description: 'Intelligently rename invoice PDF files based on content (vendor, date, amount)',
  inputSchema: {
    type: 'object',
    properties: {
      files: {
        type: 'array',
        description: 'List of PDF invoice files to rename',
        items: {
          type: 'string',
        },
        minItems: 1,
      },
      template: {
        type: 'string',
        description: 'Naming template (e.g., "{vendor}_{date}_{amount}.pdf")',
        default: '{vendor}_{date}_{amount}.pdf',
      },
      patterns: {
        type: 'array',
        description: 'Custom regex patterns for extraction',
        items: {
          type: 'string',
        },
      },
      output_dir: {
        type: 'string',
        description: 'Output directory (optional, renames in place if not specified)',
      },
      dry_run: {
        type: 'boolean',
        description: 'Show what would be renamed without actually renaming',
        default: false,
      },
    },
    required: ['files'],
  },
};

export async function handlePdfRename(params: {
  files: string[];
  template?: string;
  patterns?: string[];
  output_dir?: string;
  dry_run?: boolean;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  const requiredValidation = validateRequired(params, ['files']);
  if (!requiredValidation.valid) {
    return {
      content: [{ type: 'text', text: `Error: ${requiredValidation.error}` }],
    };
  }

  // SECURITY: Validate all file paths
  for (const file of params.files) {
    const pathValidation = validateSafePath(file);
    if (!pathValidation.valid) {
      return {
        content: [{ type: 'text', text: `Error: ${pathValidation.error}` }],
      };
    }
  }

  // SECURITY: Validate output directory path if provided
  if (params.output_dir) {
    const outputPathValidation = validateSafePath(params.output_dir);
    if (!outputPathValidation.valid) {
      return {
        content: [{ type: 'text', text: `Error: ${outputPathValidation.error}` }],
      };
    }
  }

  const args: string[] = ['-f', ...params.files];

  if (params.template) {
    args.push('-t', params.template);
  }

  if (params.patterns && params.patterns.length > 0) {
    args.push('-p', params.patterns.join(','));
  }

  if (params.output_dir) {
    args.push('-o', params.output_dir);
  }

  if (params.dry_run) {
    args.push('-d');
  }

  try {
    const result = await executeTool('pdfrename', args);

    if (result.success) {
      const action = params.dry_run ? 'Would rename' : 'Renamed';
      return {
        content: [
          {
            type: 'text',
            text: `${action} ${params.files.length} invoice(s)\nTemplate: ${params.template || '{vendor}_{date}_{amount}.pdf'}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error renaming PDFs:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfrename: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
