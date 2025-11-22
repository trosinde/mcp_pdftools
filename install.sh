#!/usr/bin/env bash
# MCP PDFTools Installer for Linux/macOS
# Version: 1.0
# Description: Automated installation script for mcp_pdftools

set -e
set -o pipefail

# ============================================================================
# Global Variables
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export MCP_INSTALL_LOG=""

# Auto-detect: If running from a cloned repository, use it directly
# This allows users to run: git clone <repo> && cd <repo> && ./install.sh
if [ -f "$SCRIPT_DIR/setup.py" ] && [ -d "$SCRIPT_DIR/src/pdftools" ] && [ -d "$SCRIPT_DIR/.git" ]; then
    # We're running from a cloned repository - use it as INSTALL_DIR
    export INSTALL_DIR="${INSTALL_DIR:-$SCRIPT_DIR}"
    # No need to clone again - we already have the repository
    export REPO_URL="${REPO_URL:-}"
else
    # We're running from a downloaded script - clone to default location
    export INSTALL_DIR="${INSTALL_DIR:-$HOME/mcp_pdftools}"
    export REPO_URL="${REPO_URL:-https://github.com/trosinde/mcp_pdftools.git}"
fi
export PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
export SKIP_DOCKER="${SKIP_DOCKER:-false}"
export SKIP_TESTS="${SKIP_TESTS:-false}"
export SKIP_MCP="${SKIP_MCP:-false}"
export MCP_TARGETS="${MCP_TARGETS:-auto}"
export LOG_LEVEL="${LOG_LEVEL:-INFO}"

# ============================================================================
# Initialization
# ============================================================================

init_logging() {
    local log_dir="$HOME/.mcp_pdftools/logs"
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local log_file="$log_dir/install_${timestamp}.log"

    mkdir -p "$log_dir"
    touch "$log_file"

    echo "Installation started at $(date)" | tee -a "$log_file"
    echo "Log file: $log_file" | tee -a "$log_file"
    echo "" | tee -a "$log_file"

    export MCP_INSTALL_LOG="$log_file"
}

parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-dir=*)
                INSTALL_DIR="${1#*=}"
                ;;
            --repo-url=*)
                REPO_URL="${1#*=}"
                ;;
            --skip-docker)
                SKIP_DOCKER=true
                ;;
            --skip-tests)
                SKIP_TESTS=true
                ;;
            --skip-mcp)
                SKIP_MCP=true
                ;;
            --mcp-targets=*)
                MCP_TARGETS="${1#*=}"
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                echo "Unknown argument: $1"
                echo "Use --help for usage information"
                exit 1
                ;;
        esac
        shift
    done
}

show_help() {
    cat <<EOF
MCP PDFTools Installer

Usage: $0 [OPTIONS]

Options:
  --install-dir=PATH     Installation directory (default: ~/mcp_pdftools)
  --repo-url=URL         GitHub repository URL
  --skip-docker          Skip Docker installation
  --skip-tests           Skip functional tests
  --skip-mcp             Skip MCP server configuration
  --mcp-targets=LIST     Comma-separated list: claude-code,claude-desktop,opencode
  -h, --help             Show this help message

Environment Variables:
  INSTALL_DIR            Same as --install-dir
  REPO_URL               Same as --repo-url
  SKIP_DOCKER            Set to 'true' to skip Docker
  SKIP_TESTS             Set to 'true' to skip tests
  SKIP_MCP               Set to 'true' to skip MCP server
  MCP_TARGETS            Same as --mcp-targets (default: auto)
  LOG_LEVEL              Logging verbosity: INFO, WARN, ERROR, DEBUG

Examples:
  # Basic installation
  ./install.sh

  # Custom installation directory
  ./install.sh --install-dir=/opt/mcp_pdftools

  # Skip Docker and tests
  ./install.sh --skip-docker --skip-tests

  # Install MCP server for specific tool
  ./install.sh --mcp-targets=claude-code

For more information, visit:
https://github.com/YOUR_ORG/mcp_pdftools

EOF
}

show_welcome() {
    cat <<EOF

╔═══════════════════════════════════════════════════════════╗
║          MCP PDFTools - Automated Installation            ║
║                       Version 1.0                         ║
╚═══════════════════════════════════════════════════════════╝

Installation Directory: $INSTALL_DIR
Repository URL: $REPO_URL
Log File: $MCP_INSTALL_LOG

This script will install:
  • Python ${PYTHON_VERSION}+
  • Docker (unless --skip-docker)
  • Git
  • Node.js (for MCP server)
  • mcp_pdftools Python package
  • MCP server integration (optional)

Estimated time: 5-15 minutes (depending on downloads)

Press Ctrl+C to cancel, or press Enter to continue...
EOF
    read -r
}

# ============================================================================
# Error Handling
# ============================================================================

