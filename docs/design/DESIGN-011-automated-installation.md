# DESIGN-011: Automated Installation Scripts

**Version**: 1.0
**Status**: Draft
**Author**: Architect
**Date**: 2025-11-22
**Requirement**: [REQ-011](../requirements/REQ-011-automated-installation.md) v1.0

---

## 1. Overview

### 1.1 Design Goals
- **Simplicity**: Single-command installation (`./install.sh` or `install.bat`)
- **Robustness**: Handle all error scenarios gracefully
- **Portability**: Work on Linux, Windows, macOS without modification
- **Idempotency**: Running multiple times yields same result
- **Observability**: Comprehensive logging for troubleshooting
- **Extensibility**: Easy to add new components or platforms

### 1.2 Architecture Pattern
**Modular Shell Script Architecture** with clear separation of concerns:
- Detection modules (platform, components)
- Installation modules (Python, Docker, Git, Node.js)
- Configuration modules (venv, repository, MCP)
- Testing and verification modules
- Logging and error handling infrastructure

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Installation Entry Point                  │
│               (install.sh / install.bat / install.ps1)       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Initialization Module                      │
│  - Parse arguments & environment variables                  │
│  - Set up logging infrastructure                            │
│  - Display welcome message                                  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Detection Module                          │
│  - Detect platform (OS, distribution, architecture)         │
│  - Check privileges (sudo/admin)                            │
│  - Detect existing components (Python, Docker, Git, Node.js)│
│  - Detect AI tools (Claude Code, Desktop, OpenCode)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               System Dependencies Module                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Python       │  │ Docker       │  │ Git          │      │
│  │ Installer    │  │ Installer    │  │ Installer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  Each installer:                                            │
│  - Check if already installed (skip if present)             │
│  - Download installer if needed                             │
│  - Run installation with platform-specific commands         │
│  - Verify installation succeeded                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│            Python Environment Setup Module                  │
│  - Create virtual environment (venv)                        │
│  - Activate virtual environment                             │
│  - Upgrade pip, setuptools, wheel                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Repository Management Module                   │
│  - Clone repository from GitHub (or update if exists)       │
│  - Verify repository structure                              │
│  - Check out specific branch/tag if requested               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│           Python Dependencies Installation Module           │
│  - Install from requirements.txt                            │
│  - Install package in editable mode (pip install -e .)      │
│  - Verify no dependency conflicts                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│               Functional Testing Module                     │
│  - Run post-installation tests (test_installation.py)       │
│  - Verify all CLI tools are accessible                      │
│  - Run basic functionality tests                            │
│  - Generate test report                                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              MCP Server Configuration Module                │
│  - Detect AI tools (if not skipped)                         │
│  - Install Node.js if needed                                │
│  - Install and build MCP server                             │
│  - Update AI tool configuration files                       │
│  - Verify MCP server responds                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  Finalization Module                        │
│  - Display installation summary                             │
│  - Show next steps and usage instructions                   │
│  - Close log file                                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Cross-Cutting Concerns                         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐            │
│  │  Logging   │  │   Error    │  │  Progress  │            │
│  │  System    │  │  Handling  │  │  Display   │            │
│  └────────────┘  └────────────┘  └────────────┘            │
│  All modules use these services                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Diagram

```
User
  │
  │ runs ./install.sh
  ▼
┌─────────────────┐
│ Main Installer  │───────┬─────► Logging Service
│                 │       │         (writes to log file)
│  - init_logging │       │
│  - detect_all   │       ├─────► Error Handler
│  - install_all  │       │         (catch errors, cleanup)
│  - configure_all│       │
│  - finalize     │       └─────► Progress Display
└─────────────────┘                 (user feedback)
  │
  ├─► Platform Detector ─────► OS-specific logic
  │     - detect_os()            (Linux/Windows/macOS)
  │     - detect_privileges()
  │
  ├─► Component Detector ───┬─► Python Detector
  │                         ├─► Docker Detector
  │                         ├─► Git Detector
  │                         ├─► Node.js Detector
  │                         └─► AI Tool Detector
  │
  ├─► Component Installer ──┬─► Python Installer
  │                         │     ├─► apt/dnf (Linux)
  │                         │     ├─► python.org (Windows)
  │                         │     └─► brew (macOS)
  │                         │
  │                         ├─► Docker Installer
  │                         │     ├─► docker.com repos (Linux)
  │                         │     └─► Docker Desktop (Win/Mac)
  │                         │
  │                         ├─► Git Installer
  │                         │     ├─► apt/dnf (Linux)
  │                         │     ├─► git-scm.com (Windows)
  │                         │     └─► brew/xcode (macOS)
  │                         │
  │                         └─► Node.js Installer
  │                               ├─► apt/dnf (Linux)
  │                               ├─► nodejs.org (Windows)
  │                               └─► brew (macOS)
  │
  ├─► Environment Manager ──┬─► create_venv()
  │                         ├─► activate_venv()
  │                         └─► upgrade_pip()
  │
  ├─► Repository Manager ───┬─► clone_repo()
  │                         ├─► update_repo()
  │                         └─► verify_repo_structure()
  │
  ├─► Dependency Manager ───┬─► install_requirements()
  │                         ├─► install_package()
  │                         └─► verify_dependencies()
  │
  ├─► Test Runner ──────────┬─► run_functional_tests()
  │                         └─► generate_test_report()
  │
  └─► MCP Configurator ─────┬─► detect_ai_tools()
                            ├─► install_mcp_server()
                            ├─► update_ai_tool_config()
                            └─► verify_mcp_server()
```

---

## 3. Module Design

### 3.1 Initialization Module

**File**: `install.sh` (Linux/macOS) / `install.ps1` (Windows PowerShell) / `install.bat` (Windows Batch)

**Functions**:

