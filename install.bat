@echo off
REM MCP PDFTools Installer for Windows
REM Version: 1.0

echo.
echo ================================================================
echo          MCP PDFTools - Windows Installation
echo                     Version 1.0
echo ================================================================
echo.
echo Windows installation requires manual steps:
echo.
echo 1. Install Python 3.8+ from https://www.python.org/downloads/
echo    - Make sure to check "Add Python to PATH" during installation
echo.
echo 2. Install Docker Desktop from https://docs.docker.com/desktop/install/windows-install/
echo.
echo 3. Install Git from https://git-scm.com/download/win
echo.
echo 4. Install Node.js from https://nodejs.org/ (if you want MCP server)
echo.
echo 5. Open PowerShell or Command Prompt and run:
echo    cd %USERPROFILE%
echo    git clone https://github.com/YOUR_ORG/mcp_pdftools.git
echo    cd mcp_pdftools
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install --upgrade pip setuptools wheel
echo    pip install -r requirements.txt
echo    pip install -e .
echo.
echo 6. Test installation:
echo    pdfmerge --version
echo.
echo For detailed instructions, see:
echo   docs/INSTALLATION.md
echo.
echo ================================================================
echo.
pause
