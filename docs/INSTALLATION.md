# Installation Guide - MCP PDF Tools

**Version**: 2.2.0
**Last Updated**: 2025-11-22

---

## ⚡ Schnellstart (Empfohlen für 99% der Benutzer)

### ✅ Linux/macOS - Automatische Installation

**Das ist alles, was Sie brauchen:**

```bash
# 1. Repository klonen
git clone https://github.com/trosinde/mcp_pdftools.git

# 2. In Verzeichnis wechseln
cd mcp_pdftools

# 3. Installer starten
./install.sh
```

**Das war's!** 🎉 Der Installer macht automatisch:
- ✅ Erkennt automatisch das geklonte Repository
- ✅ Python installieren (falls fehlt)
- ✅ Docker installieren (falls fehlt)
- ✅ Git installieren (falls fehlt)
- ✅ Virtual Environment erstellen
- ✅ Alle Abhängigkeiten installieren
- ✅ Shell-Konfiguration anbieten (.bashrc/.zshrc)
- ✅ Tests durchführen
- ✅ MCP Server konfigurieren (optional)

**Zeit**: 5-15 Minuten (je nachdem, was schon installiert ist)

**Hinweis**: Das Skript erkennt automatisch, dass Sie es aus dem geklonten Repository heraus ausführen und verwendet dieses Verzeichnis für die Installation. Sie müssen **keine** Parameter angeben!

---

### 🪟 Windows - Manuelle Anleitung

Windows benötigt manuelle Schritte:

```batch
cd mcp_pdftools
install.bat
```

Das zeigt Ihnen die Installations-Schritte an.

---

## ⚠️ Wann brauchen Sie die manuelle Installation?

**Nur in diesen seltenen Fällen:**
- ❌ Der automatische Installer funktioniert nicht
- ❌ Sie wollen die Installation selbst kontrollieren
- ❌ Sie haben spezielle Anforderungen

**Für 99% der Benutzer:** Nutzen Sie einfach `./install.sh` oben! 👆

---

## 📚 Detaillierte Dokumentation

<details>
<summary><b>Klicken Sie hier für Details zur automatischen Installation</b></summary>

## Table of Contents