```bash
# init_logging()
# Purpose: Set up logging infrastructure
# Parameters: None
# Returns: Log file path
# Side effects: Creates log directory and file
init_logging() {
    local log_dir="$HOME/.mcp_pdftools/logs"
    local timestamp=$(date +%Y-%m-%d_%H-%M-%S)
    local log_file="$log_dir/install_${timestamp}.log"

    mkdir -p "$log_dir"
    touch "$log_file"

    echo "Installation started at $(date)" | tee -a "$log_file"
    echo "Log file: $log_file" | tee -a "$log_file"

    export MCP_INSTALL_LOG="$log_file"
    return 0
}

# parse_arguments()
# Purpose: Parse command-line arguments and environment variables
# Parameters: $@ (all arguments)
# Returns: 0 on success
# Side effects: Sets global variables
parse_arguments() {
    # Set defaults
    export INSTALL_DIR="${INSTALL_DIR:-$HOME/mcp_pdftools}"
    export REPO_URL="${REPO_URL:-https://github.com/YOUR_ORG/mcp_pdftools.git}"
    export PYTHON_VERSION="${PYTHON_VERSION:-3.11}"
    export SKIP_DOCKER="${SKIP_DOCKER:-false}"
    export SKIP_TESTS="${SKIP_TESTS:-false}"
    export SKIP_MCP="${SKIP_MCP:-false}"
    export MCP_TARGETS="${MCP_TARGETS:-auto}"
    export LOG_LEVEL="${LOG_LEVEL:-INFO}"

    # Parse command-line args (override env vars)
    while [[ $# -gt 0 ]]; do
        case $1 in
            --install-dir=*)
                INSTALL_DIR="${1#*=}"
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
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown argument: $1"
                show_help
                exit 1
                ;;
        esac
        shift
    done
}

# show_welcome()
# Purpose: Display welcome message and installation plan
# Parameters: None
# Returns: 0
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
  • Docker
  • Git
  • Node.js (for MCP server)
  • mcp_pdftools Python package
  • MCP server integration (optional)

Estimated time: 5-15 minutes (depending on downloads)

Press Ctrl+C to cancel, or press Enter to continue...
EOF
    read
}
```

**Key Design Decisions**:
- Log file created FIRST before any operations
- Environment variables with sensible defaults
- User can override via env vars OR command-line args
- Welcome message shows what will be installed

---

### 3.2 Platform Detection Module

**File**: `scripts/install_utils.sh` (shared utilities)

**Functions**:

```bash
# detect_platform()
# Purpose: Detect OS, distribution, and architecture
# Parameters: None
# Returns: 0 on success, 1 if platform unsupported
# Side effects: Sets global variables OS, DISTRO, ARCH
detect_platform() {
    log_info "Detecting platform..."

    # Detect OS
    case "$(uname -s)" in
        Linux*)
            OS="linux"
            # Detect distribution
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
            DISTRO_VERSION=$(cmd.exe /c ver)
            ;;
        *)
            log_error "Unsupported operating system: $(uname -s)"
            return 1
            ;;
    esac

    # Detect architecture
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

# check_privileges()
# Purpose: Check if user has required privileges
# Parameters: None
# Returns: 0 if privileges OK, 1 otherwise
check_privileges() {
    if [ "$OS" = "linux" ]; then
        if [ "$EUID" -eq 0 ]; then
            log_warn "Running as root. This is not recommended."
            log_warn "Installation will proceed, but prefer using sudo only when needed."
        fi

        # Check if sudo is available
        if ! command -v sudo &> /dev/null; then
            log_error "sudo not found. Please install sudo or run as root."
            return 1
        fi
    fi

    # On macOS and Windows, we'll request elevation when needed
    return 0
}
```

**Platform-Specific Logic**:

| Platform | Detection Method | Package Manager | Elevation |
|----------|------------------|-----------------|-----------|
| Ubuntu/Debian | `/etc/os-release` (ID=ubuntu/debian) | apt | sudo |
| Fedora/CentOS | `/etc/os-release` (ID=fedora/centos) | dnf/yum | sudo |
| macOS | `uname -s` = Darwin | Homebrew | sudo (for some operations) |
| Windows | `uname -s` = MINGW/CYGWIN or PowerShell | Chocolatey or direct downloads | Run as Administrator |

---

### 3.3 Component Detection Module

**File**: `scripts/install_utils.sh`

**Detection Strategy**:
1. Check if command exists (`command -v <cmd>`)
2. Verify version is sufficient
3. For services (Docker), check if running

```bash
# detect_python()
# Purpose: Detect existing Python installation
# Parameters: None
# Returns: 0 if Python >= 3.8 found, 1 otherwise
# Side effects: Sets PYTHON_CMD, PYTHON_VERSION_FOUND
detect_python() {
    log_info "Detecting Python..."

    # Try python3 first, then python
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

# detect_docker()
# Purpose: Detect existing Docker installation and check daemon
# Parameters: None
# Returns: 0 if Docker running, 1 otherwise
# Side effects: Sets DOCKER_VERSION_FOUND
detect_docker() {
    log_info "Detecting Docker..."

    if ! command -v docker &> /dev/null; then
        log_info "Docker not found"
        return 1
    fi

    DOCKER_VERSION_FOUND=$(docker --version | awk '{print $3}' | sed 's/,$//')
    log_info "Docker $DOCKER_VERSION_FOUND found"

    # Check if daemon is running
    if ! docker ps &> /dev/null; then
        log_warn "Docker installed but daemon not running"
        if [ "$OS" = "linux" ]; then
            log_info "Attempting to start Docker daemon..."
            sudo systemctl start docker || {
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

# detect_git()
# Purpose: Detect existing Git installation
# Parameters: None
# Returns: 0 if Git >= 2.0 found, 1 otherwise
# Side effects: Sets GIT_VERSION_FOUND
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

# detect_nodejs()
# Purpose: Detect existing Node.js installation
# Parameters: None
# Returns: 0 if Node.js >= 16 found, 1 otherwise
# Side effects: Sets NODE_VERSION_FOUND, NPM_VERSION_FOUND
detect_nodejs() {
    log_info "Detecting Node.js..."

    if ! command -v node &> /dev/null; then
        log_info "Node.js not found"
        return 1
    fi

    NODE_VERSION_FOUND=$(node --version | sed 's/^v//')
    local major=$(echo "$NODE_VERSION_FOUND" | cut -d. -f1)

    if [ "$major" -ge 16 ]; then
        NPM_VERSION_FOUND=$(npm --version)
        log_info "✓ Node.js $NODE_VERSION_FOUND found"
        log_info "✓ npm $NPM_VERSION_FOUND found"
        return 0
    else
        log_warn "Node.js $NODE_VERSION_FOUND found but version >= 16 required"
        return 1
    fi
}

# detect_ai_tools()
# Purpose: Detect installed AI tools (Claude Code, Desktop, OpenCode)
# Parameters: None
# Returns: 0 always (detection failures are logged but not fatal)
# Side effects: Sets CLAUDE_CODE_FOUND, CLAUDE_DESKTOP_FOUND, OPENCODE_FOUND
detect_ai_tools() {
    log_info "Detecting AI tools..."

    CLAUDE_CODE_FOUND=false
    CLAUDE_DESKTOP_FOUND=false
    OPENCODE_FOUND=false

    # Detect Claude Code
    local claude_code_paths=(
        "$HOME/.claude-code"
        "$HOME/.config/claude-code"
        "$HOME/Library/Application Support/claude-code"  # macOS
        "$APPDATA/claude-code"  # Windows
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
        "$HOME/Library/Application Support/Claude"  # macOS
        "$APPDATA/Claude"  # Windows
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
```

