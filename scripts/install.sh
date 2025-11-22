#!/bin/bash
# Installation script for MCP PDF Tools
# Enhanced version with State Management and Health Check

set -e  # Exit on error

# Configuration
VENV_PATH=".venv"
DOCKER_IMAGE="jbarlow83/ocrmypdf:v14.4.0"
LOG_FILE="install.log"

# Parse arguments
NO_DOCKER=false
NO_TEST_PDFS=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-docker)
            NO_DOCKER=true
            shift
            ;;
        --no-test-pdfs)
            NO_TEST_PDFS=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-docker] [--no-test-pdfs] [--verbose]"
            exit 1
            ;;
    esac
done

echo "=================================="
echo "MCP PDF Tools - Installation"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.8"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    echo "❌ Error: Python 3.8 or higher is required. Found: $python_version"
    exit 1
fi
echo "✓ Python version: $python_version"
echo ""

# Check if in virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️  Warning: Not in a virtual environment"
    read -p "Do you want to create a virtual environment? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Creating virtual environment..."
        python3 -m venv venv
        echo "Activating virtual environment..."
        source venv/bin/activate
        echo "✓ Virtual environment created and activated"
    fi
else
    echo "✓ Virtual environment detected: $VIRTUAL_ENV"
fi
echo ""

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip
echo "✓ Pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    echo "✓ Dependencies installed"
else
    echo "❌ requirements.txt not found"
    exit 1
fi
echo ""

# Install package in development mode
echo "Installing MCP PDF Tools in development mode..."
pip install -e .
echo "✓ Package installed"
echo ""

# Install development dependencies
read -p "Install development dependencies (pytest, linting tools)? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip install -e ".[dev]"
    echo "✓ Development dependencies installed"
fi
echo ""

# Check Docker (for OCR functionality)
if [ "$NO_DOCKER" = false ]; then
    echo "Checking Docker installation (required for OCR)..."
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version 2>&1)
        echo "✓ Docker found: $docker_version"

        # Pull OCR image with pinned version
        read -p "Pull ocrmypdf Docker image ($DOCKER_IMAGE)? (required for OCR, ~500MB) (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Pulling ocrmypdf Docker image..."
            docker pull $DOCKER_IMAGE
            echo "✓ OCR Docker image pulled"

            # Test Docker OCR
            echo "Testing Docker OCR..."
            if docker run --rm $DOCKER_IMAGE --version > /dev/null 2>&1; then
                echo "✓ Docker OCR test successful"
            else
                echo "⚠️  Docker OCR test failed"
            fi
        fi
    else
        echo "⚠️  Docker not found. OCR functionality will not be available."
        echo "   To install Docker: https://docs.docker.com/get-docker/"
    fi
    echo ""
else
    echo "⚠️  Skipping Docker setup (--no-docker flag)"
    echo ""
fi

# Generate test PDFs
read -p "Generate test PDF files for testing? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Generating test PDFs..."
    python3 scripts/generate_test_pdfs.py --all
    echo "✓ Test PDFs generated in tests/fixtures/"
fi
echo ""

# Run tests
read -p "Run tests to verify installation? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest -v
    echo "✓ Tests completed"
fi
echo ""

# Health Check
echo "Running health check..."
if [ -f "scripts/health_check.py" ]; then
    if python3 scripts/health_check.py; then
        echo "✓ Health check passed"
    else
        echo "⚠️  Health check failed - see above for details"
    fi
else
    echo "⚠️  Health check script not found, skipping..."
fi
echo ""

# Summary
echo "=================================="
echo "Installation Complete!"
echo "=================================="
echo ""
echo "Available commands:"
echo "  pdftools-merge      - Merge PDF files"
echo "  pdftools-split      - Split PDF into pages"
echo "  pdftools-ocr        - OCR processing"
echo "  pdftools-protect    - Protect/encrypt PDFs"
echo "  pdftools-extract    - Extract text from PDFs"
echo "  pdftools-thumbnails - Generate thumbnails"
echo "  pdftools-rename     - Rename invoice PDFs"
echo ""
echo "For help on any command, use: <command> --help"
echo ""
echo "Documentation: docs/"
echo "Architecture Guidelines: docs/architecture/ARCHITECTURE_GUIDELINES.md"
echo ""

# Activation reminder
if [[ -z "$VIRTUAL_ENV" ]] && [ -d "venv" ]; then
    echo "⚠️  Remember to activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo ""
fi

echo "Installation log saved to: $LOG_FILE"
echo "Happy PDF processing! 🎉"
