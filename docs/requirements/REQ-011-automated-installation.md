# REQ-011: Automated Installation Scripts

**Version**: 1.0
**Status**: Draft
**Author**: Requirements Engineer
**Date**: 2025-11-22
**Feature**: Automated Installation for Linux, Windows, macOS

---

## 1. Overview

### 1.1 Purpose
Provide robust, user-friendly installation scripts that automatically set up the complete mcp_pdftools environment on all major operating systems (Linux, Windows, macOS) with minimal user intervention.

### 1.2 Scope
- **In Scope**:
  - Automatic detection and installation of system dependencies (Python, Docker, Git)
  - Python virtual environment creation (venv)
  - GitHub repository cloning
  - Python package installation
  - Post-installation functional tests
  - Detailed logging for troubleshooting
  - Handling of already-installed components
  - Uninstallation scripts

- **Out of Scope**:
  - GUI-based installers
  - Anaconda/Conda environment support
  - Cloud deployment
  - CI/CD pipeline integration (covered in future requirements)

### 1.3 Target Platforms
- **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 35+, CentOS 8+
- **Windows**: Windows 10/11 (PowerShell 5.1+ and Batch support)
- **macOS**: macOS 11 (Big Sur) and newer

---

## 2. User Stories

### US-011-1: Developer First-Time Setup
**As a** developer new to the project
**I want** to run a single installation script
**So that** all dependencies are automatically installed and configured without manual intervention

**Acceptance Criteria**:
- Script detects missing dependencies (Python, Docker, Git)
- Automatically downloads and installs missing components
- Creates isolated Python virtual environment using venv
- Clones mcp_pdftools repository from GitHub
- Installs all Python dependencies from requirements.txt
- Runs functional tests to verify installation
- Completes successfully with clear success message

### US-011-2: Existing Environment Detection
**As a** developer with some components already installed
**I want** the installation script to detect existing installations
**So that** I don't waste time re-downloading or risk conflicts

**Acceptance Criteria**:
- Script checks for Python 3.8+ installation
- Script checks for Docker installation and daemon status
- Script checks for Git installation
- Skips installation of components already present
- Reports which components were found vs. installed
- Continues installation with existing components

### US-011-3: Installation Troubleshooting
**As a** developer experiencing installation issues
**I want** detailed log files with timestamps
**So that** I can diagnose problems or get help efficiently

**Acceptance Criteria**:
- Creates timestamped log file (e.g., `install_2025-11-22_14-30-45.log`)
- Logs all detection steps (component versions found)
- Logs all download and installation actions
- Logs all errors with context and stack traces
- Log file location clearly displayed at script start
- Logs include system information (OS, architecture, versions)

### US-011-4: Installation Rollback
**As a** developer whose installation fails midway
**I want** the script to handle errors gracefully
**So that** my system is not left in an inconsistent state

**Acceptance Criteria**:
- Script detects critical errors during installation
- Provides clear error messages with suggested fixes
- Cleans up partial installations (removes incomplete venv, partial clones)
- Preserves log file for troubleshooting
- Exits with appropriate error code (non-zero on failure)

### US-011-5: Clean Uninstallation
**As a** developer who wants to remove mcp_pdftools
**I want** an uninstallation script
**So that** all project files and environments are cleanly removed

**Acceptance Criteria**:
- Removes virtual environment
- Removes cloned repository
- Optionally removes Docker containers/images
- Preserves system-wide dependencies (Python, Docker, Git)
- Asks for confirmation before deletion
- Logs uninstallation actions

### US-011-6: MCP Server Auto-Configuration
**As a** user of Claude Code, Claude Desktop, or OpenCode
**I want** the installation script to automatically detect my AI tools and configure the MCP server
**So that** I can immediately use PDF tools from my AI agent without manual configuration

**Acceptance Criteria**:
- Script detects installed AI tools:
  - Claude Code (checks for `~/.claude/config.json` or similar)
  - Claude Desktop (checks for config in `~/Library/Application Support/Claude/` on macOS, `%APPDATA%/Claude/` on Windows)
  - OpenCode (checks for config location)