**Version Comparison Logic**:
- Parse version string: `X.Y.Z`
- Compare major version first
- If major matches, compare minor
- Ignore patch version for minimum requirements

---

### 3.4 Component Installation Module

**File**: `scripts/install_utils.sh`

Each installer follows this pattern:
1. Check if already installed (call detection function)
2. If installed and version OK: Skip
3. If not installed or version too old: Install
4. Verify installation succeeded

```bash
# install_python()
# Purpose: Install Python if not present or version too old
# Parameters: None
# Returns: 0 on success, 1 on failure
install_python() {
    if detect_python; then
        log_info "⊘ Python $PYTHON_VERSION_FOUND already installed, skipping"
        return 0
    fi

    log_info "Installing Python $PYTHON_VERSION..."

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
            # Install Homebrew if not present
            if ! command -v brew &> /dev/null; then
                log_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || return 1
            fi
            brew install python@${PYTHON_VERSION} || return 1
            ;;
        windows)
            # Download Python installer
            local python_installer="python-${PYTHON_VERSION}.exe"
            local download_url="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe"

            log_info "Downloading Python from $download_url..."
            curl -L -o "$python_installer" "$download_url" || return 1

            # Run installer silently
            log_info "Running Python installer..."
            "./$python_installer" /quiet InstallAllUsers=1 PrependPath=1 || return 1

            # Clean up installer
            rm "$python_installer"
            ;;
    esac

    # Verify installation
    if detect_python; then
        log_info "✓ Python $PYTHON_VERSION_FOUND installed successfully"
        return 0
    else
        log_error "✗ Python installation verification failed"
        return 1
    fi
}

# install_docker()
# Purpose: Install Docker if not present
# Parameters: None
# Returns: 0 on success, 1 on failure
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
            # Add Docker's official GPG key
            sudo apt-get update || return 1
            sudo apt-get install -y ca-certificates curl gnupg || return 1
            sudo install -m 0755 -d /etc/apt/keyrings || return 1
            curl -fsSL https://download.docker.com/linux/$DISTRO/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg || return 1
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
        macos|windows)
            log_warn "Docker Desktop installation requires manual intervention"
            log_info "Please visit: https://docs.docker.com/desktop/"
            log_info "After installing Docker Desktop, run this script again."
            return 1
            ;;
    esac

    # Verify installation
    if detect_docker; then
        log_info "✓ Docker installed successfully"
        return 0
    else
        log_error "✗ Docker installation verification failed"
        return 1
    fi
}

# install_git()
# Purpose: Install Git if not present
# Parameters: None
# Returns: 0 on success, 1 on failure
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
            esac
            ;;
        macos)
            # Try Homebrew first
            if command -v brew &> /dev/null; then
                brew install git || return 1
            else
                # Fall back to Xcode Command Line Tools
                xcode-select --install || return 1
            fi
            ;;
        windows)
            local git_installer="Git-Installer.exe"
            local download_url="https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe"

            curl -L -o "$git_installer" "$download_url" || return 1
            "./$git_installer" /VERYSILENT /NORESTART || return 1
            rm "$git_installer"
            ;;
    esac

    # Verify installation
    if detect_git; then
        log_info "✓ Git installed successfully"
        return 0
    else
        log_error "✗ Git installation verification failed"
        return 1
    fi
}

# install_nodejs()
# Purpose: Install Node.js if not present (for MCP server)
# Parameters: None
# Returns: 0 on success, 1 on failure
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
                    # Install NodeSource repository
                    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - || return 1
                    sudo apt-get install -y nodejs || return 1
                    ;;
                fedora|centos|rhel)
                    curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash - || return 1
                    sudo dnf install -y nodejs || return 1
                    ;;
            esac
            ;;
        macos)
            brew install node@18 || return 1
            ;;
        windows)
            local node_installer="node-installer.msi"
            local download_url="https://nodejs.org/dist/v18.18.0/node-v18.18.0-x64.msi"

            curl -L -o "$node_installer" "$download_url" || return 1
            msiexec /i "$node_installer" /qn || return 1
            rm "$node_installer"
            ;;
    esac

    # Verify installation
    if detect_nodejs; then
        log_info "✓ Node.js installed successfully"
        return 0
    else
        log_error "✗ Node.js installation verification failed"
        return 1
    fi
}
```

**Retry Logic for Downloads**:
```bash
# download_with_retry()
# Purpose: Download file with exponential backoff retry
# Parameters: $1=URL, $2=output_file, $3=max_retries (default: 3)
# Returns: 0 on success, 1 on failure
download_with_retry() {
    local url="$1"
    local output="$2"
    local max_retries="${3:-3}"
    local attempt=1
    local delay=1

    while [ $attempt -le $max_retries ]; do
        log_info "Download attempt $attempt/$max_retries: $url"

        if curl -L -o "$output" "$url"; then
            log_info "✓ Download succeeded"
            return 0
        else
            log_warn "✗ Download failed (attempt $attempt/$max_retries)"

            if [ $attempt -lt $max_retries ]; then
                log_info "Retrying in ${delay}s..."
                sleep $delay
                delay=$((delay * 2))  # Exponential backoff: 1s, 2s, 4s
            fi
        fi

        attempt=$((attempt + 1))
    done

    log_error "Download failed after $max_retries attempts"
    return 1
}
```

