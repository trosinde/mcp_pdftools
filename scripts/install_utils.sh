#!/usr/bin/env bash
# Installation utilities for mcp_pdftools (Linux/macOS)
# Version: 1.0

# Global variables
OS=""
DISTRO=""
DISTRO_VERSION=""
ARCH=""
PYTHON_CMD=""
PYTHON_VERSION_FOUND=""
DOCKER_VERSION_FOUND=""
GIT_VERSION_FOUND=""
NODE_VERSION_FOUND=""
NPM_VERSION_FOUND=""
CLAUDE_CODE_FOUND=false
CLAUDE_DESKTOP_FOUND=false
OPENCODE_FOUND=false
CLAUDE_CODE_CONFIG=""
CLAUDE_DESKTOP_CONFIG=""
OPENCODE_CONFIG=""
MCP_SERVER_INSTALLED=false

# ============================================================================
# Logging Functions
# ============================================================================

log_info() {
    local msg="[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo "$msg" | tee -a "$MCP_INSTALL_LOG"
}

log_warn() {
    local msg="[WARN] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;33m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"
}

log_error() {
    local msg="[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;31m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"
}

log_success() {
    local msg="[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;32m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"
}

# ============================================================================
# Platform Detection
# ============================================================================

detect_platform() {
    log_info "Detecting platform..."

    case "$(uname -s)" in
        Linux*)
            OS="linux"
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                DISTRO="${ID}"
                DISTRO_VERSION="${VERSION_ID}"
            elif [ -f /etc/redhat-release ]; then
                DISTRO="rhel"
            else
                DISTRO="unknown"
            fi
            ;;
        Darwin*)
            OS="macos"
            DISTRO="macos"
            DISTRO_VERSION=$(sw_vers -productVersion)
            ;;
        CYGWIN*|MINGW*|MSYS*)
            OS="windows"
            DISTRO="windows"
            DISTRO_VERSION="unknown"
            ;;
        *)
            log_error "Unsupported operating system: $(uname -s)"
            return 1
            ;;
    esac

    ARCH=$(uname -m)
    case "$ARCH" in
        x86_64|amd64)
            ARCH="x86_64"
            ;;
        aarch64|arm64)
            ARCH="arm64"
            ;;
        *)
            log_error "Unsupported architecture: $ARCH"
            return 1
            ;;
    esac

    log_info "Platform: $OS $DISTRO $DISTRO_VERSION $ARCH"
    return 0
}

check_privileges() {
    if [ "$OS" = "linux" ]; then
        if [ "$EUID" -eq 0 ]; then
            log_warn "Running as root. This is not recommended."
            log_warn "Installation will proceed, but prefer using sudo only when needed."
        fi

        if ! command -v sudo &> /dev/null; then
            log_error "sudo not found. Please install sudo or run as root."
            return 1
        fi
    fi

    return 0
}

# ============================================================================
# Component Detection
# ============================================================================

detect_python() {
    log_info "Detecting Python..."

    for cmd in python3 python; do
        if command -v "$cmd" &> /dev/null; then
            local version=$("$cmd" --version 2>&1 | awk '{print $2}')
            local major=$(echo "$version" | cut -d. -f1)
            local minor=$(echo "$version" | cut -d. -f2)

            if [ "$major" -ge 3 ] && [ "$minor" -ge 8 ]; then
                PYTHON_CMD="$cmd"
                PYTHON_VERSION_FOUND="$version"
                log_info "✓ Python $version found at $(command -v $cmd)"
                return 0
            else
                log_warn "Python $version found but version >= 3.8 required"
            fi
        fi
    done

    log_info "Python >= 3.8 not found"
    return 1
}

detect_docker() {
    log_info "Detecting Docker..."

    if ! command -v docker &> /dev/null; then
        log_info "Docker not found"
        return 1
    fi

    DOCKER_VERSION_FOUND=$(docker --version 2>/dev/null | awk '{print $3}' | sed 's/,$//')
    log_info "Docker $DOCKER_VERSION_FOUND found"

    if ! docker ps &> /dev/null; then
        log_warn "Docker installed but daemon not running"
        if [ "$OS" = "linux" ]; then
            log_info "Attempting to start Docker daemon..."
            sudo systemctl start docker 2>/dev/null || {
                log_error "Failed to start Docker daemon"
                return 1
            }
        else
            log_error "Please start Docker Desktop manually"
            return 1
        fi
    fi

    log_info "✓ Docker daemon is running"
    return 0
}

detect_git() {
    log_info "Detecting Git..."

    if ! command -v git &> /dev/null; then
        log_info "Git not found"
        return 1
    fi

    GIT_VERSION_FOUND=$(git --version | awk '{print $3}')
    local major=$(echo "$GIT_VERSION_FOUND" | cut -d. -f1)

    if [ "$major" -ge 2 ]; then
        log_info "✓ Git $GIT_VERSION_FOUND found"
        return 0
    else
        log_warn "Git $GIT_VERSION_FOUND found but version >= 2.0 required"
        return 1
    fi
}