1. [Automated Installation Details](#automated-installation-linuxmacos)
2. [Manual Installation (Advanced)](#manual-installation)
3. [Windows Installation](#windows-installation)
4. [System Requirements](#system-requirements)
5. [Troubleshooting](#troubleshooting)
6. [Uninstallation](#uninstallation)
7. [MCP Server Configuration](#mcp-server-configuration)

</details>

---

## Automated Installation (Linux/macOS)

### What It Does

The automated installer (`install.sh`) performs the following steps:

1. **Platform Detection** - Identifies your OS (Ubuntu, Debian, Fedora, macOS)
2. **Dependency Installation** - Installs Python, Docker, Git, Node.js if missing
3. **Virtual Environment** - Creates isolated Python environment (venv)
4. **Repository Setup** - Clones/updates repository from GitHub
5. **Package Installation** - Installs all Python dependencies
6. **Functional Tests** - Verifies all 7 tools work correctly
7. **MCP Server** - Optionally configures AI tool integration

### Installation Time

- **Fresh installation** (all components): 8-15 minutes
- **With existing components**: 1-5 minutes

### Step-by-Step

#### 1. Clone Repository

```bash
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools
```

#### 2. Run Installer

```bash
./install.sh
```

**The installer auto-detects that you're running from a cloned repository!**

The installer will display:
```
╔═══════════════════════════════════════════════════════════╗
║          MCP PDFTools - Automated Installation            ║
║                       Version 1.0                         ║
╚═══════════════════════════════════════════════════════════╝

Installation Directory: /home/user/repos/mcp_pdftools (auto-detected)
Repository: Using existing repository

This script will install:
  • Python 3.11+
  • Docker (unless --skip-docker)
  • Git
  • Node.js (for MCP server)
  • mcp_pdftools Python package
  • MCP server integration (optional)

Press Ctrl+C to cancel, or press Enter to continue...
```

#### 3. Monitor Progress

The installer shows progress for each step:
```
Step 1/10: Detecting platform...
Platform: linux ubuntu 22.04 x86_64

Step 2/10: Checking Python...
✓ Python 3.10.12 found at /usr/bin/python3
⊘ Python 3.10.12 already installed, skipping

Step 3/10: Checking Docker...
Docker not found
Installing Docker...
✓ Docker 24.0.7 installed successfully

...
```

#### 4. Verify Installation

After completion:
```bash
# Activate virtual environment
cd ~/mcp_pdftools
source venv/bin/activate

# Test tools
pdfmerge --version
pdfsplit --version
ocrutil --help
```

### Command-Line Options

Customize installation behavior:

```bash
# Custom installation directory
./install.sh --install-dir=/opt/mcp_pdftools

# Skip Docker installation
./install.sh --skip-docker

# Skip functional tests
./install.sh --skip-tests

# Skip MCP server configuration
./install.sh --skip-mcp

# Configure MCP for specific AI tool
./install.sh --mcp-targets=claude-code

# Show help
./install.sh --help
```

### Environment Variables

Alternative to command-line options:

```bash
export INSTALL_DIR=/opt/mcp_pdftools
export SKIP_DOCKER=true
export SKIP_TESTS=true
export SKIP_MCP=true
export MCP_TARGETS=claude-code,claude-desktop
./install.sh
```

### Installation Logs

All installation actions are logged to:
```
~/.mcp_pdftools/logs/install_YYYY-MM-DD_HH-MM-SS.log
```

Review logs for troubleshooting:
```bash
cat ~/.mcp_pdftools/logs/install_2025-11-22_14-30-00.log
```

---

## Manual Installation

If automated installation doesn't work or you prefer manual control:

### Prerequisites

- **Python 3.8+** - [Download](https://www.python.org/downloads/)
- **Git** - [Download](https://git-scm.com/downloads)
- **Docker** (optional, for OCR) - [Download](https://docs.docker.com/get-docker/)
- **Node.js 16+** (optional, for MCP server) - [Download](https://nodejs.org/)

### Installation Steps

#### 1. Install Python

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

**Fedora/CentOS**:
```bash
sudo dnf install python3 python3-pip
```

**macOS**:
```bash
brew install python@3.11
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/) and run installer.
✅ Check "Add Python to PATH" during installation.

#### 2. Install Git

**Ubuntu/Debian**:
```bash
sudo apt install git
```

**Fedora/CentOS**:
```bash
sudo dnf install git
```

**macOS**:
```bash
brew install git
# or
xcode-select --install
```

**Windows**:
Download from [git-scm.com](https://git-scm.com/download/win)

#### 3. Install Docker (Optional)

**Linux (Ubuntu/Debian)**:
```bash
# Add Docker's official GPG key
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
```

**macOS/Windows**:
Download Docker Desktop from [docs.docker.com/desktop](https://docs.docker.com/desktop/)

#### 4. Clone Repository

```bash
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools
```

#### 5. Create Virtual Environment

```bash
python3 -m venv venv
```

#### 6. Activate Virtual Environment

**Linux/macOS**:
```bash
source venv/bin/activate
```

**Windows (PowerShell)**:
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt)**:
```batch
venv\Scripts\activate.bat
```

#### 7. Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

#### 8. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 9. Install Package

```bash
pip install -e .
```

#### 10. Verify Installation

```bash
pdfmerge --version
pdfsplit --version
ocrutil --help
pdfgettxt --version
pdfprotect --version
pdfthumbnails --version
pdfrename --version
```

All 7 tools should respond with version information or help text.

---

## Windows Installation

### Automated Setup

Run `install.bat` for step-by-step instructions:

```batch
cd mcp_pdftools
install.bat
```

This displays:
1. Download links for Python, Docker, Git
2. Manual installation steps
3. Virtual environment setup commands

### Manual Steps

#### 1. Install Python

Download Python 3.11+ from [python.org](https://www.python.org/downloads/)

During installation:
- ✅ Check "Add Python to PATH"
- ✅ Check "Install pip"

Verify:
```batch
python --version
pip --version
```

#### 2. Install Git

Download from [git-scm.com](https://git-scm.com/download/win)

Accept default settings during installation.

#### 3. Install Docker Desktop

Download from [docs.docker.com/desktop/install/windows-install](https://docs.docker.com/desktop/install/windows-install/)

After installation:
1. Start Docker Desktop
2. Wait for "Docker is running" notification

#### 4. Clone Repository

```batch
cd %USERPROFILE%
git clone https://github.com/trosinde/mcp_pdftools.git
cd mcp_pdftools
```

#### 5. Create Virtual Environment

```batch
python -m venv venv
```

#### 6. Activate Virtual Environment

**PowerShell**:
```powershell
.\venv\Scripts\Activate.ps1
```

**Command Prompt**:
```batch
venv\Scripts\activate.bat
```

#### 7. Install Dependencies

```batch
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -e .
```

#### 8. Verify Installation

```batch
pdfmerge --version
pdfsplit --version
ocrutil --help
```

---

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **OS** | Linux (Ubuntu 20.04+, Debian 11+, Fedora 35+), macOS 11+, Windows 10/11 |
| **Python** | 3.8 or higher |
| **RAM** | 2 GB minimum, 4 GB recommended |
| **Disk Space** | 500 MB for installation |
| **Internet** | Required for installation (downloading dependencies) |

### Recommended Configuration

| Component | Recommendation |
|-----------|----------------|
| **OS** | Ubuntu 22.04 LTS, macOS 13, Windows 11 |
| **Python** | 3.11 or higher |
| **RAM** | 8 GB |
| **Disk Space** | 2 GB (includes Docker images for OCR) |
| **Docker** | Latest stable version |

### Optional Components

| Component | Purpose | Installation |
|-----------|---------|--------------|
| **Tesseract OCR** | Native OCR (alternative to Docker) | `sudo apt install tesseract-ocr` (Linux)<br>`brew install tesseract` (macOS) |
| **Node.js 16+** | MCP server for AI tools | Installed automatically by `install.sh` |

---

## Troubleshooting

### Common Issues

#### Issue 1: Permission Denied

**Error**:
```
Permission denied while trying to connect to the Docker daemon
```

**Solution**:
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in, or run:
newgrp docker

# Verify
docker ps
```

#### Issue 2: Python Version Too Old

**Error**:
```
Python 3.7 found but version >= 3.8 required
```

**Solution**:
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# Or use the automated installer
./install.sh
```

#### Issue 3: venv Creation Fails

**Error**:
```
Failed to create virtual environment
```

**Solution (Linux)**:
```bash
# Install python3-venv package
sudo apt install python3-venv

# Retry
python3 -m venv venv
```

#### Issue 4: pip Install Fails

**Error**:
```
ERROR: Could not install packages due to an EnvironmentError
```

**Solution**:
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Retry with --no-cache-dir
pip install --no-cache-dir -r requirements.txt
```

#### Issue 5: Docker Not Running

**Error**:
```
Cannot connect to Docker daemon
```

**Solution**:
```bash
# Linux
sudo systemctl start docker

# macOS/Windows
# Start Docker Desktop application
```

#### Issue 6: Command Not Found After Install

**Error**:
```
pdfmerge: command not found
```

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate.bat  # Windows

# Verify installation
pip list | grep pdftools

# Reinstall if needed
pip install -e .
```

### Getting Help

If installation fails:

1. **Check Logs**: `~/.mcp_pdftools/logs/install_*.log`
2. **Review Error Messages**: Installation shows clear error messages
3. **Run Tests**: `python scripts/test_installation.py`
4. **Manual Install**: Try manual installation steps above
5. **Report Issue**: [GitHub Issues](https://github.com/trosinde/mcp_pdftools/issues)

Include in your issue:
- Operating system and version
- Python version (`python --version`)
- Installation log file
- Error messages

---

## Uninstallation

### Automated Uninstallation

**Linux/macOS**:
```bash
cd ~/mcp_pdftools
./uninstall.sh
```

The uninstaller will:
1. Ask for confirmation
2. Remove virtual environment
3. Optionally remove installation directory
4. Optionally remove Docker images
5. Preserve system dependencies (Python, Docker, Git)

### Manual Uninstallation

#### 1. Deactivate Virtual Environment

```bash
deactivate
```

#### 2. Remove Installation Directory

**Linux/macOS**:
```bash
cd ~
rm -rf mcp_pdftools
```

**Windows**:
```batch
cd %USERPROFILE%
rmdir /s /q mcp_pdftools
```

#### 3. Remove Log Files (Optional)

**Linux/macOS**:
```bash
rm -rf ~/.mcp_pdftools
```

**Windows**:
```batch
rmdir /s /q %USERPROFILE%\.mcp_pdftools
```

#### 4. System Dependencies

**Keep** Python, Docker, Git, Node.js if you use them for other projects.

**Remove** only if no longer needed:

**Python** (not recommended):
```bash
# Ubuntu/Debian
sudo apt remove python3

# macOS
brew uninstall python@3.11
```

**Docker**:
```bash
# Ubuntu/Debian
sudo apt remove docker-ce docker-ce-cli containerd.io

# macOS
brew uninstall --cask docker
```

---

## MCP Server Configuration

### What is MCP Server?

The MCP (Model Context Protocol) server enables AI tools like Claude Code, Claude Desktop, and OpenCode to use PDF processing tools directly.

### Automated Configuration

The installer automatically:
1. Detects installed AI tools
2. Offers to configure MCP server
3. Installs Node.js if needed
4. Builds MCP server
5. Updates AI tool configuration

### Manual Configuration

If automatic configuration fails:

#### 1. Install Node.js

```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node@18

# Windows
# Download from nodejs.org
```

#### 2. Build MCP Server

```bash
cd ~/mcp_pdftools/mcp-server
npm install
npm run build
```

#### 3. Configure AI Tool

**Claude Code**:

Edit `~/.config/claude-code/config.json` (Linux) or `%APPDATA%/claude-code/config.json` (Windows):

```json
{
  "mcpServers": {
    "pdftools": {
      "command": "node",
      "args": ["/home/user/mcp_pdftools/mcp-server/dist/index.js"]
    }
  }
}
```

**Claude Desktop**:

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or similar:

```json
{
  "mcpServers": {
    "pdftools": {
      "command": "node",
      "args": ["/home/user/mcp_pdftools/mcp-server/dist/index.js"]
    }
  }
}
```

#### 4. Restart AI Tool

Restart Claude Code/Desktop to load the MCP server.

#### 5. Test

In Claude Code/Desktop:
```
"Merge these two PDF files: file1.pdf, file2.pdf"
```

The AI should use the `pdf_merge` tool.

### Troubleshooting MCP

**Server doesn't respond**:
```bash
# Test server manually
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | node mcp-server/dist/index.js

# Should output list of 7 PDF tools
```

**AI tool doesn't find server**:
1. Check config file path is correct
2. Verify absolute path to `index.js`
3. Restart AI tool
4. Check AI tool logs for errors

---

## Platform-Specific Notes

### Ubuntu/Debian

- Uses `apt` package manager
- Requires `sudo` for system package installation
- Virtual environment package: `python3-venv`

### Fedora/CentOS

- Uses `dnf` or `yum` package manager
- SELinux may require configuration for Docker
- Python usually includes venv by default

### macOS

- Requires Homebrew (installed automatically)
- May need Xcode Command Line Tools for Git
- Docker Desktop requires manual download
- ARM (M1/M2) and Intel architectures supported

### Windows

- PowerShell 5.1+ or Command Prompt required
- Windows Defender may slow installation
- Docker Desktop requires WSL 2 backend
- Long path support recommended: `git config --global core.longpaths true`

---

## Next Steps

After successful installation:

1. **Read Documentation**: [README.md](../README.md)
2. **Try Examples**: [Usage Examples](../README.md#usage-examples)
3. **Tool Guides**: [docs/tools/](../tools/)
4. **Development**: [DEVELOPMENT_PROCESS.md](DEVELOPMENT_PROCESS.md)

---

## Support

- **Documentation**: [GitHub Repository](https://github.com/trosinde/mcp_pdftools)
- **Issues**: [Report a Bug](https://github.com/trosinde/mcp_pdftools/issues)
- **Discussions**: [GitHub Discussions](https://github.com/trosinde/mcp_pdftools/discussions)

---

**Installation Guide Version**: 2.2.0
**Last Updated**: 2025-11-22