---

### 3.5 Python Environment Module

**File**: `scripts/install_utils.sh`

```bash
# create_virtualenv()
# Purpose: Create Python virtual environment using venv
# Parameters: None
# Returns: 0 on success, 1 on failure
# Side effects: Creates venv/ directory
create_virtualenv() {
    log_info "Creating Python virtual environment..."

    cd "$INSTALL_DIR" || return 1

    # Create venv
    "$PYTHON_CMD" -m venv venv || {
        log_error "Failed to create virtual environment"
        log_error "On Linux, you may need to install python3-venv:"
        log_error "  sudo apt install python3-venv"
        return 1
    }

    log_info "✓ Virtual environment created at $INSTALL_DIR/venv"
    return 0
}

# activate_virtualenv()
# Purpose: Activate virtual environment
# Parameters: None
# Returns: 0 on success
# Side effects: Modifies PATH and VIRTUAL_ENV
activate_virtualenv() {
    log_info "Activating virtual environment..."

    case "$OS" in
        linux|macos)
            source "$INSTALL_DIR/venv/bin/activate" || return 1
            ;;
        windows)
            # PowerShell
            if [ -f "$INSTALL_DIR/venv/Scripts/Activate.ps1" ]; then
                . "$INSTALL_DIR/venv/Scripts/Activate.ps1" || return 1
            else
                # Batch
                "$INSTALL_DIR/venv/Scripts/activate.bat" || return 1
            fi
            ;;
    esac

    # Verify activation
    if [ -z "$VIRTUAL_ENV" ]; then
        log_error "Virtual environment activation failed"
        return 1
    fi

    log_info "✓ Virtual environment activated"
    log_info "  VIRTUAL_ENV=$VIRTUAL_ENV"
    log_info "  Python: $(which python)"
    return 0
}

# upgrade_pip()
# Purpose: Upgrade pip, setuptools, and wheel in venv
# Parameters: None
# Returns: 0 on success, 1 on failure
upgrade_pip() {
    log_info "Upgrading pip, setuptools, and wheel..."

    python -m pip install --upgrade pip setuptools wheel || {
        log_error "Failed to upgrade pip"
        return 1
    }

    local pip_version=$(pip --version | awk '{print $2}')
    log_info "✓ pip upgraded to version $pip_version"
    return 0
}
```

---

### 3.6 Repository Management Module

**File**: `scripts/install_utils.sh`

```bash
# clone_repository()
# Purpose: Clone repository from GitHub or update if exists
# Parameters: None
# Returns: 0 on success, 1 on failure
clone_repository() {
    log_info "Cloning repository from $REPO_URL..."

    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "Repository already exists, updating..."
        cd "$INSTALL_DIR" || return 1
        git pull || {
            log_error "Failed to update repository"
            return 1
        }
        log_info "✓ Repository updated"
    elif [ -d "$INSTALL_DIR" ] && [ -n "$(ls -A $INSTALL_DIR)" ]; then
        log_error "Directory $INSTALL_DIR exists but is not a git repository"
        log_error "Please remove it or choose a different installation directory"
        return 1
    else
        git clone "$REPO_URL" "$INSTALL_DIR" || {
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

# verify_repository_structure()
# Purpose: Verify repository has expected structure
# Parameters: None
# Returns: 0 if valid, 1 otherwise
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
```

---

### 3.7 Dependency Installation Module

**File**: `scripts/install_utils.sh`

```bash
# install_python_dependencies()
# Purpose: Install Python dependencies from requirements.txt
# Parameters: None
# Returns: 0 on success, 1 on failure
install_python_dependencies() {
    log_info "Installing Python dependencies..."

    cd "$INSTALL_DIR" || return 1

    # Install from requirements.txt with retry
    local attempt=1
    local max_attempts=3

    while [ $attempt -le $max_attempts ]; do
        log_info "Installation attempt $attempt/$max_attempts"

        if pip install -r requirements.txt; then
            log_info "✓ Dependencies installed"
            break
        else
            log_warn "Installation failed (attempt $attempt/$max_attempts)"

            if [ $attempt -eq $max_attempts ]; then
                log_error "Failed to install dependencies after $max_attempts attempts"
                log_error "Try running with --no-cache-dir:"
                log_error "  pip install --no-cache-dir -r requirements.txt"
                return 1
            fi

            # Retry with --no-cache-dir on second attempt
            if [ $attempt -eq 2 ]; then
                log_info "Retrying with --no-cache-dir..."
                pip install --no-cache-dir -r requirements.txt || continue
            fi
        fi

        attempt=$((attempt + 1))
    done

    return 0
}

# install_package_editable()
# Purpose: Install package in editable mode
# Parameters: None
# Returns: 0 on success, 1 on failure
install_package_editable() {
    log_info "Installing package in editable mode..."

    cd "$INSTALL_DIR" || return 1

    pip install -e . || {
        log_error "Failed to install package"
        return 1
    }

    log_info "✓ Package installed in editable mode"
    return 0
}

# verify_installation()
# Purpose: Verify package installed correctly
# Parameters: None
# Returns: 0 on success, 1 on failure
verify_installation() {
    log_info "Verifying installation..."

    # Check pip list
    if ! pip list | grep -q "pdftools"; then
        log_error "Package not found in pip list"
        return 1
    fi

    # Check imports
    python -c "import pdftools; print(f'pdftools version: {pdftools.__version__}')" || {
        log_error "Failed to import pdftools"
        return 1
    }

    # Check for dependency conflicts
    local conflicts=$(pip check 2>&1 | grep -i "conflict")
    if [ -n "$conflicts" ]; then
        log_warn "Dependency conflicts detected:"
        log_warn "$conflicts"
        log_warn "This may cause issues. Consider resolving conflicts."
    fi

    log_info "✓ Installation verified"
    return 0
}
```

---

### 3.8 Functional Testing Module

**File**: `scripts/test_installation.py`

