#!/usr/bin/env bash
# MCP PDFTools Uninstaller for Linux/macOS
# Version: 1.0
# Description: Clean removal of mcp_pdftools installation

set -e
set -o pipefail

# ============================================================================
# Global Variables
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$SCRIPT_DIR"
LOG_FILE="$HOME/.mcp_pdftools/logs/uninstall_$(date +%Y-%m-%d_%H-%M-%S).log"

# ============================================================================
# Logging
# ============================================================================

log_info() {
    local msg="[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

log_warn() {
    local msg="[WARN] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;33m$msg\033[0m" | tee -a "$LOG_FILE"
}

log_error() {
    local msg="[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;31m$msg\033[0m" | tee -a "$LOG_FILE"
}

log_success() {
    local msg="[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;32m$msg\033[0m" | tee -a "$LOG_FILE"
}

# ============================================================================
# Initialization
# ============================================================================

init_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    log_info "Uninstallation started"
}

show_header() {
    cat <<EOF

╔═══════════════════════════════════════════════════════════╗
║          MCP PDFTools - Uninstaller                       ║
║                   Version 1.0                             ║
╚═══════════════════════════════════════════════════════════╝

This script will remove:
  • Virtual environment: $INSTALL_DIR/venv
  • Installation directory: $INSTALL_DIR (optional)
  • Docker images (optional)
  • Log files (optional)

System dependencies (Python, Docker, Git, Node.js) will be preserved.

Log File: $LOG_FILE

EOF
}

# ============================================================================
# Confirmation
# ============================================================================

confirm() {
    local prompt="$1"
    local response

    while true; do
        read -p "$prompt [y/N]: " response
        case "$response" in
            [Yy]|[Yy][Ee][Ss])
                return 0
                ;;
            [Nn]|[Nn][Oo]|"")
                return 1
                ;;
            *)
                echo "Please answer yes or no."
                ;;
        esac
    done
}

# ============================================================================
# Uninstallation Functions
# ============================================================================

deactivate_venv() {
    log_info "Deactivating virtual environment if active..."

    if [ -n "$VIRTUAL_ENV" ]; then
        log_info "Virtual environment is active: $VIRTUAL_ENV"
        # Note: deactivate is a shell function, can't easily call from here
        log_warn "Please run 'deactivate' manually after uninstallation if needed"
    else
        log_info "No active virtual environment detected"
    fi
}

remove_venv() {
    log_info "Removing virtual environment..."

    if [ -d "$INSTALL_DIR/venv" ]; then
        rm -rf "$INSTALL_DIR/venv" || {
            log_error "Failed to remove virtual environment"
            return 1
        }
        log_success "✓ Virtual environment removed"
    else
        log_info "Virtual environment not found, skipping"
    fi

    return 0
}

remove_installation_dir() {
    if confirm "Remove entire installation directory ($INSTALL_DIR)?"; then
        log_info "Removing installation directory..."

        # Safety check: don't remove home directory or root
        if [ "$INSTALL_DIR" = "$HOME" ] || [ "$INSTALL_DIR" = "/" ]; then
            log_error "Safety check failed: refusing to remove $INSTALL_DIR"
            return 1
        fi

        # Safety check: ensure this looks like mcp_pdftools directory
        if [ ! -f "$INSTALL_DIR/setup.py" ] || [ ! -d "$INSTALL_DIR/src/pdftools" ]; then
            log_warn "Directory $INSTALL_DIR doesn't look like mcp_pdftools installation"
            if ! confirm "Are you sure you want to remove it?"; then
                log_info "Skipping directory removal"
                return 0
            fi
        fi

        rm -rf "$INSTALL_DIR" || {
            log_error "Failed to remove installation directory"
            return 1
        }

        log_success "✓ Installation directory removed"
        log_warn "Note: You are currently in a deleted directory"
        log_warn "Please navigate elsewhere: cd ~"
    else
        log_info "Skipping installation directory removal"
    fi

    return 0
}

remove_docker_images() {
    if confirm "Remove Docker images for mcp-pdftools?"; then
        log_info "Removing Docker images..."

        if command -v docker &> /dev/null; then
            local images=$(docker images --filter=reference="*mcp*pdf*" -q)
            if [ -n "$images" ]; then
                docker rmi $images 2>&1 | tee -a "$LOG_FILE" || {
                    log_warn "Failed to remove some Docker images"
                }
                log_success "✓ Docker images removed"
            else
                log_info "No matching Docker images found"
            fi
        else
            log_warn "Docker not found, skipping Docker image removal"
        fi
    else
        log_info "Skipping Docker image removal"
    fi

    return 0
}

remove_log_files() {
    if confirm "Remove log files ($HOME/.mcp_pdftools/logs)?"; then
        log_info "Removing log files..."

        # Close current log file first
        local current_log="$LOG_FILE"

        if [ -d "$HOME/.mcp_pdftools/logs" ]; then
            rm -rf "$HOME/.mcp_pdftools/logs" || {
                log_warn "Failed to remove log files"
                return 1
            }
            echo "✓ Log files removed"
        else
            log_info "Log directory not found"
        fi

        # Also remove parent directory if empty
        if [ -d "$HOME/.mcp_pdftools" ]; then
            rmdir "$HOME/.mcp_pdftools" 2>/dev/null || true
        fi
    else
        log_info "Skipping log file removal"
        log_info "Uninstallation log preserved at: $LOG_FILE"
    fi

    return 0
}

# ============================================================================
# Main Uninstallation Flow
# ============================================================================

main() {
    init_logging
    show_header

    # Final confirmation
    if ! confirm "Proceed with uninstallation?"; then
        log_info "Uninstallation cancelled by user"
        echo "Uninstallation cancelled."
        exit 0
    fi

    echo ""
    log_info "Starting uninstallation..."
    echo ""

    # Step 1: Remove shell configuration
    remove_shell_configuration || log_warn "Shell configuration removal completed with warnings"

    # Step 2: Deactivate venv
    deactivate_venv

    # Step 3: Remove virtual environment
    remove_venv || log_error "Failed to remove venv, continuing..."

    # Step 3: Remove installation directory (optional)
    # Note: This will delete the script itself!
    if [ "$INSTALL_DIR" != "$SCRIPT_DIR" ]; then
        remove_installation_dir || log_error "Failed to remove installation dir, continuing..."
    else
        echo ""
        log_warn "Skipping installation directory removal (would delete this script)"
        echo ""
    fi

    # Step 4: Remove Docker images (optional)
    remove_docker_images || log_error "Failed to remove Docker images, continuing..."

    # Step 5: Remove log files (optional)
    remove_log_files || log_warn "Failed to remove log files"

    # Summary
    echo ""
    cat <<EOF
╔═══════════════════════════════════════════════════════════╗
║              Uninstallation Completed                     ║
╚═══════════════════════════════════════════════════════════╝

What was removed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Virtual environment
✓ Installation directory (if selected)
✓ Docker images (if selected)
✓ Log files (if selected)

What was preserved:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ System Python
✓ System Docker
✓ System Git
✓ System Node.js

If you want to reinstall mcp_pdftools in the future, simply run:
  $ git clone <repo-url>
  $ cd mcp_pdftools
  $ ./install.sh

Thank you for using MCP PDFTools!

EOF

    log_success "Uninstallation completed successfully"
    exit 0
}

# Run main function
main "$@"