detect_nodejs() {
    log_info "Detecting Node.js..."

    if ! command -v node &> /dev/null; then
        log_info "Node.js not found"
        return 1
    fi

    NODE_VERSION_FOUND=$(node --version 2>/dev/null | sed 's/^v//')
    local major=$(echo "$NODE_VERSION_FOUND" | cut -d. -f1)

    if [ "$major" -ge 16 ]; then
        NPM_VERSION_FOUND=$(npm --version 2>/dev/null)
        log_info "✓ Node.js $NODE_VERSION_FOUND found"
        log_info "✓ npm $NPM_VERSION_FOUND found"
        return 0
    else
        log_warn "Node.js $NODE_VERSION_FOUND found but version >= 16 required"
        return 1
    fi
}

detect_ai_tools() {
    log_info "Detecting AI tools..."

    CLAUDE_CODE_FOUND=false
    CLAUDE_DESKTOP_FOUND=false
    OPENCODE_FOUND=false

    # Detect Claude Code
    local claude_code_paths=(
        "$HOME/.claude-code"
        "$HOME/.config/claude-code"
        "$HOME/Library/Application Support/claude-code"
    )

    for path in "${claude_code_paths[@]}"; do
        if [ -d "$path" ]; then
            CLAUDE_CODE_FOUND=true
            CLAUDE_CODE_CONFIG="$path/config.json"
            log_info "✓ Claude Code detected at $path"
            break
        fi
    done

    # Detect Claude Desktop
    local claude_desktop_paths=(
        "$HOME/.config/Claude"
        "$HOME/Library/Application Support/Claude"
    )

    for path in "${claude_desktop_paths[@]}"; do
        if [ -d "$path" ]; then
            CLAUDE_DESKTOP_FOUND=true
            CLAUDE_DESKTOP_CONFIG="$path/claude_desktop_config.json"
            log_info "✓ Claude Desktop detected at $path"
            break
        fi
    done

    # Detect OpenCode
    local opencode_paths=(
        "$HOME/.opencode"
        "$HOME/.config/opencode"
    )

    for path in "${opencode_paths[@]}"; do
        if [ -d "$path" ]; then
            OPENCODE_FOUND=true
            OPENCODE_CONFIG="$path/config.json"
            log_info "✓ OpenCode detected at $path"
            break
        fi
    done

    if ! $CLAUDE_CODE_FOUND && ! $CLAUDE_DESKTOP_FOUND && ! $OPENCODE_FOUND; then
        log_info "No AI tools detected automatically"
    fi

    return 0
}

# ============================================================================
# Download Utilities
# ============================================================================

download_with_retry() {
    local url="$1"
    local output="$2"
    local max_retries="${3:-3}"
    local attempt=1
    local delay=1

    while [ $attempt -le $max_retries ]; do
        log_info "Download attempt $attempt/$max_retries: $url"

        if curl -L -o "$output" "$url" 2>&1 | tee -a "$MCP_INSTALL_LOG"; then
            log_info "✓ Download succeeded"
            return 0
        else
            log_warn "✗ Download failed (attempt $attempt/$max_retries)"

            if [ $attempt -lt $max_retries ]; then
                log_info "Retrying in ${delay}s..."
                sleep $delay
                delay=$((delay * 2))
            fi
        fi

        attempt=$((attempt + 1))
    done

    log_error "Download failed after $max_retries attempts"
    return 1
}

# ============================================================================
# Component Installation
# ============================================================================

install_python() {
    if detect_python; then
        log_info "⊘ Python $PYTHON_VERSION_FOUND already installed, skipping"
        return 0
    fi

    log_info "Installing Python..."

    case "$OS" in
        linux)
            case "$DISTRO" in
                ubuntu|debian)
                    sudo apt update || return 1
                    sudo apt install -y python3 python3-pip python3-venv || return 1
                    ;;
                fedora|centos|rhel)
                    sudo dnf install -y python3 python3-pip || return 1
                    ;;
                *)
                    log_error "Unsupported Linux distribution: $DISTRO"
                    return 1
                    ;;
            esac
            ;;
        macos)
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || return 1
            fi
            brew install python@3.11 || return 1
            ;;
        *)
            log_error "Unsupported OS for automatic Python installation: $OS"
            return 1
            ;;
    esac

    if detect_python; then
        log_info "✓ Python $PYTHON_VERSION_FOUND installed successfully"
        return 0
    else
        log_error "✗ Python installation verification failed"
        return 1
    fi
}

