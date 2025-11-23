/**
 * PDF Protection Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFileExists, validateRequired, validateSafePath } from '../utils/validator.js';

export const pdfProtectTool = {
  name: 'pdf_protect',
  description: 'Add password protection and permissions to PDF files',
  inputSchema: {
    type: 'object',
    properties: {
      input_file: {
        type: 'string',
        description: 'Input PDF file',
      },
      output_file: {
        type: 'string',
        description: 'Output protected PDF file',
      },
      user_password: {
        type: 'string',
        description: 'Password required to open the PDF',
      },
      owner_password: {
        type: 'string',
        description: 'Password required to change permissions (optional)',
      },
      allow_printing: {
        type: 'boolean',
        description: 'Allow printing',
        default: true,
      },
      allow_modification: {
        type: 'boolean',
        description: 'Allow content modification',
        default: false,
      },
      allow_copying: {
        type: 'boolean',
        description: 'Allow text/graphics copying',
        default: true,
      },
    },
    required: ['input_file', 'output_file', 'user_password'],
  },
};

export async function handlePdfProtect(params: {
  input_file: string;
  output_file: string;
  user_password: string;
  owner_password?: string;
  allow_printing?: boolean;
  allow_modification?: boolean;
  allow_copying?: boolean;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  const requiredValidation = validateRequired(params, ['input_file', 'output_file', 'user_password']);
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

  const args: string[] = [
    params.input_file,
    '-o', params.output_file,
    '--user-password', params.user_password,
  ];

  if (params.owner_password) {
    args.push('--owner-password', params.owner_password);
  }

  if (params.allow_printing !== undefined) {
    args.push(params.allow_printing ? '--allow-printing' : '--no-printing');
  }

  if (params.allow_modification !== undefined) {
    args.push(params.allow_modification ? '--allow-modification' : '--no-modification');
  }

  if (params.allow_copying !== undefined) {
    args.push(params.allow_copying ? '--allow-copying' : '--no-copying');
  }

  try {
    const result = await executeTool('pdfprotect', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Successfully protected PDF file\nInput: ${params.input_file}\nOutput: ${params.output_file}\n\nPermissions:\n- Printing: ${params.allow_printing !== false ? 'Allowed' : 'Denied'}\n- Modification: ${params.allow_modification ? 'Allowed' : 'Denied'}\n- Copying: ${params.allow_copying !== false ? 'Allowed' : 'Denied'}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error protecting PDF:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfprotect: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
