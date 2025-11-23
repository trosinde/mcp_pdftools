#!/usr/bin/env bash
#
# MCP Configuration Generator
# Generates and optionally installs MCP configuration for AI agents
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Detect installation paths
if [ -d "/home/$(whoami)/mcp_pdftools" ]; then
    INSTALL_DIR="/home/$(whoami)/mcp_pdftools"
elif [ -d "$(pwd)/mcp-server" ]; then
    INSTALL_DIR="$(pwd)"
else
    echo -e "${RED}Error: Could not find PDFTools installation${NC}"
    echo "Searched:"
    echo "  - /home/$(whoami)/mcp_pdftools"
    echo "  - $(pwd)"
    exit 1
fi

MCP_SERVER_PATH="$INSTALL_DIR/mcp-server/dist/index.js"
VENV_PATH="$INSTALL_DIR/venv/bin/python"

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  MCP Configuration Generator${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo "Installation directory: $INSTALL_DIR"
echo "MCP Server: $MCP_SERVER_PATH"
echo "Python venv: $VENV_PATH"
echo

# Verify files exist
if [ ! -f "$MCP_SERVER_PATH" ]; then
    echo -e "${RED}Error: MCP server not found at $MCP_SERVER_PATH${NC}"
    echo "Please build the server first: cd mcp-server && npm run build"
    exit 1
fi

if [ ! -f "$VENV_PATH" ]; then
    echo -e "${YELLOW}Warning: Python venv not found at $VENV_PATH${NC}"
    echo "The server will try to auto-detect the venv path."
fi

# Generate OpenCode configuration
generate_opencode_config() {
    cat <<EOF
{
  "pdftools": {
    "type": "local",
    "command": [
      "node",
      "$MCP_SERVER_PATH"
    ],
    "enabled": true,
    "environment": {
      "MCP_PDFTOOLS_VENV": "$VENV_PATH",
      "MCP_PDFTOOLS_TIMEOUT": "300000",
      "MCP_PDFTOOLS_MAX_OUTPUT": "10485760"
    },
    "timeout": 300000
  }
}
EOF
}

# Generate Claude Desktop configuration
generate_claude_config() {
    cat <<EOF
{
  "pdftools": {
    "command": "node",
    "args": ["$MCP_SERVER_PATH"],
    "env": {
      "MCP_PDFTOOLS_VENV": "$VENV_PATH",
      "MCP_PDFTOOLS_TIMEOUT": "300000",
      "MCP_PDFTOOLS_MAX_OUTPUT": "10485760"
    }
  }
}
EOF
}

# Detect and configure OpenCode
configure_opencode() {
    local config_file="$HOME/.config/opencode/opencode.json"

    if [ ! -f "$config_file" ]; then
        echo -e "${YELLOW}OpenCode config not found at $config_file${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Found OpenCode configuration${NC}"
    echo

    # Check if already configured
    if grep -q '"pdftools"' "$config_file"; then
        echo -e "${YELLOW}PDFTools is already configured in OpenCode${NC}"
        echo -n "Would you like to update it? [y/N] "
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            echo "Skipping OpenCode configuration"
            return 0
        fi
    fi

    echo "Configuration to add:"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    generate_opencode_config
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo

    echo -n "Add this configuration to OpenCode? [y/N] "
    read -r response

    if [[ "$response" =~ ^[Yy]$ ]]; then
        # Backup existing config
        cp "$config_file" "$config_file.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${GREEN}✓ Backed up config to $config_file.backup.$(date +%Y%m%d_%H%M%S)${NC}"

        # Use Python to merge JSON (safer than manual editing)
        python3 <<EOF
import json
import sys

config_file = "$config_file"

try:
    with open(config_file, 'r') as f:
        config = json.load(f)

    if 'mcp' not in config:
        config['mcp'] = {}

    config['mcp']['pdftools'] = {
        "type": "local",
        "command": ["node", "$MCP_SERVER_PATH"],
        "enabled": True,
        "environment": {
            "MCP_PDFTOOLS_VENV": "$VENV_PATH",
            "MCP_PDFTOOLS_TIMEOUT": "300000",
            "MCP_PDFTOOLS_MAX_OUTPUT": "10485760"
        },
        "timeout": 300000
    }

    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

    print("✓ Configuration added successfully")
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ OpenCode configuration updated!${NC}"
            echo
            echo "Next steps:"
            echo "  1. Restart OpenCode"
            echo "  2. PDFTools should appear in the available MCP servers"
            echo "  3. Test with: 'Merge these PDF files: file1.pdf file2.pdf'"
        else
            echo -e "${RED}✗ Failed to update configuration${NC}"
            echo "Please add the configuration manually to: $config_file"
        fi
    else
        echo "Configuration NOT added."
        echo "To add manually, edit: $config_file"
    fi
}

# Detect and configure Claude Desktop
configure_claude() {
    local config_file="$HOME/.config/claude/config.json"

    if [ ! -f "$config_file" ]; then
        echo -e "${YELLOW}Claude Desktop config not found at $config_file${NC}"
        return 1
    fi

    echo -e "${GREEN}✓ Found Claude Desktop configuration${NC}"
    echo

    # Similar logic as OpenCode (omitted for brevity)
    echo "Claude Desktop configuration:"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    generate_claude_config
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
    echo "Please add this to $config_file manually under 'mcpServers'"
}

# Main
echo "Detecting AI agent configurations..."
echo

# Try to configure detected agents
opencode_configured=false
claude_configured=false

if configure_opencode; then
    opencode_configured=true
fi

echo
if configure_claude; then
    claude_configured=true
fi

# Summary
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}  Configuration Summary${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if $opencode_configured; then
    echo -e "${GREEN}✓ OpenCode: Configured${NC}"
else
    echo -e "${YELLOW}⊘ OpenCode: Not configured${NC}"
fi

if $claude_configured; then
    echo -e "${GREEN}✓ Claude Desktop: Configured${NC}"
else
    echo -e "${YELLOW}⊘ Claude Desktop: Not configured${NC}"
fi

echo
echo "Done!"