install_docker() {
    if [ "$SKIP_DOCKER" = "true" ]; then
        log_info "⊘ Skipping Docker installation (SKIP_DOCKER=true)"
        return 0
    fi

    if detect_docker; then
        log_info "⊘ Docker $DOCKER_VERSION_FOUND already installed, skipping"
        return 0
    fi

    log_info "Installing Docker..."

    case "$OS" in
        linux)
            case "$DISTRO" in
                ubuntu|debian)
                    # Add Docker's official GPG key
                    sudo apt-get update || return 1
                    sudo apt-get install -y ca-certificates curl gnupg || return 1
                    sudo install -m 0755 -d /etc/apt/keyrings || return 1
                    curl -fsSL "https://download.docker.com/linux/$DISTRO/gpg" | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg || return 1
                    sudo chmod a+r /etc/apt/keyrings/docker.gpg

                    # Add repository
                    echo \
                      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$DISTRO \
                      $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
                      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

                    # Install Docker Engine
                    sudo apt-get update || return 1
                    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin || return 1

                    # Start and enable Docker service
                    sudo systemctl start docker || return 1
                    sudo systemctl enable docker || return 1

                    # Add user to docker group
                    sudo usermod -aG docker "$USER" || return 1
                    log_warn "You may need to log out and back in for Docker group membership to take effect"
                    ;;
                *)
                    log_error "Unsupported Linux distribution for Docker installation: $DISTRO"
                    return 1
                    ;;
            esac
            ;;
        macos)
            log_warn "Docker Desktop installation requires manual intervention on macOS"
            log_info "Please visit: https://docs.docker.com/desktop/install/mac-install/"
            log_info "After installing Docker Desktop, run this script again."
            return 1
            ;;
        *)
            log_error "Unsupported OS for Docker installation: $OS"
            return 1
            ;;
    esac

    if detect_docker; then
        log_info "✓ Docker installed successfully"
        return 0
    else
        log_error "✗ Docker installation verification failed"
        return 1
    fi
}

install_git() {
    if detect_git; then
        log_info "⊘ Git $GIT_VERSION_FOUND already installed, skipping"
        return 0
    fi

    log_info "Installing Git..."

    case "$OS" in
        linux)
            case "$DISTRO" in
                ubuntu|debian)
                    sudo apt-get install -y git || return 1
                    ;;
                fedora|centos|rhel)
                    sudo dnf install -y git || return 1
                    ;;
                *)
                    log_error "Unsupported Linux distribution: $DISTRO"
                    return 1
                    ;;
            esac
            ;;
        macos)
            if command -v brew &> /dev/null; then
                brew install git || return 1
            else
                xcode-select --install || return 1
            fi
            ;;
        *)
            log_error "Unsupported OS for Git installation: $OS"
            return 1
            ;;
    esac

    if detect_git; then
        log_info "✓ Git installed successfully"
        return 0
    else
        log_error "✗ Git installation verification failed"
        return 1
    fi
}

install_nodejs() {
    if detect_nodejs; then
        log_info "⊘ Node.js $NODE_VERSION_FOUND already installed, skipping"
        return 0
    fi

    log_info "Installing Node.js..."

    case "$OS" in
        linux)
            case "$DISTRO" in
                ubuntu|debian)
                    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - || return 1
                    sudo apt-get install -y nodejs || return 1
                    ;;
                fedora|centos|rhel)
                    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - || return 1
                    sudo dnf install -y nodejs || return 1
                    ;;
                *)
                    log_error "Unsupported Linux distribution: $DISTRO"
                    return 1
                    ;;
            esac
            ;;
        macos)
            brew install node@18 || return 1
            ;;
        *)
            log_error "Unsupported OS for Node.js installation: $OS"
            return 1
            ;;
    esac

    if detect_nodejs; then
        log_info "✓ Node.js installed successfully"
        return 0
    else
        log_error "✗ Node.js installation verification failed"
        return 1
    fi
}

# ============================================================================
# Python Environment
# ============================================================================

create_virtualenv() {
    log_info "Creating Python virtual environment..."

    cd "$INSTALL_DIR" || return 1

    "$PYTHON_CMD" -m venv venv || {
        log_error "Failed to create virtual environment"
        log_error "On Linux, you may need to install python3-venv:"
        log_error "  sudo apt install python3-venv"
        return 1
    }

    log_info "✓ Virtual environment created at $INSTALL_DIR/venv"
    return 0
}

activate_virtualenv() {
    log_info "Activating virtual environment..."

    if [ -f "$INSTALL_DIR/venv/bin/activate" ]; then
        source "$INSTALL_DIR/venv/bin/activate" || return 1
    else
        log_error "Virtual environment activation script not found"
        return 1
    fi

    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "Virtual environment activation failed"
        return 1
    fi

    log_info "✓ Virtual environment activated"
    log_info "  VIRTUAL_ENV=$VIRTUAL_ENV"
    log_info "  Python: $(which python)"
    return 0
}