```python
#!/usr/bin/env python3
"""Post-installation functional tests.

This script verifies that all PDF tools are correctly installed
and can perform basic operations.
"""

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Tuple

# Test results
class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

def run_command(cmd: List[str], timeout: int = 30) -> Tuple[bool, str]:
    """Run command and return success status and output."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, f"Command timed out after {timeout}s"
    except Exception as e:
        return False, str(e)

def test_cli_tool_version(tool_name: str) -> TestResult:
    """Test that CLI tool responds to --version."""
    success, output = run_command([tool_name, "--version"])
    if success:
        return TestResult(
            f"{tool_name} --version",
            True,
            f"Version: {output.strip()}"
        )
    else:
        return TestResult(
            f"{tool_name} --version",
            False,
            f"Failed: {output}"
        )

def test_cli_tool_help(tool_name: str) -> TestResult:
    """Test that CLI tool responds to --help."""
    success, output = run_command([tool_name, "--help"])
    if success and len(output) > 0:
        return TestResult(
            f"{tool_name} --help",
            True,
            "Help displayed successfully"
        )
    else:
        return TestResult(
            f"{tool_name} --help",
            False,
            f"Failed: {output}"
        )

def test_python_imports() -> TestResult:
    """Test that all Python modules can be imported."""
    modules = [
        "pdftools",
        "pdftools.merge",
        "pdftools.split",
        "pdftools.ocr",
        "pdftools.protection",
        "pdftools.text_extraction",
        "pdftools.thumbnails",
        "pdftools.renaming",
    ]

    failed_imports = []
    for module in modules:
        try:
            __import__(module)
        except Exception as e:
            failed_imports.append(f"{module}: {e}")

    if not failed_imports:
        return TestResult(
            "Python module imports",
            True,
            f"All {len(modules)} modules imported successfully"
        )
    else:
        return TestResult(
            "Python module imports",
            False,
            "Failed imports:\n" + "\n".join(failed_imports)
        )

def test_docker_accessible() -> TestResult:
    """Test that Docker is accessible."""
    success, output = run_command(["docker", "ps"])
    if success:
        return TestResult(
            "Docker accessibility",
            True,
            "Docker daemon is running"
        )
    else:
        return TestResult(
            "Docker accessibility",
            False,
            f"Docker not accessible: {output}"
        )

def main():
    """Run all post-installation tests."""
    print("=" * 60)
    print("Running Post-Installation Functional Tests")
    print("=" * 60)
    print()

    results: List[TestResult] = []

    # Test 1: Python module imports
    print("Test 1: Python Module Imports...")
    results.append(test_python_imports())

    # Test 2-8: CLI tools
    cli_tools = [
        "pdfmerge",
        "pdfsplit",
        "ocrutil",
        "pdfgettxt",
        "pdfprotect",
        "pdfthumbnails",
        "pdfrename",
    ]

    for i, tool in enumerate(cli_tools, start=2):
        print(f"Test {i}: {tool} --version...")
        results.append(test_cli_tool_version(tool))

        print(f"Test {i+7}: {tool} --help...")
        results.append(test_cli_tool_help(tool))

    # Test 16: Docker
    print("Test 16: Docker Accessibility...")
    results.append(test_docker_accessible())

    # Summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)

    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    for result in results:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status}: {result.name}")
        if result.message:
            print(f"         {result.message}")

    print()
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    # Write report to file
    report_file = Path.home() / ".mcp_pdftools" / "installation_test_report.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)

    with open(report_file, "w") as f:
        f.write("Post-Installation Test Report\n")
        f.write("=" * 60 + "\n\n")
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            f.write(f"{status}: {result.name}\n")
            if result.message:
                f.write(f"  {result.message}\n")
        f.write(f"\nTotal: {len(results)}, Passed: {passed}, Failed: {failed}\n")

    print(f"\nTest report saved to: {report_file}")

    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)

if __name__ == "__main__":
    main()
```

**Calling the test script**:
```bash
# run_functional_tests()
# Purpose: Run post-installation functional tests
# Parameters: None
# Returns: 0 if all tests pass, 1 if any fail
run_functional_tests() {
    if [ "$SKIP_TESTS" = "true" ]; then
        log_info "⊘ Skipping functional tests (SKIP_TESTS=true)"
        return 0
    fi

    log_info "Running functional tests..."

    cd "$INSTALL_DIR" || return 1

    python scripts/test_installation.py
    local test_exit_code=$?

    if [ $test_exit_code -eq 0 ]; then
        log_info "✓ All functional tests passed"
        return 0
    else
        log_warn "✗ Some functional tests failed"
        log_warn "See test report at ~/.mcp_pdftools/installation_test_report.txt"
        log_warn "Installation will continue, but some features may not work"
        return 0  # Don't fail installation on test failures
    fi
}
```

---

### 3.9 MCP Server Configuration Module

**File**: `scripts/install_utils.sh`