- If AI tool detected: Automatically installs and configures MCP server integration
- If no AI tool detected: Offers guided installation with selection menu:
  ```
  MCP Server Installation:
  [1] Claude Code
  [2] Claude Desktop
  [3] OpenCode
  [4] All of the above
  [5] Skip MCP server installation
  Select option [1-5]:
  ```
- Configures selected MCP server(s) according to REQ-010
- Verifies MCP server installation with test call
- Logs MCP server configuration steps

---

## 3. Functional Requirements

### FR-011-1: Platform Detection
**Priority**: MUST
**Description**: Automatically detect operating system and architecture

**Details**:
- Detect OS family: Linux, Windows, macOS
- Detect Linux distribution (Ubuntu, Debian, Fedora, CentOS, etc.)
- Detect architecture: x86_64, arm64
- Log detected platform information
- Exit with error if platform is unsupported

**Validation**:
```bash
# Linux
./install.sh  # Detects Ubuntu 22.04 x86_64

# Windows
install.bat  # Detects Windows 11 x86_64

# macOS
./install.sh  # Detects macOS 13 arm64
```

### FR-011-2: Python Installation
**Priority**: MUST
**Description**: Ensure Python 3.8+ is installed on the system

**Details**:
- **Detection**:
  - Check for `python3` or `python` command
  - Verify version >= 3.8 using `python3 --version`
  - Check for `pip` availability

- **Linux Installation**:
  - Ubuntu/Debian: `sudo apt update && sudo apt install -y python3 python3-pip python3-venv`
  - Fedora/CentOS: `sudo dnf install -y python3 python3-pip`
  - Require sudo/root privileges

- **Windows Installation**:
  - Download Python 3.11+ installer from python.org
  - Run installer silently: `/quiet InstallAllUsers=1 PrependPath=1`
  - Verify installation after completion

- **macOS Installation**:
  - Check for Homebrew, install if missing: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
  - Install Python: `brew install python@3.11`

**Validation**:
- `python3 --version` returns >= 3.8
- `pip3 --version` succeeds
- Log Python and pip versions

### FR-011-3: Docker Installation
**Priority**: MUST
**Description**: Ensure Docker is installed and running

**Details**:
- **Detection**:
  - Check for `docker` command
  - Verify Docker daemon is running: `docker ps`
  - Check Docker version

- **Linux Installation**:
  - Add Docker's official GPG key and repository
  - Install Docker Engine: `sudo apt install -y docker-ce docker-ce-cli containerd.io` (Ubuntu/Debian)
  - Start Docker service: `sudo systemctl start docker && sudo systemctl enable docker`
  - Add current user to docker group: `sudo usermod -aG docker $USER`
  - Notify user to log out/in for group changes

- **Windows Installation**:
  - Download Docker Desktop installer
  - Run installer silently (if possible) or prompt user to install manually
  - Start Docker Desktop
  - Wait for Docker daemon to be ready

- **macOS Installation**:
  - Install via Homebrew: `brew install --cask docker`
  - Or prompt user to download Docker Desktop for Mac
  - Start Docker Desktop application
  - Wait for Docker daemon to be ready

**Validation**:
- `docker --version` succeeds
- `docker ps` succeeds (daemon is running)
- Log Docker version

### FR-011-4: Git Installation
**Priority**: MUST
**Description**: Ensure Git is installed for repository cloning

**Details**:
- **Detection**:
  - Check for `git` command
  - Verify version >= 2.0

- **Linux Installation**:
  - Ubuntu/Debian: `sudo apt install -y git`
  - Fedora/CentOS: `sudo dnf install -y git`

- **Windows Installation**:
  - Download Git for Windows installer
  - Run installer silently: `/VERYSILENT /NORESTART`

- **macOS Installation**:
  - Install via Homebrew: `brew install git`
  - Or use Xcode Command Line Tools: `xcode-select --install`

**Validation**:
- `git --version` succeeds
- Log Git version

### FR-011-5: Virtual Environment Creation
**Priority**: MUST
**Description**: Create isolated Python virtual environment using venv (NOT Anaconda)

**Details**:
- **Location**: `./venv/` in project root
- **Creation**: `python3 -m venv venv`
- **Activation**:
  - Linux/macOS: `source venv/bin/activate`
  - Windows PowerShell: `.\venv\Scripts\Activate.ps1`
  - Windows Batch: `venv\Scripts\activate.bat`