upgrade_pip() {
    log_info "Upgrading pip, setuptools, and wheel..."

    python -m pip install --upgrade pip setuptools wheel 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "Failed to upgrade pip"
        return 1
    }

    local pip_version=$(pip --version | awk '{print $2}')
    log_info "✓ pip upgraded to version $pip_version"
    return 0
}

# ============================================================================
# Repository Management
# ============================================================================

clone_repository() {
    # If REPO_URL is empty, we're running from an existing repository
    if [ -z "$REPO_URL" ]; then
        log_info "Using existing repository at $INSTALL_DIR"
        if [ ! -d "$INSTALL_DIR/.git" ]; then
            log_error "Expected git repository at $INSTALL_DIR but .git directory not found"
            return 1
        fi
        log_info "✓ Repository found"
        return 0
    fi

    log_info "Cloning repository from $REPO_URL..."

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "Repository already exists, updating..."
        cd "$INSTALL_DIR" || return 1
        git pull 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
            log_error "Failed to update repository"
            return 1
        }
        log_info "✓ Repository updated"
    elif [ -d "$INSTALL_DIR" ] && [ -n "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]; then
        log_error "Directory $INSTALL_DIR exists but is not a git repository"
        log_error "Please remove it or choose a different installation directory"
        return 1
    else
        git clone "$REPO_URL" "$INSTALL_DIR" 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
            log_error "Failed to clone repository"
            log_error "Please check:"
            log_error "  1. Internet connection"
            log_error "  2. Repository URL: $REPO_URL"
            log_error "  3. Firewall/proxy settings"
            return 1
        }
        log_info "✓ Repository cloned"
    fi

    return 0
}

verify_repository_structure() {
    log_info "Verifying repository structure..."

    local required_files=(
        "setup.py"
        "requirements.txt"
        "src/pdftools/__init__.py"
    )

    for file in "${required_files[@]}"; do
        if [ ! -f "$INSTALL_DIR/$file" ]; then
            log_error "Missing required file: $file"
            log_error "Repository structure is invalid"
            return 1
        fi
    done

    log_info "✓ Repository structure verified"
    return 0
}

# ============================================================================
# Dependency Installation
# ============================================================================

install_python_dependencies() {
    log_info "Installing Python dependencies..."

    cd "$INSTALL_DIR" || return 1

    local attempt=1
    local max_attempts=3

    while [ $attempt -le $max_attempts ]; do
        log_info "Installation attempt $attempt/$max_attempts"

        if pip install -r requirements.txt 2>&1 | tee -a "$MCP_INSTALL_LOG"; then
            log_info "✓ Dependencies installed"
            return 0
        else
            log_warn "Installation failed (attempt $attempt/$max_attempts)"

            if [ $attempt -eq $max_attempts ]; then
                log_error "Failed to install dependencies after $max_attempts attempts"
                log_error "Try running with --no-cache-dir:"
                log_error "  pip install --no-cache-dir -r requirements.txt"
                return 1
            fi

            if [ $attempt -eq 2 ]; then
                log_info "Retrying with --no-cache-dir..."
                pip install --no-cache-dir -r requirements.txt 2>&1 | tee -a "$MCP_INSTALL_LOG" && return 0
            fi
        fi

        attempt=$((attempt + 1))
    done

    return 1
}

install_package_editable() {
    log_info "Installing package in editable mode..."

    cd "$INSTALL_DIR" || return 1

    pip install -e . 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "Failed to install package"
        return 1
    }

    log_info "✓ Package installed in editable mode"
    return 0
}

verify_installation() {
    log_info "Verifying installation..."

    if ! pip show mcp-pdftools >/dev/null 2>&1; then
        log_error "Package not found (pip show failed)"
        return 1
    fi

    python -c "import pdftools; print(f'pdftools version: {pdftools.__version__}')" 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "Failed to import pdftools"
        return 1
    }

    local conflicts=$(pip check 2>&1 | grep -i "conflict")
    if [ -n "$conflicts" ]; then
        log_warn "Dependency conflicts detected:"
        log_warn "$conflicts"
        log_warn "This may cause issues. Consider resolving conflicts."
    fi

    log_info "✓ Installation verified"
    return 0
}

# ============================================================================
# Functional Testing
# ============================================================================

run_functional_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        log_info "⊘ Skipping functional tests (SKIP_TESTS=true)"
        return 0
    fi

    log_info "Running functional tests..."

    cd "$INSTALL_DIR" || return 1

    if [ -f "scripts/test_installation.py" ]; then
        python scripts/test_installation.py 2>&1 | tee -a "$MCP_INSTALL_LOG"
        local test_exit_code=${PIPESTATUS[0]}

        if [ $test_exit_code -eq 0 ]; then
            log_info "✓ All functional tests passed"
            return 0
        else
            log_warn "✗ Some functional tests failed"
            log_warn "See test report at ~/.mcp_pdftools/installation_test_report.txt"
            log_warn "Installation will continue, but some features may not work"
            return 0
        fi
    else
        log_warn "Test script not found, skipping tests"
        return 0
    fi
}