```bash
# configure_mcp_server()
# Purpose: Detect AI tools and configure MCP server
# Parameters: None
# Returns: 0 on success, 1 on failure
configure_mcp_server() {
    if [ "$SKIP_MCP" = "true" ]; then
        log_info "⊘ Skipping MCP server configuration (SKIP_MCP=true)"
        return 0
    fi

    log_info "Configuring MCP server..."

    # Detect AI tools
    detect_ai_tools

    # Determine which tools to configure
    local targets=()

    if [ "$MCP_TARGETS" = "auto" ]; then
        # Auto-detect mode
        $CLAUDE_CODE_FOUND && targets+=("claude-code")
        $CLAUDE_DESKTOP_FOUND && targets+=("claude-desktop")
        $OPENCODE_FOUND && targets+=("opencode")

        if [ ${#targets[@]} -eq 0 ]; then
            # No AI tools detected, show menu
            show_mcp_selection_menu || return 0  # User can skip
        fi
    else
        # Manual mode (MCP_TARGETS specified)
        IFS=',' read -ra targets <<< "$MCP_TARGETS"
    fi

    # Install and configure MCP server for each target
    for target in "${targets[@]}"; do
        log_info "Configuring MCP server for $target..."

        case "$target" in
            claude-code)
                configure_mcp_for_claude_code || return 1
                ;;
            claude-desktop)
                configure_mcp_for_claude_desktop || return 1
                ;;
            opencode)
                configure_mcp_for_opencode || return 1
                ;;
            *)
                log_warn "Unknown MCP target: $target"
                ;;
        esac
    done

    return 0
}

# show_mcp_selection_menu()
# Purpose: Show interactive menu for MCP server selection
# Parameters: None
# Returns: 0 if user made selection, 1 if user skipped
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

# install_mcp_server()
# Purpose: Install and build MCP server (only once)
# Parameters: None
# Returns: 0 on success, 1 on failure
# Side effects: Sets MCP_SERVER_INSTALLED=true
install_mcp_server() {
    if [ "$MCP_SERVER_INSTALLED" = "true" ]; then
        log_info "⊘ MCP server already installed"
        return 0
    fi

    log_info "Installing MCP server..."

    # Ensure Node.js is installed
    if ! detect_nodejs; then
        log_info "Node.js not found, installing..."
        install_nodejs || return 1
    fi

    # Navigate to MCP server directory
    cd "$INSTALL_DIR/mcp-server" || {
        log_error "MCP server directory not found"
        return 1
    }

    # Install npm dependencies
    log_info "Installing npm dependencies..."
    npm install || {
        log_error "npm install failed"
        return 1
    }

    # Build server
    log_info "Building MCP server..."
    npm run build || {
        log_error "npm run build failed"
        return 1
    }

    # Verify build
    if [ ! -f "dist/index.js" ]; then
        log_error "MCP server build failed (dist/index.js not found)"
        return 1
    fi

    log_info "✓ MCP server installed and built"
    export MCP_SERVER_INSTALLED=true
    return 0
}

# configure_mcp_for_claude_code()
# Purpose: Configure MCP server for Claude Code
# Parameters: None
# Returns: 0 on success, 1 on failure
configure_mcp_for_claude_code() {
    log_info "Configuring MCP server for Claude Code..."

    # Install MCP server if not already done
    install_mcp_server || return 1

    # Find Claude Code config file
    local config_file="$CLAUDE_CODE_CONFIG"
    if [ -z "$config_file" ]; then
        # Try default locations
        for path in "$HOME/.claude-code/config.json" "$HOME/.config/claude-code/config.json"; do
            if [ -f "$path" ]; then
                config_file="$path"
                break
            fi
        done

        if [ -z "$config_file" ]; then
            log_error "Claude Code config file not found"
            log_info "Please configure manually by adding to your Claude Code config:"
            show_mcp_config_json
            return 1
        fi
    fi

    # Backup config
    cp "$config_file" "${config_file}.backup.$(date +%Y%m%d_%H%M%S)" || {
        log_warn "Failed to create config backup"
    }

    # Update config with jq (if available) or Python
    if command -v jq &> /dev/null; then
        jq ".mcpServers.pdftools = {\"command\": \"node\", \"args\": [\"$INSTALL_DIR/mcp-server/dist/index.js\"]}" \
            "$config_file" > "${config_file}.tmp" && mv "${config_file}.tmp" "$config_file"
    else
        # Use Python to update JSON
        python3 -c "
import json
with open('$config_file', 'r') as f:
    config = json.load(f)
if 'mcpServers' not in config:
    config['mcpServers'] = {}
config['mcpServers']['pdftools'] = {
    'command': 'node',
    'args': ['$INSTALL_DIR/mcp-server/dist/index.js']
}
with open('$config_file', 'w') as f:
    json.dump(config, f, indent=2)
"
    fi

    # Verify MCP server responds
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

# verify_mcp_server()
# Purpose: Verify MCP server responds to test call
# Parameters: None
# Returns: 0 if server responds, 1 otherwise
verify_mcp_server() {
    log_info "Verifying MCP server..."

    local test_request='{"jsonrpc":"2.0","method":"tools/list","id":1}'
    local response=$(echo "$test_request" | node "$INSTALL_DIR/mcp-server/dist/index.js" 2>&1)

    if echo "$response" | grep -q "pdf_merge"; then
        log_info "✓ MCP server responds correctly"
        log_info "  Available tools: pdf_merge, pdf_split, pdf_ocr, ..."
        return 0
    else
        log_error "✗ MCP server did not respond correctly"
        log_error "  Response: $response"
        return 1
    fi
}

# show_mcp_config_json()
# Purpose: Display MCP config JSON for manual configuration
# Parameters: None
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

# configure_mcp_for_claude_desktop()
# Purpose: Configure MCP server for Claude Desktop
# Parameters: None
# Returns: 0 on success, 1 on failure
configure_mcp_for_claude_desktop() {
    # Similar to configure_mcp_for_claude_code
    # but uses different config file location
    log_info "Configuring MCP server for Claude Desktop..."
    # ... (implementation similar to Claude Code)
    log_info "✓ MCP server configured for Claude Desktop"
    return 0
}

# configure_mcp_for_opencode()
# Purpose: Configure MCP server for OpenCode
# Parameters: None
# Returns: 0 on success, 1 on failure
configure_mcp_for_opencode() {
    # Similar to configure_mcp_for_claude_code
    log_info "Configuring MCP server for OpenCode..."
    # ... (implementation similar to Claude Code)
    log_info "✓ MCP server configured for OpenCode"
    return 0
}
```

---

### 3.10 Logging Module

**File**: `scripts/install_utils.sh`

```bash
# Logging functions
LOG_FILE=""

# log_info()
# Purpose: Log info message
# Parameters: $1=message
log_info() {
    local msg="[INFO] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo "$msg" | tee -a "$MCP_INSTALL_LOG"
}

# log_warn()
# Purpose: Log warning message
# Parameters: $1=message
log_warn() {
    local msg="[WARN] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;33m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"  # Yellow
}

# log_error()
# Purpose: Log error message
# Parameters: $1=message
log_error() {
    local msg="[ERROR] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;31m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"  # Red
}

# log_success()
# Purpose: Log success message
# Parameters: $1=message
log_success() {
    local msg="[SUCCESS] $(date '+%Y-%m-%d %H:%M:%S') $1"
    echo -e "\033[1;32m$msg\033[0m" | tee -a "$MCP_INSTALL_LOG"  # Green
}

# log_command()
# Purpose: Log command execution with output
# Parameters: $@=command and arguments
log_command() {
    local cmd="$@"
    log_info "Executing: $cmd"

    local output=$($cmd 2>&1)
    local exit_code=$?

    echo "$output" >> "$MCP_INSTALL_LOG"

    if [ $exit_code -eq 0 ]; then
        log_info "Command succeeded (exit code: $exit_code)"
    else
        log_error "Command failed (exit code: $exit_code)"
    fi

    return $exit_code
}
```

