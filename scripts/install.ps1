# Installation script for MCP PDF Tools (Windows PowerShell)

Write-Host "==================================" -ForegroundColor Cyan
Write-Host "MCP PDF Tools - Installation" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1 | Select-String -Pattern "\d+\.\d+\.\d+" | ForEach-Object { $_.Matches.Value }
    $version = [version]$pythonVersion
    $requiredVersion = [version]"3.8.0"

    if ($version -lt $requiredVersion) {
        Write-Host "Error: Python 3.8 or higher is required. Found: $pythonVersion" -ForegroundColor Red
        exit 1
    }
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found. Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "Warning: Not in a virtual environment" -ForegroundColor Yellow
    $createVenv = Read-Host "Do you want to create a virtual environment? (y/n)"

    if ($createVenv -eq 'y' -or $createVenv -eq 'Y') {
        Write-Host "Creating virtual environment..." -ForegroundColor Yellow
        python -m venv venv

        Write-Host "Activating virtual environment..." -ForegroundColor Yellow
        .\venv\Scripts\Activate.ps1

        Write-Host "Virtual environment created and activated" -ForegroundColor Green
    }
} else {
    Write-Host "Virtual environment detected: $env:VIRTUAL_ENV" -ForegroundColor Green
}
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "Pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
    Write-Host "Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "Error: requirements.txt not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Install package in development mode
Write-Host "Installing MCP PDF Tools in development mode..." -ForegroundColor Yellow
pip install -e .
Write-Host "Package installed" -ForegroundColor Green
Write-Host ""

# Install development dependencies
$installDev = Read-Host "Install development dependencies (pytest, linting tools)? (y/n)"
if ($installDev -eq 'y' -or $installDev -eq 'Y') {
    Write-Host "Installing development dependencies..." -ForegroundColor Yellow
    pip install -e ".[dev]"
    Write-Host "Development dependencies installed" -ForegroundColor Green
}
Write-Host ""

# Check Docker (for OCR functionality)
Write-Host "Checking Docker installation (required for OCR)..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "Docker found: $dockerVersion" -ForegroundColor Green

    # Pull OCR image
    $pullImage = Read-Host "Pull ocrmypdf Docker image? (required for OCR, ~500MB) (y/n)"
    if ($pullImage -eq 'y' -or $pullImage -eq 'Y') {
        Write-Host "Pulling ocrmypdf Docker image..." -ForegroundColor Yellow
        docker pull jbarlow83/ocrmypdf
        Write-Host "OCR Docker image pulled" -ForegroundColor Green
    }
} catch {
    Write-Host "Docker not found. OCR functionality will not be available." -ForegroundColor Yellow
    Write-Host "To install Docker: https://docs.docker.com/desktop/windows/" -ForegroundColor Yellow
}
Write-Host ""

# Generate test PDFs
$generateTests = Read-Host "Generate test PDF files for testing? (y/n)"
if ($generateTests -eq 'y' -or $generateTests -eq 'Y') {
    Write-Host "Generating test PDFs..." -ForegroundColor Yellow
    python scripts\generate_test_pdfs.py --all
    Write-Host "Test PDFs generated in tests\fixtures\" -ForegroundColor Green
}
Write-Host ""

# Run tests
$runTests = Read-Host "Run tests to verify installation? (y/n)"
if ($runTests -eq 'y' -or $runTests -eq 'Y') {
    Write-Host "Running tests..." -ForegroundColor Yellow
    pytest -v
    Write-Host "Tests completed" -ForegroundColor Green
}
Write-Host ""

# Summary
Write-Host "==================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Available commands:" -ForegroundColor Yellow
Write-Host "  pdftools-merge      - Merge PDF files"
Write-Host "  pdftools-split      - Split PDF into pages"
Write-Host "  pdftools-ocr        - OCR processing"
Write-Host "  pdftools-protect    - Protect/encrypt PDFs"
Write-Host "  pdftools-extract    - Extract text from PDFs"
Write-Host "  pdftools-thumbnails - Generate thumbnails"
Write-Host "  pdftools-rename     - Rename invoice PDFs"
Write-Host ""
Write-Host "For help on any command, use: <command> --help" -ForegroundColor Cyan
Write-Host ""
Write-Host "Documentation: docs\" -ForegroundColor Cyan
Write-Host "Architecture Guidelines: docs\architecture\ARCHITECTURE_GUIDELINES.md" -ForegroundColor Cyan
Write-Host ""

# Activation reminder
if (-not $env:VIRTUAL_ENV -and (Test-Path "venv")) {
    Write-Host "Remember to activate the virtual environment:" -ForegroundColor Yellow
    Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Happy PDF processing!" -ForegroundColor Green