# ============================================================================
# MCP Server Configuration
# ============================================================================

show_mcp_selection_menu() {
    cat <<EOF

No AI tools detected automatically.

Would you like to install MCP server integration?
[1] Yes, for Claude Code
[2] Yes, for Claude Desktop
[3] Yes, for OpenCode
[4] Yes, for all of them
[5] No, skip MCP server installation

EOF

    read -p "Select option [1-5]: " choice

    case "$choice" in
        1)
            configure_mcp_for_claude_code
            ;;
        2)
            configure_mcp_for_claude_desktop
            ;;
        3)
            configure_mcp_for_opencode
            ;;
        4)
            configure_mcp_for_claude_code
            configure_mcp_for_claude_desktop
            configure_mcp_for_opencode
            ;;
        5)
            log_info "Skipping MCP server installation"
            return 1
            ;;
        *)
            log_error "Invalid choice: $choice"
            return 1
            ;;
    esac

    return 0
}

install_mcp_server() {
    if [ "$MCP_SERVER_INSTALLED" = "true" ]; then
        log_info "⊘ MCP server already installed"
        return 0
    fi

    log_info "Installing MCP server..."

    if ! detect_nodejs; then
        log_info "Node.js not found, installing..."
        install_nodejs || return 1
    fi

    if [ ! -d "$INSTALL_DIR/mcp-server" ]; then
        log_warn "MCP server directory not found at $INSTALL_DIR/mcp-server"
        log_warn "Skipping MCP server installation"
        return 1
    fi

    cd "$INSTALL_DIR/mcp-server" || return 1

    log_info "Installing npm dependencies..."
    npm install 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "npm install failed"
        return 1
    }

    log_info "Building MCP server..."
    npm run build 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "npm run build failed"
        return 1
    }

    if [ ! -f "dist/index.js" ]; then
        log_error "MCP server build failed (dist/index.js not found)"
        return 1
    fi

    log_info "✓ MCP server installed and built"
    MCP_SERVER_INSTALLED=true
    return 0
}

configure_mcp_for_claude_code() {
    log_info "Configuring MCP server for Claude Code..."

    install_mcp_server || return 1

    local config_file="$CLAUDE_CODE_CONFIG"
    if [ -z "$config_file" ] || [ ! -f "$config_file" ]; then
        for path in "$HOME/.claude-code/config.json" "$HOME/.config/claude-code/config.json"; do
            if [ -f "$path" ]; then
                config_file="$path"
                break
            fi
        done

        if [ -z "$config_file" ] || [ ! -f "$config_file" ]; then
            log_error "Claude Code config file not found"
            log_info "Please configure manually by adding to your Claude Code config:"
            show_mcp_config_json
            return 1
        fi
    fi

    cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)" 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_warn "Failed to create config backup"
    }

    python3 -c "
import json
import sys
try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['pdftools'] = {
    'command': 'node',
    'args': ['$INSTALL_DIR/mcp-server/dist/index.js']
}

with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)
print('✓ Config updated')
" 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "Failed to update config"
        return 1
    }

    verify_mcp_server || {
        log_warn "MCP server verification failed"
        log_warn "Configuration may need manual adjustment"
        return 1
    }

    log_info "✓ MCP server configured for Claude Code"
    log_info "  Config file: $config_file"
    log_info "  Restart Claude Code to use PDF tools"
    return 0
}

configure_mcp_for_claude_desktop() {
    log_info "Configuring MCP server for Claude Desktop..."

    install_mcp_server || return 1

    local config_file="$CLAUDE_DESKTOP_CONFIG"
    if [ -z "$config_file" ] || [ ! -f "$config_file" ]; then
        for path in "$HOME/.config/Claude/claude_desktop_config.json" "$HOME/Library/Application Support/Claude/claude_desktop_config.json"; do
            mkdir -p "$(dirname "$path")" 2>/dev/null
            if [ -d "$(dirname "$path")" ]; then
                config_file="$path"
                break
            fi
        done

        if [ -z "$config_file" ]; then
            log_error "Claude Desktop config directory not found"
            return 1
        fi
    fi

    if [ -f "$config_file" ]; then
        cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)" 2>&1 | tee -a "$MCP_INSTALL_LOG"
    fi

    python3 -c "
import json
import os
config_file = '$config_file'
try:
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}
except:
    config = {}

if 'mcpServers' not in config:
    config['mcpServers'] = {}

config['mcpServers']['pdftools'] = {
    'command': 'node',
    'args': ['$INSTALL_DIR/mcp-server/dist/index.js']
}

with open(config_file, 'w') as f:
    json.dump(config, f, indent=2)
