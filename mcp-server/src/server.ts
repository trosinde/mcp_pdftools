#!/usr/bin/env node
/**
 * MCP Server for PDFTools
 * Exposes all 7 PDF tools as MCP tools for AI agents
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import { validateToolName, sanitizeErrorMessage } from './utils/security.js';

// Import tool definitions and handlers
import { pdfMergeTool, handlePdfMerge } from './tools/merge.js';
import { pdfSplitTool, handlePdfSplit } from './tools/split.js';
import { pdfExtractTextTool, handlePdfExtractText } from './tools/extract.js';
import { pdfOcrTool, handlePdfOcr } from './tools/ocr.js';
import { pdfProtectTool, handlePdfProtect } from './tools/protect.js';
import { pdfThumbnailsTool, handlePdfThumbnails } from './tools/thumbnails.js';
import { pdfRenameTool, handlePdfRename } from './tools/rename.js';

/**
 * Create and configure the MCP server
 */
export function createServer() {
  const server = new Server(
    {
      name: 'mcp-pdftools',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Register all 7 PDF tools
  const tools = [
    pdfMergeTool,
    pdfSplitTool,
    pdfExtractTextTool,
    pdfOcrTool,
    pdfProtectTool,
    pdfThumbnailsTool,
    pdfRenameTool,
  ];

  /**
   * Handle list_tools request
   */
  server.setRequestHandler(ListToolsRequestSchema, async () => ({
    tools,
  }));

  /**
   * Handle call_tool request
   */
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    // SECURITY: Validate tool name against whitelist
    const toolValidation = validateToolName(name);
    if (!toolValidation.valid) {
      return {
        content: [
          {
            type: 'text',
            text: toolValidation.error || 'Invalid tool name',
          },
        ],
        isError: true,
      };
    }

    try {
      switch (name) {
        case 'pdf_merge':
          return await handlePdfMerge(args as Parameters<typeof handlePdfMerge>[0]);

        case 'pdf_split':
          return await handlePdfSplit(args as Parameters<typeof handlePdfSplit>[0]);

        case 'pdf_extract_text':
          return await handlePdfExtractText(args as Parameters<typeof handlePdfExtractText>[0]);

        case 'pdf_ocr':
          return await handlePdfOcr(args as Parameters<typeof handlePdfOcr>[0]);

        case 'pdf_protect':
          return await handlePdfProtect(args as Parameters<typeof handlePdfProtect>[0]);

        case 'pdf_thumbnails':
          return await handlePdfThumbnails(args as Parameters<typeof handlePdfThumbnails>[0]);

        case 'pdf_rename_invoice':
          return await handlePdfRename(args as Parameters<typeof handlePdfRename>[0]);

        default:
          return {
            content: [
              {
                type: 'text',
                text: `Unknown tool: ${name}`,
              },
            ],
            isError: true,
          };
      }
    } catch (error) {
      // SECURITY: Sanitize error messages to prevent information disclosure
      const errorMessage = error instanceof Error ? error.message : String(error);
      const sanitized = sanitizeErrorMessage(errorMessage, `Tool execution failed`);

      return {
        content: [
          {
            type: 'text',
            text: sanitized,
          },
        ],
        isError: true,
      };
    }
  });

  return server;
}

/**
 * Run the MCP server
 */
export async function runServer() {
  const server = createServer();
  const transport = new StdioServerTransport();

  await server.connect(transport);

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    await server.close();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await server.close();
    process.exit(0);
  });
}