---

### 3.11 Error Handling Module

**File**: `scripts/install_utils.sh`

```bash
# Error handling
set -e  # Exit on error
set -o pipefail  # Pipe failures propagate

# cleanup_on_error()
# Purpose: Clean up partial installations on error
# Parameters: None
# Returns: 0
cleanup_on_error() {
    local exit_code=$?

    if [ $exit_code -ne 0 ]; then
        log_error "Installation failed with exit code: $exit_code"
        log_info "Cleaning up partial installation..."

        # Remove incomplete venv
        if [ -d "$INSTALL_DIR/venv" ] && [ ! -f "$INSTALL_DIR/venv/.installation_complete" ]; then
            log_info "Removing incomplete virtual environment..."
            rm -rf "$INSTALL_DIR/venv"
        fi

        log_error "Installation incomplete. Please check the log file:"
        log_error "  $MCP_INSTALL_LOG"
        log_error ""
        log_error "Common issues:"
        log_error "  1. Network connection - check internet connectivity"
        log_error "  2. Permissions - ensure you have sudo/admin rights"
        log_error "  3. Disk space - ensure sufficient free space"
        log_error ""
        log_error "For help, visit: https://github.com/YOUR_ORG/mcp_pdftools/issues"
    fi

    exit $exit_code
}

# Set trap for cleanup
trap cleanup_on_error EXIT INT TERM
```

---

### 3.12 Finalization Module

**File**: `install.sh`

```bash
# finalize_installation()
# Purpose: Display installation summary and next steps
# Parameters: None
# Returns: 0
finalize_installation() {
    # Mark venv as complete
    touch "$INSTALL_DIR/venv/.installation_complete"

    # Display summary
    cat <<EOF

╔═══════════════════════════════════════════════════════════╗
║              Installation Completed Successfully!         ║
╚═══════════════════════════════════════════════════════════╝

Installation Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Python $PYTHON_VERSION_FOUND installed
✓ Docker $DOCKER_VERSION_FOUND installed and running
✓ Git $GIT_VERSION_FOUND installed
✓ Node.js $NODE_VERSION_FOUND installed
✓ Virtual environment created: $INSTALL_DIR/venv
✓ Repository cloned: $INSTALL_DIR
✓ Dependencies installed
✓ Functional tests passed
✓ MCP server configured for: $(echo "${targets[@]}" | tr ' ' ', ')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Next Steps:

1. Activate the virtual environment:
   $ cd $INSTALL_DIR
   $ source venv/bin/activate  # Linux/macOS
   $ venv\\Scripts\\activate     # Windows

2. Verify installation:
   $ pdfmerge --version
   $ pdfsplit --help

3. Try merging PDFs:
   $ pdfmerge file1.pdf file2.pdf -o merged.pdf

4. Use from AI agents (if MCP configured):
   - Open Claude Code / Claude Desktop / OpenCode
   - Ask: "Merge these PDF files: file1.pdf, file2.pdf"

5. View documentation:
   $ cat $INSTALL_DIR/README.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Installation Log: $MCP_INSTALL_LOG
Test Report: $HOME/.mcp_pdftools/installation_test_report.txt

For help: https://github.com/YOUR_ORG/mcp_pdftools

Happy PDF processing! 🎉

EOF

    return 0
}
```

---

## 4. File Structure

```
mcp_pdftools/
├── install.sh                  # Main installer (Linux/macOS)
├── install.ps1                 # PowerShell installer (Windows)
├── install.bat                 # Batch installer (Windows)
├── uninstall.sh                # Uninstaller (Linux/macOS)
├── uninstall.ps1               # Uninstaller (Windows PowerShell)
├── uninstall.bat               # Uninstaller (Windows Batch)
├── scripts/
│   ├── install_utils.sh        # Shared utilities (Linux/macOS)
│   ├── install_utils.ps1       # Shared utilities (Windows PowerShell)
│   └── test_installation.py    # Post-installation functional tests
└── venv/                       # Virtual environment (created by installer)
```

---

## 5. Data Flow

### Installation Flow

```
User Input
  │
  ├─► Command-line args (--install-dir=/path)
  ├─► Environment variables (INSTALL_DIR=/path)
  └─► Interactive prompts (MCP server selection)
  │
  ▼
Installation Script
  │
  ├─► Parse and validate inputs
  ├─► Detect platform and components
  ├─► Install missing components
  ├─► Configure environment
  └─► Test installation
  │
  ▼
Log File (install_YYYY-MM-DD_HH-MM-SS.log)
  │
  ├─► All detection results
  ├─► All commands executed
  ├─► All command outputs
  └─► All errors and warnings
  │
  ▼
Test Report (installation_test_report.txt)
  │
  ├─► Test results (pass/fail)
  └─► Summary statistics
  │
  ▼
User Output
  │
  ├─► Progress messages
  ├─► Success/failure indicators
  └─► Next steps instructions
```

---

## 6. Error Handling Strategy

### Error Codes

| Exit Code | Meaning | Example |
|-----------|---------|---------|
| 0 | Success | Installation completed successfully |
| 1 | Missing privileges | User lacks sudo/admin rights |
| 2 | Unsupported platform | Windows 7, unsupported Linux distro |
| 3 | Network failure | Cannot download Python installer |
| 4 | Component installation failure | Docker installation failed |
| 5 | Virtual environment creation failure | python3-venv not installed |
| 6 | Repository clone failure | GitHub unreachable |
| 7 | Dependency installation failure | pip install failed |
| 8 | Functional test failure | CLI tools not working |

### Error Recovery

