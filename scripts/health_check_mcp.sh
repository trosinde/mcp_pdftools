#!/usr/bin/env bash
#
# MCP Server Health Check Script
# Verifies MCP server installation and configuration
#
# Exit codes:
#   0 - All checks passed
#   1 - One or more checks failed

# Don't exit on error - we want to run all checks
set +e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
CHECKS_PASSED=0
CHECKS_FAILED=0

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((CHECKS_PASSED++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((CHECKS_FAILED++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  MCP Server Health Check"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Detect installation directory
if [ -d "mcp-server" ]; then
    # Running from repo root
    MCP_DIR="$(pwd)/mcp-server"
elif [ -d "../mcp-server" ]; then
    # Running from scripts/
    MCP_DIR="$(cd .. && pwd)/mcp-server"
elif [ -d "/home/$(whoami)/mcp_pdftools/mcp-server" ]; then
    # System installation
    MCP_DIR="/home/$(whoami)/mcp_pdftools/mcp-server"
else
    check_fail "MCP server directory not found"
    echo
    echo "Searched locations:"
    echo "  - $(pwd)/mcp-server"
    echo "  - $(pwd)/../mcp-server"
    echo "  - /home/$(whoami)/mcp_pdftools/mcp-server"
    exit 1
fi

check_pass "MCP server directory found: $MCP_DIR"

# Check 1: Directory structure
echo
echo "Checking directory structure..."
if [ -d "$MCP_DIR/src" ]; then
    check_pass "src/ directory exists"
else
    check_fail "src/ directory missing"
fi

if [ -d "$MCP_DIR/tests" ]; then
    check_pass "tests/ directory exists"
else
    check_fail "tests/ directory missing"
fi

if [ -f "$MCP_DIR/package.json" ]; then
    check_pass "package.json exists"
else
    check_fail "package.json missing"
fi

if [ -f "$MCP_DIR/tsconfig.json" ]; then
    check_pass "tsconfig.json exists"
else
    check_fail "tsconfig.json missing"
fi

# Check 2: Dependencies installed
echo
echo "Checking dependencies..."
if [ -d "$MCP_DIR/node_modules" ]; then
    check_pass "node_modules/ exists"

    if [ -d "$MCP_DIR/node_modules/@modelcontextprotocol" ]; then
        check_pass "MCP SDK installed"
    else
        check_fail "MCP SDK not installed"
    fi
else
    check_fail "node_modules/ missing - run 'npm install'"
fi

# Check 3: TypeScript compilation
echo
echo "Checking TypeScript compilation..."
if [ -d "$MCP_DIR/dist" ]; then
    check_pass "dist/ directory exists"

    if [ -f "$MCP_DIR/dist/index.js" ]; then
        check_pass "dist/index.js exists"
    else
        check_fail "dist/index.js missing - run 'npm run build'"
    fi

    if [ -f "$MCP_DIR/dist/server.js" ]; then
        check_pass "dist/server.js exists"
    else
        check_fail "dist/server.js missing"
    fi
else
    check_fail "dist/ directory missing - run 'npm run build'"
fi

# Check 4: All tool files present
echo
echo "Checking tool files..."
TOOLS=("merge" "split" "extract" "ocr" "protect" "thumbnails" "rename")
TOOLS_OK=0

for tool in "${TOOLS[@]}"; do
    if [ -f "$MCP_DIR/dist/tools/${tool}.js" ]; then
        ((TOOLS_OK++))
    else
        check_fail "Tool missing: $tool"
    fi
done

if [ $TOOLS_OK -eq 7 ]; then
    check_pass "All 7 tools present"
else
    check_fail "Only $TOOLS_OK/7 tools found"
fi

# Check 5: Utility files present
echo
echo "Checking utility files..."
UTILS=("validator" "security" "executor" "config")
UTILS_OK=0

for util in "${UTILS[@]}"; do
    if [ -f "$MCP_DIR/dist/utils/${util}.js" ]; then
        ((UTILS_OK++))
    else
        check_fail "Utility missing: $util"
    fi
done

if [ $UTILS_OK -eq 4 ]; then
    check_pass "All 4 utilities present"
else
    check_fail "Only $UTILS_OK/4 utilities found"
fi

# Check 6: Run tests
echo
echo "Running tests..."
cd "$MCP_DIR"

if npm test > /tmp/mcp_test_output.log 2>&1; then
    TEST_COUNT=$(grep -oP '\d+ passed' /tmp/mcp_test_output.log | grep -oP '^\d+')
    check_pass "All tests passed ($TEST_COUNT tests)"
else
    check_fail "Tests failed - see /tmp/mcp_test_output.log"
    cat /tmp/mcp_test_output.log
fi

# Check 7: Node.js version
echo
echo "Checking Node.js version..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')

    if [ "$NODE_MAJOR" -ge 18 ]; then
        check_pass "Node.js $NODE_VERSION (>= 18.0.0)"
    else
        check_fail "Node.js $NODE_VERSION (< 18.0.0 required)"
    fi
else
    check_fail "Node.js not found"
fi

# Check 8: Configuration detection
echo
echo "Detecting AI agent configurations..."
CONFIG_FOUND=0

if [ -f "$HOME/.config/opencode/opencode.json" ]; then
    check_pass "OpenCode config found"
    ((CONFIG_FOUND++))

    if grep -q "pdftools" "$HOME/.config/opencode/opencode.json"; then
        check_pass "PDFTools configured in OpenCode"
    else
        check_warn "PDFTools NOT configured in OpenCode"
        echo "  Add configuration with: scripts/generate_mcp_config.sh"
    fi
fi

if [ -f "$HOME/.config/claude/config.json" ]; then
    check_pass "Claude Desktop config found"
    ((CONFIG_FOUND++))

    if grep -q "pdftools" "$HOME/.config/claude/config.json"; then
        check_pass "PDFTools configured in Claude Desktop"
    else
        check_warn "PDFTools NOT configured in Claude Desktop"
    fi
fi

if [ $CONFIG_FOUND -eq 0 ]; then
    check_warn "No AI agent configurations found"
fi

# Summary
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Health Check Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}Passed:${NC} $CHECKS_PASSED"
echo -e "${RED}Failed:${NC} $CHECKS_FAILED"
echo

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo
    echo "MCP Server is ready to use."
    echo "To configure AI agents, run: scripts/generate_mcp_config.sh"
    exit 0
else
    echo -e "${RED}✗ $CHECKS_FAILED check(s) failed${NC}"
    echo
    echo "Please fix the issues above and run the health check again."
    exit 1
fi