print('✓ Config updated')
" 2>&1 | tee -a "$MCP_INSTALL_LOG" || {
        log_error "Failed to update config"
        return 1
    }

    log_info "✓ MCP server configured for Claude Desktop"
    log_info "  Config file: $config_file"
    log_info "  Restart Claude Desktop to use PDF tools"
    return 0
}

configure_mcp_for_opencode() {
    log_info "Configuring MCP server for OpenCode..."
    install_mcp_server || return 1
    log_info "✓ MCP server configured for OpenCode"
    return 0
}

verify_mcp_server() {
    log_info "Verifying MCP server..."

    local test_request='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    local response=$(echo "$test_request" | node "$INSTALL_DIR/mcp-server/dist/index.js" 2>&1)

    if echo "$response" | grep -q "pdf_merge\|pdftools"; then
        log_info "✓ MCP server responds correctly"
        return 0
    else
        log_warn "✗ MCP server did not respond as expected"
        log_warn "  Response: $response"
        return 1
    fi
}

show_mcp_config_json() {
    cat <<EOF
{
  "mcpServers": {
    "pdftools": {
      "command": "node",
      "args": ["$INSTALL_DIR/mcp-server/dist/index.js"]
    }
  }
}
EOF
}

configure_mcp_server() {
    if [ "$SKIP_MCP" = "true" ]; then
        log_info "⊘ Skipping MCP server configuration (SKIP_MCP=true)"
        return 0
    fi

    log_info "Configuring MCP server..."

    detect_ai_tools

    local targets=()

    if [ "$MCP_TARGETS" = "auto" ]; then
        $CLAUDE_CODE_FOUND && targets+=("claude-code")
        $CLAUDE_DESKTOP_FOUND && targets+=("claude-desktop")
        $OPENCODE_FOUND && targets+=("opencode")

        if [ ${#targets[@]} -eq 0 ]; then
            show_mcp_selection_menu || return 0
            return $?
        fi
    else
        IFS=',' read -ra targets <<< "$MCP_TARGETS"
    fi

    for target in "${targets[@]}"; do
        log_info "Configuring MCP server for $target..."

        case "$target" in
            claude-code)
                configure_mcp_for_claude_code || log_warn "Failed to configure MCP for Claude Code"
                ;;
            claude-desktop)
                configure_mcp_for_claude_desktop || log_warn "Failed to configure MCP for Claude Desktop"
                ;;
            opencode)
                configure_mcp_for_opencode || log_warn "Failed to configure MCP for OpenCode"
                ;;
            *)
                log_warn "Unknown MCP target: $target"
                ;;
        esac
    done

    return 0
}

# ============================================================================
# Shell Integration and PATH Configuration
# ============================================================================

detect_shell() {
    # Check if SKIP_SHELL_CONFIG is set
    if [ "$SKIP_SHELL_CONFIG" = "true" ]; then
        log_info "⊘ Skipping shell configuration (SKIP_SHELL_CONFIG=true)"
        return 1
    fi

    # Get shell from environment
    local shell_path="${SHELL:-}"

    # Handle missing $SHELL
    if [ -z "$shell_path" ]; then
        log_warn "SHELL environment variable not set"
        # Try to detect from parent process
        shell_path=$(ps -p $$ -o comm= 2>/dev/null || echo "")
    fi

    # Determine shell type
    case "$shell_path" in
        */bash)
            echo "bash"
            return 0
            ;;
        */zsh)
            echo "zsh"
            return 0
            ;;
        */fish)
            echo "fish"
            return 0
            ;;
        *powershell*|*pwsh*)
            echo "powershell"
            return 0
            ;;
        *)
            echo "unknown"
            return 1
            ;;
    esac
}

get_shell_config_file() {
    local shell_type="$1"
    local config_file=""

    case "$shell_type" in
        bash)
            # Prefer .bashrc, fallback to .bash_profile
            if [ -f "$HOME/.bashrc" ] || [ ! -f "$HOME/.bash_profile" ]; then
                config_file="$HOME/.bashrc"
            else
                config_file="$HOME/.bash_profile"
            fi
            ;;
        zsh)
            config_file="$HOME/.zshrc"
            ;;
        fish)
            config_file="$HOME/.config/fish/config.fish"
            ;;
        powershell)
            config_file="$HOME/Documents/PowerShell/Microsoft.PowerShell_profile.ps1"
            ;;
        *)
            return 1
            ;;
    esac

    echo "$config_file"
    return 0
}

check_path_already_configured() {
    local config_file="$1"
    local install_dir="$2"

    # Check if file exists
    if [ ! -f "$config_file" ]; then
        return 1  # Not configured
    fi

    # Search for marker comment
    if grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
        return 0  # Already configured
    fi

    # Search for PATH containing install directory
    if grep -q "$install_dir/venv/bin" "$config_file"; then
        log_warn "Found PATH entry without marker comment"
        log_warn "Manual configuration detected - skipping auto-config"
        return 0  # Assume configured
    fi

    return 1  # Not configured
}

