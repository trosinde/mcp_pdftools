/**
 * PDF Thumbnails Tool - MCP Implementation
 */

import { executeTool } from '../utils/executor.js';
import { validateFileExists, validateRequired, validateNumberRange, validateSafePath } from '../utils/validator.js';

export const pdfThumbnailsTool = {
  name: 'pdf_thumbnails',
  description: 'Generate thumbnail images from PDF pages',
  inputSchema: {
    type: 'object',
    properties: {
      input_file: {
        type: 'string',
        description: 'Input PDF file',
      },
      output_dir: {
        type: 'string',
        description: 'Output directory for thumbnail images',
      },
      size: {
        type: 'integer',
        description: 'Thumbnail size in pixels (width)',
        default: 200,
        minimum: 50,
        maximum: 1000,
      },
      format: {
        type: 'string',
        description: 'Image format: png, jpg, or webp',
        enum: ['png', 'jpg', 'webp'],
        default: 'png',
      },
      pages: {
        type: 'string',
        description: 'Page range (e.g., "1-5", "all")',
        default: 'all',
      },
    },
    required: ['input_file', 'output_dir'],
  },
};

export async function handlePdfThumbnails(params: {
  input_file: string;
  output_dir: string;
  size?: number;
  format?: string;
  pages?: string;
}): Promise<{ content: Array<{ type: string; text: string }> }> {
  const requiredValidation = validateRequired(params, ['input_file', 'output_dir']);
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

  // SECURITY: Validate output directory path
  const outputPathValidation = validateSafePath(params.output_dir);
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

  if (params.size) {
    const sizeValidation = validateNumberRange(params.size, 50, 1000, 'size');
    if (!sizeValidation.valid) {
      return {
        content: [{ type: 'text', text: `Error: ${sizeValidation.error}` }],
      };
    }
  }

  const args: string[] = [params.input_file, '-o', params.output_dir];

  if (params.size) {
    args.push('-s', String(params.size));
  }

  if (params.format) {
    args.push('-f', params.format);
  }

  if (params.pages) {
    args.push('-p', params.pages);
  }

  try {
    const result = await executeTool('pdfthumbnails', args);

    if (result.success) {
      return {
        content: [
          {
            type: 'text',
            text: `Successfully generated thumbnails\nInput: ${params.input_file}\nOutput directory: ${params.output_dir}\nSize: ${params.size || 200}px\nFormat: ${params.format || 'png'}\n\n${result.stdout}`,
          },
        ],
      };
    } else {
      return {
        content: [
          {
            type: 'text',
            text: `Error generating thumbnails:\n${result.stderr}\n\nExit code: ${result.exitCode}`,
          },
        ],
      };
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `Error executing pdfthumbnails: ${error instanceof Error ? error.message : String(error)}`,
        },
      ],
    };
  }
}