- **pip Upgrade**: `pip install --upgrade pip setuptools wheel`
- **Verification**: Ensure `which python` points to venv

**Validation**:
- Directory `venv/` exists
- `venv/bin/python` (Linux/macOS) or `venv\Scripts\python.exe` (Windows) exists
- Activated venv shows in prompt or `VIRTUAL_ENV` variable

### FR-011-6: Repository Cloning
**Priority**: MUST
**Description**: Clone mcp_pdftools repository from GitHub

**Details**:
- **Repository URL**: `https://github.com/YOUR_ORG/mcp_pdftools.git` (configurable)
- **Target Directory**: User-specified or default to `~/mcp_pdftools`
- **Clone Command**: `git clone <repo_url> <target_dir>`
- **Branch**: Default to `main` branch
- **Handling Existing Directory**:
  - If directory exists and is a git repo: `git pull` to update
  - If directory exists but not a git repo: Error and exit
  - If directory doesn't exist: Fresh clone

**Validation**:
- Directory exists and contains `.git/`
- `git status` succeeds
- Contains `setup.py` and `requirements.txt`

### FR-011-7: Dependency Installation
**Priority**: MUST
**Description**: Install all Python dependencies from requirements.txt

**Details**:
- **Command**: `pip install -r requirements.txt`
- **Additional Tools**: Install package in editable mode: `pip install -e .`
- **Verification**: Import key modules to verify installation
- **Retry Logic**: Retry up to 3 times on network failures

**Validation**:
- `pip list` shows all required packages
- `pip check` shows no conflicts
- Import test: `python -c "import pdftools; print(pdftools.__version__)"`

### FR-011-8: Functional Testing
**Priority**: MUST
**Description**: Run post-installation functional tests to verify all tools work

**Details**:
- **Test Script**: `scripts/test_installation.py` (to be created)
- **Tests**:
  - Verify all CLI tools are accessible: `pdfmerge --version`, `pdfsplit --version`, etc.
  - Run basic functionality test for each tool
  - Check Docker is accessible
  - Verify OCR dependencies (Tesseract)
- **Report**: Display test results summary (passed/failed/skipped)
- **Exit Code**: Non-zero if any critical test fails

**Validation**:
- All 7 CLI tools respond to `--help`
- Basic merge test succeeds
- Basic split test succeeds
- OCR test succeeds (if Tesseract installed)
- Test report saved to `installation_test_report.txt`

### FR-011-9: Logging System
**Priority**: MUST
**Description**: Comprehensive logging for installation troubleshooting