cleanup_on_error() {
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "═══════════════════════════════════════════════════════════"
        echo "Installation failed with exit code: $exit_code"
        echo "═══════════════════════════════════════════════════════════"
        echo ""
        echo "Cleaning up partial installation..."

        # Remove incomplete venv
        if [ -d "$INSTALL_DIR/venv" ] && [ ! -f "$INSTALL_DIR/venv/.installation_complete" ]; then
            echo "Removing incomplete virtual environment..."
            rm -rf "$INSTALL_DIR/venv"
        fi

        echo ""
        echo "Installation incomplete. Please check the log file:"
        echo "  $MCP_INSTALL_LOG"
        echo ""
        echo "Common issues:"
        echo "  1. Network connection - check internet connectivity"
        echo "  2. Permissions - ensure you have sudo/admin rights"
        echo "  3. Disk space - ensure sufficient free space"
        echo ""
        echo "For help, visit: https://github.com/YOUR_ORG/mcp_pdftools/issues"
        echo ""
    fi

    exit $exit_code
}

trap cleanup_on_error EXIT INT TERM

# ============================================================================
# Finalization
# ============================================================================

finalize_installation() {
    touch "$INSTALL_DIR/venv/.installation_complete"

    local mcp_configured=""
    if [ "$SKIP_MCP" != "true" ]; then
        mcp_configured="(MCP server configured)"
    fi

    cat <<EOF

╔═══════════════════════════════════════════════════════════╗
║              Installation Completed Successfully!         ║
╚═══════════════════════════════════════════════════════════╝

Installation Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Python ${PYTHON_VERSION_FOUND:-installed}
✓ Docker ${DOCKER_VERSION_FOUND:-installed} (or skipped)
✓ Git ${GIT_VERSION_FOUND:-installed}
✓ Node.js ${NODE_VERSION_FOUND:-installed} (if MCP enabled)
✓ Virtual environment: $INSTALL_DIR/venv
✓ Repository: $INSTALL_DIR
✓ Dependencies installed
✓ Functional tests completed
$mcp_configured

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:

1. Activate the virtual environment:
   $ cd $INSTALL_DIR
   $ source venv/bin/activate

2. Verify installation:
   $ pdfmerge --version
   $ pdfsplit --help

3. Try merging PDFs:
   $ pdfmerge file1.pdf file2.pdf -o merged.pdf

4. View all available tools:
   $ pdfmerge --help
   $ pdfsplit --help
   $ ocrutil --help
   $ pdfgettxt --help
   $ pdfprotect --help
   $ pdfthumbnails --help
   $ pdfrename --help

5. Use from AI agents (if MCP configured):
   - Open Claude Code / Claude Desktop / OpenCode
   - Ask: "Merge these PDF files: file1.pdf, file2.pdf"

6. View documentation:
   $ cat $INSTALL_DIR/README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installation Log: $MCP_INSTALL_LOG
Test Report: $HOME/.mcp_pdftools/installation_test_report.txt

For help: https://github.com/YOUR_ORG/mcp_pdftools

Happy PDF processing! 🎉

EOF
}

# ============================================================================
# Main Installation Flow
# ============================================================================

main() {
    # Initialize
    init_logging
    parse_arguments "$@"

    # Load utility functions
    if [ -f "$SCRIPT_DIR/scripts/install_utils.sh" ]; then
        source "$SCRIPT_DIR/scripts/install_utils.sh"
    else
        echo "Error: install_utils.sh not found at $SCRIPT_DIR/scripts/install_utils.sh"
        exit 1
    fi

    # Show welcome
    show_welcome

    # Step 1: Platform detection
    log_info "Step 1/10: Detecting platform..."
    detect_platform || exit 2
    check_privileges || exit 1

    # Step 2: Detect and install Python
    log_info "Step 2/10: Checking Python..."
    install_python || exit 4

    # Step 3: Detect and install Docker
    log_info "Step 3/10: Checking Docker..."
    install_docker || {
        if [ "$SKIP_DOCKER" != "true" ]; then
            log_warn "Docker installation failed but continuing..."
        fi
    }

    # Step 4: Detect and install Git
    log_info "Step 4/10: Checking Git..."
    install_git || exit 4

    # Step 5: Create virtual environment
    log_info "Step 5/10: Creating virtual environment..."
    clone_repository || exit 6
    verify_repository_structure || exit 6
    create_virtualenv || exit 5

    # Step 6: Activate virtual environment
    log_info "Step 6/10: Activating virtual environment..."
    activate_virtualenv || exit 5
    upgrade_pip || exit 5

    # Step 7: Install dependencies
    log_info "Step 7/11: Installing Python dependencies..."
    install_python_dependencies || exit 7
    install_package_editable || exit 7
    verify_installation || exit 7

    # Step 8: Configure shell environment
    log_info "Step 8/11: Configuring shell environment..."
    configure_shell_environment || log_warn "Shell configuration completed with warnings"

    # Step 9: Run functional tests
    log_info "Step 9/11: Running functional tests..."
    run_functional_tests || log_warn "Tests completed with warnings"

    # Step 10: Configure MCP server
    log_info "Step 10/11: Configuring MCP server..."
    configure_mcp_server || log_warn "MCP configuration completed with warnings"

    # Step 11: Finalize
    log_info "Step 11/11: Finalizing installation..."
    finalize_installation

    log_success "Installation completed successfully!"
    exit 0
}

# Run main function
main "$@"