create_config_backup() {
    local config_file="$1"
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local backup_file="${config_file}.backup.${timestamp}"

    # Check if file exists
    if [ ! -f "$config_file" ]; then
        log_info "Config file doesn't exist yet, no backup needed"
        return 0
    fi

    # Create backup
    if cp "$config_file" "$backup_file"; then
        log_info "✓ Backup created: $backup_file"
        echo "$backup_file"  # Return backup path
        return 0
    else
        log_error "Failed to create backup"
        return 1
    fi
}

add_path_to_shell_config() {
    local config_file="$1"
    local install_dir="$2"
    local shell_type="$3"

    # Create config file if it doesn't exist
    if [ ! -f "$config_file" ]; then
        # Create parent directory if needed
        local parent_dir=$(dirname "$config_file")
        mkdir -p "$parent_dir" 2>/dev/null

        touch "$config_file"
        chmod 644 "$config_file"
        log_info "Created new config file: $config_file"
    fi

    # Prepare PATH configuration
    local marker="# mcp_pdftools - Added by automated installation"
    local path_export=""

    case "$shell_type" in
        bash|zsh)
            path_export="export PATH=\"\$HOME/mcp_pdftools/venv/bin:\$PATH\""
            ;;
        fish)
            path_export="set -gx PATH \$HOME/mcp_pdftools/venv/bin \$PATH"
            ;;
        powershell)
            path_export="\$env:Path = \"\$env:USERPROFILE\\mcp_pdftools\\venv\\Scripts;\$env:Path\""
            ;;
    esac

    # Add to config file
    {
        echo ""
        echo "$marker"
        echo "$path_export"
    } >> "$config_file"

    log_info "✓ PATH configuration added to $config_file"
    return 0
}

validate_shell_config() {
    local config_file="$1"
    local shell_type="$2"
    local backup_file="$3"

    case "$shell_type" in
        bash)
            if bash -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (bash -n)"
                return 0
            fi
            ;;
        zsh)
            if zsh -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (zsh -n)"
                return 0
            fi
            ;;
        fish)
            if fish -n "$config_file" 2>/dev/null; then
                log_info "✓ Syntax validation passed (fish -n)"
                return 0
            fi
            ;;
        *)
            log_warn "Syntax validation not supported for $shell_type"
            return 0  # Assume valid
            ;;
    esac

    # Validation failed - restore backup
    log_error "Syntax validation failed!"
    if [ -n "$backup_file" ] && [ -f "$backup_file" ]; then
        log_info "Restoring backup from $backup_file"
        mv "$backup_file" "$config_file"
    fi
    return 1
}

activate_path_current_session() {
    local install_dir="$1"
    local venv_bin="$install_dir/venv/bin"

    # Add to PATH in current session
    export PATH="$venv_bin:$PATH"
    log_info "✓ PATH updated in current session"

    # Verify
    if [ -d "$venv_bin" ]; then
        log_info "✓ Virtual environment bin directory exists"
        return 0
    else
        log_error "Virtual environment bin directory not found: $venv_bin"
        return 1
    fi
}

verify_tools_accessible() {
    local tools=("pdfmerge" "pdfsplit" "pdfgettxt" "ocrutil" "pdfprotect" "pdfthumbnails" "pdfrename")
    local failed=0

    log_info "Verifying CLI tools are accessible..."

    for tool in "${tools[@]}"; do
        if command -v "$tool" >/dev/null 2>&1; then
            local tool_path=$(which "$tool" 2>/dev/null || echo "unknown")
            log_info "  ✓ $tool: $tool_path"
        else
            log_warn "  ✗ $tool: Not found in PATH"
            ((failed++))
        fi
    done

    if [ $failed -eq 0 ]; then
        log_info "✓ All 7 CLI tools are globally accessible"
        return 0
    else
        log_warn "$failed CLI tools not accessible"
        return 1
    fi
}

show_manual_config_instructions() {
    local shell_type="$1"
    local install_dir="$2"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║       Manual Shell Configuration Instructions           ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "To make PDF tools globally available, add to your shell config:"
    echo ""

    case "$shell_type" in
        bash)
            echo "For Bash (~/.bashrc):"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload:"
            echo "  source ~/.bashrc"
            ;;
        zsh)
            echo "For Zsh (~/.zshrc):"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload:"
            echo "  source ~/.zshrc"
            ;;
        fish)
            echo "For Fish (~/.config/fish/config.fish):"
            echo "  set -gx PATH $install_dir/venv/bin \$PATH"
            echo ""
            echo "Then reload:"
            echo "  source ~/.config/fish/config.fish"
            ;;
        *)
            echo "Add the following to your shell configuration file:"
            echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
            echo ""
            echo "Then reload your shell."
            ;;
    esac

    echo ""
    echo "To verify:"
    echo "  which pdfmerge"
    echo "  pdfmerge --version"
    echo ""
}