**Details**:
- **Log File Naming**: `install_YYYY-MM-DD_HH-MM-SS.log`
- **Log Location**:
  - Linux/macOS: `~/.mcp_pdftools/logs/`
  - Windows: `%USERPROFILE%\.mcp_pdftools\logs\`
- **Log Levels**:
  - INFO: Normal progress messages
  - WARNING: Non-critical issues (component already installed)
  - ERROR: Critical failures with stack traces
  - DEBUG: Detailed command output
- **Log Contents**:
  - Timestamp for each entry
  - System information (OS, architecture, Python version)
  - Each component detection result
  - All download/installation commands executed
  - Command output (stdout/stderr)
  - Error context and stack traces
  - Installation duration
- **Console Output**: Mirror important messages to console with color coding

**Validation**:
- Log file created at script start
- Log contains timestamped entries
- All commands logged with output
- Errors include full context

### FR-011-10: Progress Indicators
**Priority**: SHOULD
**Description**: User-friendly progress display during installation

**Details**:
- **Display**:
  - ASCII progress bar or spinner for long operations
  - Step counter: "Step 3/8: Installing Docker..."
  - Estimated time remaining (if feasible)
- **Messages**:
  - Clear descriptions: "Downloading Python 3.11 installer..."
  - Success indicators: "✓ Python 3.11 installed successfully"
  - Skip indicators: "⊘ Docker already installed, skipping"
  - Error indicators: "✗ Failed to install Git"

**Validation**:
- Progress displayed for downloads >5 seconds
- Each major step shows current/total count
- Success/failure clearly indicated

### FR-011-11: Uninstallation Script
**Priority**: SHOULD
**Description**: Clean removal of mcp_pdftools installation

**Details**:
- **Script Names**:
  - Linux/macOS: `uninstall.sh`
  - Windows: `uninstall.bat` and `uninstall.ps1`
- **Actions**:
  1. Display what will be removed
  2. Ask for user confirmation (Y/n)
  3. Deactivate virtual environment if active
  4. Remove virtual environment directory
  5. Optionally remove repository directory
  6. Optionally remove Docker images: `docker rmi mcp-pdftools-*`
  7. Remove log files (with confirmation)
  8. Do NOT remove system dependencies (Python, Docker, Git)
- **Logging**: Create uninstallation log

**Validation**:
- User can cancel at confirmation
- Virtual environment removed
- Repository optionally removed
- System dependencies preserved
- Uninstallation logged

### FR-011-12: MCP Server Detection and Configuration
**Priority**: SHOULD
**Description**: Automatically detect AI tools (Claude Code, Claude Desktop, OpenCode) and configure MCP server integration

**Details**:
- **AI Tool Detection**:
  - **Claude Code**:
    - Linux/macOS: Check `~/.claude-code/` or `~/.config/claude-code/`
    - Windows: Check `%APPDATA%/claude-code/`
    - Verify config file exists

  - **Claude Desktop**:
    - Linux: Check `~/.config/Claude/` or `~/.local/share/Claude/`
    - macOS: Check `~/Library/Application Support/Claude/`
    - Windows: Check `%APPDATA%/Claude/`
    - Verify application is installed

  - **OpenCode**:
    - Check common installation locations
    - Verify config directory exists

- **Automatic Configuration Flow** (if AI tool detected):
  1. Display: "✓ Detected Claude Code"
  2. Ask: "Install MCP server integration for Claude Code? [Y/n]"
  3. If yes:
     - Install MCP server according to REQ-010 (npm install, etc.)
     - Update AI tool config with MCP server path
     - Add pdftools server configuration
     - Display: "✓ MCP server configured for Claude Code"

- **Manual Configuration Flow** (if no AI tool detected):
  1. Display menu:
     ```
     No AI tools detected automatically.

     Would you like to install MCP server integration?
     [1] Yes, for Claude Code
     [2] Yes, for Claude Desktop
     [3] Yes, for OpenCode
     [4] Yes, for all of them
     [5] No, skip MCP server installation

     Select option [1-5]:
     ```
  2. Based on selection, install and configure MCP server for chosen tool(s)
  3. Provide manual configuration instructions if paths cannot be auto-detected

- **MCP Server Installation** (for each selected AI tool):
  - Check if Node.js/npm is installed (required for REQ-010)
  - If missing: Install Node.js or prompt user to install
  - Navigate to MCP server directory: `cd mcp-server/`
  - Install dependencies: `npm install`
  - Build server: `npm run build`
  - Update AI tool config file with server configuration:
    ```json
    {
      "mcpServers": {
        "pdftools": {
          "command": "node",
          "args": ["/path/to/mcp-server/dist/index.js"]
        }
      }
    }
    ```

- **Verification**:
  - Test MCP server responds: `echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | node mcp-server/dist/index.js`
  - Verify all 7 PDF tools are listed
  - Display success message with next steps

- **Environment Variables**:
  - `SKIP_MCP`: Skip MCP server installation entirely (default: false)
  - `MCP_TARGETS`: Comma-separated list of targets ("claude-code,claude-desktop,opencode")

**Validation**:
- AI tools correctly detected (or menu shown if none found)
- MCP server installed and built successfully
- Config files updated with correct paths
- Test call to MCP server succeeds
- User can immediately use PDF tools from their AI agent

---

## 4. Non-Functional Requirements

### NFR-011-1: Performance
**Priority**: SHOULD
- Fresh installation completes in < 15 minutes on modern systems (excluding large downloads)
- Installation with all components present completes in < 2 minutes
- Network retry delays: exponential backoff (1s, 2s, 4s)

### NFR-011-2: Reliability
**Priority**: MUST
- Installation succeeds on 95%+ of supported platforms
- Script handles network interruptions gracefully (retry logic)
- No system corruption on installation failure
- Idempotent: Running script multiple times yields same result

### NFR-011-3: Usability
**Priority**: MUST
- Single command to start installation: `./install.sh` or `install.bat`
- No configuration files required for basic installation
- Clear error messages with suggested fixes
- Progress visible during long operations

### NFR-011-4: Security
**Priority**: MUST
- Downloads only from official sources (python.org, docker.com, github.com)
- Verify checksums for downloaded installers (where possible)
- Do not store credentials in logs or scripts
- Warn if running as root/Administrator (Linux/macOS)
- Request elevation only when necessary

### NFR-011-5: Maintainability
**Priority**: SHOULD
- Modular script structure (separate functions for each component)
- Configuration via environment variables:
  - `INSTALL_DIR`: Target installation directory
  - `REPO_URL`: GitHub repository URL
  - `SKIP_TESTS`: Skip functional tests
  - `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR
- Easy to add new dependency checks

### NFR-011-6: Portability
**Priority**: MUST
- Scripts work on all specified platforms without modification
- Use POSIX-compliant shell commands (Linux/macOS)
- Windows scripts support both PowerShell and Batch
- No hardcoded paths (use relative paths or variables)

---

## 5. Technical Requirements

### TR-011-1: Script Languages
- **Linux/macOS**: Bash shell script (`.sh`)
  - Shebang: `#!/usr/bin/env bash`
  - Bash version: >= 4.0
  - POSIX-compliant where possible

- **Windows**:
  - PowerShell script (`.ps1`) for Windows 10+
  - Batch script (`.bat`) for compatibility
  - Both scripts provide same functionality

### TR-011-2: External Dependencies
**During Installation** (must work even if these are missing initially):
- curl or wget (for downloads on Linux/macOS)
- sudo (for system package installation on Linux/macOS)
- Internet connection (for downloads and git clone)

**After Installation**:
- Python 3.8+
- Docker
- Git
- Tesseract OCR (optional, for OCR functionality)
- Node.js 16+ and npm (optional, for MCP server integration)

### TR-011-3: File Structure
```
mcp_pdftools/
├── install.sh              # Linux/macOS installation script
├── install.bat             # Windows Batch installation script
├── install.ps1             # Windows PowerShell installation script
├── uninstall.sh            # Linux/macOS uninstallation
├── uninstall.bat           # Windows Batch uninstallation
├── uninstall.ps1           # Windows PowerShell uninstallation
├── scripts/
│   ├── test_installation.py  # Post-install functional tests
│   ├── install_utils.sh      # Shared utility functions (Linux/macOS)
│   └── install_utils.ps1     # Shared utility functions (Windows)
└── venv/                   # Virtual environment (created by script)
```

### TR-011-4: Environment Variables
**Set by Installation Script**:
- `MCP_PDFTOOLS_HOME`: Installation directory
- `VIRTUAL_ENV`: Python virtual environment path

**Configurable by User**:
- `INSTALL_DIR`: Target installation directory (default: `~/mcp_pdftools`)
- `REPO_URL`: GitHub repository URL (default: official repo)
- `PYTHON_VERSION`: Specific Python version to install (default: 3.11)
- `SKIP_DOCKER`: Skip Docker installation (default: false)
- `SKIP_TESTS`: Skip functional tests (default: false)
- `SKIP_MCP`: Skip MCP server installation (default: false)
- `MCP_TARGETS`: Comma-separated AI tools for MCP server (default: auto-detect)
- `LOG_LEVEL`: Logging verbosity (default: INFO)

---

## 6. Constraints

### Technical Constraints
- Must work with standard Python venv (no Anaconda/Conda support)
- Cannot require user to manually edit system files
- Must preserve existing system configurations
- Limited to official package managers (apt, dnf, brew, choco)

### Business Constraints
- Installation scripts must be open-source (same license as project)
- No telemetry or usage tracking
- No external dependencies beyond standard OS tools

### Platform Constraints
- **Linux**: Requires package manager (apt, dnf, yum)
- **Windows**: Requires PowerShell 5.1+ or Command Prompt
- **macOS**: May require Xcode Command Line Tools

---

## 7. Error Handling

### Error Categories

