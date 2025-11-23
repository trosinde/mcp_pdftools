#!/usr/bin/env node
/**
 * MCP PDFTools Server - Entry Point
 *
 * This is the main entry point for the MCP server.
 * It can be run directly or used as a module.
 *
 * Usage:
 *   node dist/index.js
 *   mcp-pdftools
 */

import { runServer } from './server.js';

/**
 * Main entry point
 */
async function main() {
  try {
    await runServer();
  } catch (error) {
    console.error('Fatal error starting MCP server:', error);
    process.exit(1);
  }
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}

export { createServer, runServer } from './server.js';