request_shell_config_consent() {
    local shell_type="$1"
    local config_file="$2"
    local install_dir="$3"

    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║         Shell Configuration (Optional)                   ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""
    echo "To make PDF tools globally available, we can configure your shell."
    echo ""
    echo "Detected shell: $shell_type"
    echo "Configuration file: $config_file"
    echo ""
    echo "The following will be added:"
    echo "  # mcp_pdftools - Added by automated installation"
    echo "  export PATH=\"$install_dir/venv/bin:\$PATH\""
    echo ""
    echo "Benefits:"
    echo "  ✓ Run 'pdfmerge' from any directory"
    echo "  ✓ No need to activate virtual environment"
    echo "  ✓ Uninstaller will automatically remove this configuration"
    echo ""
    echo "Alternative:"
    echo "  ○ Skip this step and activate venv manually:"
    echo "    \$ cd $install_dir"
    echo "    \$ source venv/bin/activate"
    echo ""

    if confirm "Configure shell automatically?"; then
        return 0
    else
        log_info "Shell configuration declined by user"
        show_manual_config_instructions "$shell_type" "$install_dir"
        return 1
    fi
}

configure_shell_environment() {
    log_info "Configuring shell environment..."

    # 1. Detect shell
    local shell_type=$(detect_shell)
    if [ $? -ne 0 ] || [ "$shell_type" = "unknown" ]; then
        log_warn "Could not detect shell type"
        show_manual_config_instructions "unknown" "$INSTALL_DIR"
        return 0  # Non-fatal
    fi

    log_info "Detected shell: $shell_type"

    # 2. Get config file
    local config_file=$(get_shell_config_file "$shell_type")
    if [ -z "$config_file" ]; then
        log_error "Could not determine config file for $shell_type"
        show_manual_config_instructions "$shell_type" "$INSTALL_DIR"
        return 0  # Non-fatal
    fi

    log_info "Configuration file: $config_file"

    # 3. Check if already configured
    if check_path_already_configured "$config_file" "$INSTALL_DIR"; then
        log_info "✓ Shell already configured, skipping"
        return 0
    fi

    # 4. Request user consent
    if ! request_shell_config_consent "$shell_type" "$config_file" "$INSTALL_DIR"; then
        return 0  # User declined, non-fatal
    fi

    # 5. Create backup
    local backup_file=$(create_config_backup "$config_file")

    # 6. Add PATH modification
    if ! add_path_to_shell_config "$config_file" "$INSTALL_DIR" "$shell_type"; then
        log_error "Failed to modify shell configuration"
        return 1
    fi

    # 7. Validate syntax
    if ! validate_shell_config "$config_file" "$shell_type" "$backup_file"; then
        log_error "Shell configuration syntax validation failed"
        return 1
    fi

    # 8. Activate in current session
    activate_path_current_session "$INSTALL_DIR"

    # 9. Verify tools accessible
    if verify_tools_accessible; then
        log_info "✓ Shell configured successfully"
        echo ""
        echo "PDF tools are now available globally:"
        echo "  \$ pdfmerge file1.pdf file2.pdf -o merged.pdf"
        echo "  \$ pdfsplit input.pdf -m pages"
        echo "  \$ pdfgettxt document.pdf -o output.txt"
        echo ""
        return 0
    else
        log_warn "Some tools not accessible, but configuration applied"
        return 0  # Non-fatal
    fi
}

remove_shell_configuration() {
    log_info "Removing shell configuration..."

    # Detect shell configs to clean
    local configs=(
        "$HOME/.bashrc"
        "$HOME/.bash_profile"
        "$HOME/.zshrc"
        "$HOME/.config/fish/config.fish"
    )

    local found=0

    for config_file in "${configs[@]}"; do
        if [ ! -f "$config_file" ]; then
            continue
        fi

        # Check if marker exists
        if ! grep -q "# mcp_pdftools - Added by automated installation" "$config_file"; then
            continue
        fi

        found=1
        log_info "Found mcp_pdftools configuration in $config_file"

        # Create backup
        local backup_file="${config_file}.backup.$(date +%Y-%m-%d_%H-%M-%S)"
        if cp "$config_file" "$backup_file"; then
            log_info "  ✓ Backup created: $backup_file"
        fi

        # Remove marker and next line (PATH export)
        # Also remove empty line before marker if it exists
        sed -i.tmp '/^$/{ N; /\n# mcp_pdftools - Added by automated installation/{ N; d; }; P; D; }' "$config_file"
        sed -i.tmp '/# mcp_pdftools - Added by automated installation/,+1 d' "$config_file"
        rm -f "${config_file}.tmp"

        log_info "  ✓ Configuration removed from $config_file"
    done

    if [ $found -eq 0 ]; then
        log_info "No shell configuration found to remove"
    else
        log_info "✓ Shell configuration cleanup complete"
    fi

    return 0
}