#### Category 1: Missing Privileges
**Error**: User lacks sudo/admin rights
**Handling**:
- Detect missing privileges before attempting installation
- Display clear message: "This script requires administrator privileges"
- Exit with code 1

#### Category 2: Unsupported Platform
**Error**: OS or architecture not supported
**Handling**:
- Detect platform at script start
- Display: "Unsupported platform: Windows 7 (requires Windows 10+)"
- Exit with code 2

#### Category 3: Network Failures
**Error**: Cannot download dependencies
**Handling**:
- Retry download up to 3 times with exponential backoff
- Log each retry attempt
- On final failure: "Failed to download Python installer after 3 attempts"
- Suggest checking internet connection
- Exit with code 3

#### Category 4: Component Installation Failure
**Error**: Dependency installation fails (Python, Docker, Git)
**Handling**:
- Log full error output
- Display component-specific error message
- Suggest manual installation steps
- Exit with code 4

#### Category 5: Virtual Environment Creation Failure
**Error**: Cannot create venv
**Handling**:
- Check if python3-venv package is installed (Linux)
- Display: "Failed to create virtual environment. Install python3-venv package."
- Exit with code 5

#### Category 6: Repository Clone Failure
**Error**: Cannot clone GitHub repository
**Handling**:
- Check internet connection
- Verify repository URL is accessible
- Suggest checking firewall/proxy settings
- Exit with code 6

#### Category 7: Dependency Installation Failure
**Error**: pip install fails
**Handling**:
- Log pip error output
- Retry with `--no-cache-dir` flag
- Check for disk space issues
- Suggest upgrading pip: `pip install --upgrade pip`
- Exit with code 7

#### Category 8: Functional Test Failures
**Error**: Post-install tests fail
**Handling**:
- Display which tests failed
- Log test output to file
- Mark installation as "completed with warnings"
- Exit with code 0 (warning) or 8 (critical test failure)

---

## 8. Installation Flowchart

```
START
  ↓
[Display Welcome & Log Location]
  ↓
[Detect Platform (OS, Architecture)]
  ↓
[Check Privileges (sudo/admin)]
  ↓
[Detect Python] → Missing? → [Install Python] → Verify
  ↓ Present
  ↓
[Detect Docker] → Missing? → [Install Docker] → Verify
  ↓ Present
  ↓
[Detect Git] → Missing? → [Install Git] → Verify
  ↓ Present
  ↓
[Create Virtual Environment (venv)]
  ↓
[Activate Virtual Environment]
  ↓
[Upgrade pip, setuptools, wheel]
  ↓
[Clone/Update Repository from GitHub]
  ↓
[Install Dependencies (pip install -r requirements.txt)]
  ↓
[Install Package (pip install -e .)]
  ↓
[Run Functional Tests]
  ↓
[Detect AI Tools (Claude Code, Claude Desktop, OpenCode)]
  ↓
AI Tool Found? → Yes → [Ask to Configure MCP Server]
  ↓ No            ↓ User agrees
  ↓               ↓
  ↓         [Detect Node.js] → Missing? → [Install Node.js]
  ↓               ↓ Present
  ↓               ↓
  ↓         [Install MCP Server (npm install, build)]
  ↓               ↓
  ↓         [Update AI Tool Config]
  ↓               ↓
  ↓         [Verify MCP Server]
  ↓               ↓
  └───────────────┘
  ↓
[Display Installation Summary]
  ↓
[Display Next Steps (including MCP usage)]
  ↓
END (Exit Code: 0=Success, 1-8=Errors)
```

---

## 9. Success Criteria

### Installation Success
- [ ] All system dependencies detected or installed (Python, Docker, Git)
- [ ] Virtual environment created and activated
- [ ] Repository cloned successfully
- [ ] All Python dependencies installed without conflicts
- [ ] All 7 CLI tools respond to `--version`
- [ ] Functional tests pass (or complete with warnings)
- [ ] MCP server configured for detected AI tools (if applicable)
- [ ] Log file created with all actions recorded
- [ ] User can immediately use any PDF tool
- [ ] User can use PDF tools from AI agent (if MCP configured)

### User Experience Success
- [ ] Single-command installation: `./install.sh` or `install.bat`
- [ ] Clear progress indicators throughout
- [ ] Errors provide actionable suggestions
- [ ] Installation completes in < 15 minutes (fresh install)
- [ ] Log file helps diagnose any issues