```
┌──────────────────┐
│  Error Detected  │
└────────┬─────────┘
         │
         ▼
   ┌─────────────┐
   │ Log Error   │← Full context, stack trace
   │ with Context│
   └─────┬───────┘
         │
         ▼
   ┌─────────────────┐
   │ Attempt Cleanup │
   │ - Remove partial│
   │   installations │
   │ - Preserve logs │
   └─────┬───────────┘
         │
         ▼
   ┌─────────────────────┐
   │ Display Error to    │
   │ User with:          │
   │ - Clear description │
   │ - Suggested fixes   │
   │ - Log file location │
   └─────┬───────────────┘
         │
         ▼
   ┌───────────────┐
   │ Exit with     │
   │ Appropriate   │
   │ Error Code    │
   └───────────────┘
```

---

## 7. Security Considerations

### 7.1 Download Security
- Download only from official sources:
  - Python: python.org
  - Docker: docker.com
  - Git: git-scm.com
  - Node.js: nodejs.org
- Use HTTPS for all downloads
- Verify checksums where possible (SHA256)

### 7.2 Privilege Management
- Request elevation only when necessary
- On Linux: Use sudo for specific commands, not entire script
- Warn if running as root
- Never store credentials in logs or scripts

### 7.3 Code Injection Prevention
- Validate all user inputs
- Quote all variable expansions in shell scripts
- Use `set -e` and `set -o pipefail` to catch errors
- Avoid `eval` unless absolutely necessary

---

## 8. Testing Strategy

### 8.1 Unit Tests
Test individual functions in isolation:
- Platform detection logic
- Version parsing
- Component detection

**Example**:
```bash
# Test detect_python() function
test_detect_python() {
    # Mock python3 command
    python3() { echo "Python 3.10.0"; }

    detect_python
    assertEqual "$?" "0" "detect_python should succeed"
    assertEqual "$PYTHON_VERSION_FOUND" "3.10.0" "Should detect correct version"
}
```

### 8.2 Integration Tests
Test full installation flow on each platform:

| Platform | Test Environment | Test Scenario |
|----------|------------------|---------------|
| Ubuntu 22.04 | Docker container | Fresh installation |
| Ubuntu 22.04 | Docker container | Update existing installation |
| Fedora 38 | Docker container | Fresh installation |
| macOS 13 | GitHub Actions | Fresh installation |
| Windows 11 | GitHub Actions | Fresh installation |

### 8.3 Manual Tests
- Fresh OS installations (VMs)
- Network interruption during download
- Disk space limitation
- Running as non-sudo user
- MCP server configuration with various AI tools

---

## 9. Performance Considerations

### 9.1 Optimization Strategies
- Parallel downloads where possible
- Cache package manager metadata
- Skip unnecessary dependency checks if components already installed
- Use fast download mirrors (geographically close)

### 9.2 Expected Timings

| Scenario | Expected Time |
|----------|---------------|
| Fresh installation (all components) | 10-15 minutes |
| Installation (Python+Git already installed) | 5-8 minutes |
| Installation (all components already installed) | < 2 minutes |
| Uninstallation | < 1 minute |

---

## 10. Monitoring and Observability

### 10.1 Logging Levels
- **INFO**: Normal progress messages
- **WARN**: Non-critical issues (component already installed)
- **ERROR**: Critical failures
- **DEBUG**: Detailed command output (if LOG_LEVEL=DEBUG)

### 10.2 Log File Structure
```
[INFO] 2025-11-22 14:30:00 Installation started
[INFO] 2025-11-22 14:30:00 Log file: /home/user/.mcp_pdftools/logs/install_2025-11-22_14-30-00.log
[INFO] 2025-11-22 14:30:01 Detecting platform...
[INFO] 2025-11-22 14:30:01 Platform: linux ubuntu 22.04 x86_64
[INFO] 2025-11-22 14:30:02 Detecting Python...
[INFO] 2025-11-22 14:30:02 ✓ Python 3.10.12 found at /usr/bin/python3
[INFO] 2025-11-22 14:30:03 ⊘ Python 3.10.12 already installed, skipping
...
```

---

## 11. Dependencies

### 11.1 External Dependencies
- **curl or wget**: For downloads (Linux/macOS)
- **sudo**: For system package installation (Linux/macOS)
- **Internet connection**: For downloads and git clone

### 11.2 Internal Dependencies
- REQ-010 (MCP Server): MCP server installation module depends on REQ-010 implementation

---

## 12. Future Enhancements (v2.0)

- GUI installer for Windows/macOS
- Offline installation mode (bundled dependencies)
- Automatic updates for mcp_pdftools
- Docker-only installation mode
- Integration with system package managers (snap, chocolatey, homebrew cask)

---

## 13. Acceptance Criteria Mapping

| Requirement | Design Module | Acceptance Criteria |
|-------------|---------------|---------------------|
| FR-011-1 | Platform Detection Module | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-2 | Component Installation (Python) | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-3 | Component Installation (Docker) | AC-011-1, AC-011-2, AC-011-3, AC-011-4 |
| FR-011-4 | Component Installation (Git) | AC-011-1, AC-011-2, AC-011-3, AC-011-4 |
| FR-011-5 | Python Environment Module | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-6 | Repository Management Module | AC-011-1, AC-011-2, AC-011-3, AC-011-4 |
| FR-011-7 | Dependency Installation Module | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-8 | Functional Testing Module | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-9 | Logging Module | AC-011-6 |
| FR-011-10 | Progress Indicators | AC-011-1, AC-011-2, AC-011-3 |
| FR-011-11 | Finalization Module | AC-011-7 |
| FR-011-12 | MCP Server Configuration Module | AC-011-8 |

---

## 14. Open Questions

1. **Windows Docker Installation**: Should we prompt user to install Docker Desktop manually, or attempt automated installation?
   - **Decision**: Prompt for manual installation on first attempt, provide automation in v2.0

2. **Tesseract OCR Installation**: Should we auto-install Tesseract for OCR functionality?
   - **Decision**: Optional installation, skip if not needed for basic PDF operations

3. **Multiple Python Versions**: How to handle systems with multiple Python versions?
   - **Decision**: Prefer `python3` over `python`, allow user to specify `PYTHON_VERSION`

---

## 15. Approval

**Status**: Draft → Architecture Review Required

**Next Steps**:
1. Architecture review (Phase 4)
2. Implementation (Phase 5)
3. Code review (Phase 6)
4. Testing (Phase 7)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-22
**Requirement Version**: REQ-011 v1.0