### Quality Success
- [ ] Installation succeeds on Ubuntu 22.04, Windows 11, macOS 13
- [ ] Handles already-installed components gracefully
- [ ] No system corruption on failure
- [ ] Uninstallation cleanly removes all project files

---

## 10. Out of Scope (Future Requirements)

- GUI-based installers
- Automated OS updates (e.g., upgrading Ubuntu)
- Integration with CI/CD pipelines (separate REQ)
- Docker-only installation (running everything in containers)
- Offline installation mode (bundled dependencies)
- Automated updates for mcp_pdftools
- Integration tests for installation scripts (separate TEST requirement)

---

## 11. Dependencies

### Upstream Dependencies
- None (this is a foundational requirement)

### Downstream Dependencies
- **REQ-010 (MCP Server)**: Installation scripts should optionally install MCP server
- Future deployment requirements will build on this installation foundation

---

## 12. Acceptance Criteria

### AC-011-1: Linux Installation
**Given** a fresh Ubuntu 22.04 system without Python, Docker, or Git
**When** user runs `./install.sh`
**Then**:
- Python 3.11+ is installed
- Docker is installed and running
- Git is installed
- Virtual environment created at `./venv/`
- Repository cloned from GitHub
- All dependencies installed
- Functional tests pass
- User sees "Installation completed successfully" message

### AC-011-2: Windows Installation
**Given** a fresh Windows 11 system
**When** user runs `install.bat` or `install.ps1`
**Then**:
- Python 3.11+ is installed
- Docker Desktop is installed and running
- Git for Windows is installed
- Virtual environment created at `.\venv\`
- Repository cloned from GitHub
- All dependencies installed
- Functional tests pass
- User sees "Installation completed successfully" message

### AC-011-3: macOS Installation
**Given** a fresh macOS 13 system
**When** user runs `./install.sh`
**Then**:
- Homebrew installed (if missing)
- Python 3.11+ installed via Homebrew
- Docker Desktop installed
- Git installed
- Virtual environment created at `./venv/`
- Repository cloned from GitHub
- All dependencies installed
- Functional tests pass
- User sees "Installation completed successfully" message

### AC-011-4: Existing Components
**Given** a system with Python 3.10, Docker, and Git already installed
**When** user runs installation script
**Then**:
- Script detects existing Python 3.10
- Script detects existing Docker
- Script detects existing Git
- Skips installation of these components
- Proceeds with venv creation and dependency installation
- Completes in < 2 minutes
- Log shows "Python 3.10 found, skipping installation"

### AC-011-5: Error Handling
**Given** a system where Docker installation fails
**When** installation script runs
**Then**:
- Error is logged with full context
- User sees clear error message: "Failed to install Docker"
- Suggested fix is displayed
- Log file path is shown
- Script exits with code 4
- No partial installations left behind

### AC-011-6: Logging
**Given** any installation scenario
**When** installation script runs
**Then**:
- Log file created: `install_YYYY-MM-DD_HH-MM-SS.log`
- Log contains platform information
- Log contains all detection results
- Log contains all commands executed
- Log contains all command outputs
- Log contains any errors with stack traces
- User can use log file to diagnose issues

### AC-011-7: Uninstallation
**Given** a completed installation
**When** user runs `./uninstall.sh` or `uninstall.bat`
**Then**:
- User is asked for confirmation
- Virtual environment is removed
- Repository is optionally removed (user choice)
- Docker images are optionally removed (user choice)
- System dependencies (Python, Docker, Git) are preserved
- Uninstallation is logged
- User sees "Uninstallation completed" message

### AC-011-8: MCP Server Auto-Configuration
**Given** a system with Claude Code installed
**When** user runs installation script
**Then**:
- Script detects Claude Code installation
- Script asks: "Install MCP server integration for Claude Code? [Y/n]"
- User confirms (Y)
- Script detects or installs Node.js 16+
- Script installs MCP server: `cd mcp-server && npm install && npm run build`
- Script updates Claude Code config with MCP server path
- Script verifies MCP server responds to test call
- User sees: "✓ MCP server configured for Claude Code"
- User can immediately invoke PDF tools from Claude Code

**Given** a system with no AI tools installed
**When** user runs installation script
**Then**:
- Script displays: "No AI tools detected automatically"
- Script shows selection menu with options 1-5
- User can select which AI tool(s) to configure
- Script configures MCP server for selected tool(s)
- Or user can skip MCP installation (option 5)

---

## 13. Testing Strategy

### Unit Testing
- Test individual functions (platform detection, version parsing, etc.)
- Mock external commands (apt, brew, docker, git)
- Test error handling for each component

### Integration Testing
- Test full installation flow on each platform (Ubuntu, Windows, macOS)
- Test with various pre-existing configurations
- Test uninstallation after installation

### Manual Testing
- Fresh OS installations (VMs or cloud instances)
- Systems with partial installations
- Network interruption scenarios
- Disk space limitation scenarios

### Test Coverage Targets
- Platform detection: 100%
- Component installation: 90%+
- Error handling: 90%+
- Overall script: 85%+

---

## 14. Documentation Requirements

### User Documentation
- **Installation Guide** (`docs/INSTALLATION.md`):
  - Quick start (single command)
  - System requirements
  - Troubleshooting common issues
  - Environment variable reference
  - Uninstallation instructions

### Developer Documentation
- **Installation Architecture** (`docs/design/DESIGN-011-automated-installation.md`):
  - Script architecture and flow
  - Component detection algorithms
  - Error handling strategy
  - Adding new platforms/components

### Inline Documentation
- Shell script comments explaining each major section
- Function-level documentation for all utility functions

---

## 15. Risks and Mitigation

### Risk 1: Platform-Specific Package Manager Changes
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Use stable package manager APIs
- Version-pin critical dependencies
- Maintain compatibility matrix
- Regular testing on fresh OS installations

### Risk 2: Network Failures During Installation
**Probability**: High
**Impact**: Medium
**Mitigation**:
- Implement retry logic with exponential backoff
- Clear error messages for network issues
- Log all download attempts
- Suggest checking firewall/proxy

### Risk 3: Permission Issues
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- Detect privileges early in script
- Request elevation only when needed
- Provide clear privilege error messages
- Document required permissions

### Risk 4: Docker Installation Complexity
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Provide fallback to manual Docker installation
- Link to official Docker installation guides
- Allow skipping Docker with `SKIP_DOCKER=true`
- Document Docker installation separately

### Risk 5: Python Version Conflicts
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Always use virtual environment (venv)
- Never modify system Python
- Clearly specify Python version requirements
- Test with multiple Python versions (3.8, 3.9, 3.10, 3.11)

---

## 16. Versioning and Compatibility

### Script Versioning
- Installation scripts follow semantic versioning: `v1.0.0`
- Version embedded in script header
- Log file includes script version

### Compatibility Matrix

| Installation Script | Python | Docker | Git | Ubuntu | Windows | macOS |
|---------------------|--------|--------|-----|--------|---------|-------|
| v1.0.0 | 3.8-3.11 | 20.10+ | 2.0+ | 20.04+ | 10/11 | 11+ |

---

## 17. Future Enhancements (v2.0)

- Offline installation mode (bundled dependencies)
- GUI installer for Windows/macOS
- Automatic updates for mcp_pdftools
- Integration with system package managers (snap, chocolatey, homebrew cask)
- Docker-only installation mode
- Multi-user installation support
- Configuration wizard for advanced options

---

## 18. References

- [Python venv Documentation](https://docs.python.org/3/library/venv.html)
- [Docker Installation Guide](https://docs.docker.com/engine/install/)
- [Git Installation Guide](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Homebrew Installation](https://brew.sh/)
- [PowerShell Documentation](https://docs.microsoft.com/en-us/powershell/)
- [Bash Scripting Guide](https://www.gnu.org/software/bash/manual/)

---

## 19. Approval

**Status**: Draft → Team Review Required

**Next Steps**:
1. Team review of requirements (Phase 2)
2. Architecture review after design (Phase 4)
3. Implementation (Phase 5)
4. Testing and test report (Phases 6-8)
5. Release decision (Phase 9)

---

**Document Version**: 1.0
**Last Updated**: 2025-11-22
**Next Review**: After Team Review (Phase 2)
