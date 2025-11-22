#!/bin/bash
# De-Installation script for MCP PDF Tools

set -e  # Exit on error

# Configuration
VENV_PATH=".venv"
TEST_DATA_DIR="tests/test_data"
DOCKER_IMAGE="jbarlow83/ocrmypdf"

# Parse arguments
ALL=false
NO_CONFIRM=false
KEEP_TEST_DATA=false
KEEP_DOCKER=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --all)
            ALL=true
            shift
            ;;
        --no-confirm)
            NO_CONFIRM=true
            shift
            ;;
        --keep-test-data)
            KEEP_TEST_DATA=true
            shift
            ;;
        --keep-docker)
            KEEP_DOCKER=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--all] [--no-confirm] [--keep-test-data] [--keep-docker]"
            echo ""
            echo "Options:"
            echo "  --all              Remove everything (virtualenv, test data, Docker images)"
            echo "  --no-confirm       Skip confirmation dialogs"
            echo "  --keep-test-data   Keep generated test PDF files"
            echo "  --keep-docker      Keep Docker images"
            exit 1
            ;;
    esac
done

echo "======================================="
echo "MCP PDF Tools - De-Installation"
echo "======================================="
echo ""

# Summary of what will be removed
echo "This will remove:"
echo "  - Virtual environment ($VENV_PATH)"
if [ "$KEEP_TEST_DATA" = false ] || [ "$ALL" = true ]; then
    echo "  - Test PDF files ($TEST_DATA_DIR/test_*.pdf)"
fi
if [ "$KEEP_DOCKER" = false ] || [ "$ALL" = true ]; then
    echo "  - Docker images ($DOCKER_IMAGE)"
fi
echo "  - Installation logs (install*.log, .install_state.json)"
echo ""

# Confirmation
if [ "$NO_CONFIRM" = false ]; then
    read -p "Are you sure you want to continue? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "De-installation cancelled."
        exit 0
    fi
    echo ""
fi

# Remove virtualenv
if [ -d "$VENV_PATH" ]; then
    echo "Removing virtual environment..."
    rm -rf "$VENV_PATH"
    echo "✓ Virtual environment removed: $VENV_PATH"
else
    echo "⚠️  Virtual environment not found: $VENV_PATH"
fi
echo ""

# Remove test data
if [ "$KEEP_TEST_DATA" = false ] || [ "$ALL" = true ]; then
    if [ -d "$TEST_DATA_DIR" ]; then
        echo "Removing test PDF files..."
        test_files=$(find "$TEST_DATA_DIR" -name "test_*.pdf" 2>/dev/null | wc -l)
        if [ "$test_files" -gt 0 ]; then
            find "$TEST_DATA_DIR" -name "test_*.pdf" -delete
            echo "✓ Removed $test_files test PDF file(s)"
        else
            echo "⚠️  No test PDF files found"
        fi
    else
        echo "⚠️  Test data directory not found: $TEST_DATA_DIR"
    fi
    echo ""
fi

# Remove Docker images
if [ "$KEEP_DOCKER" = false ] || [ "$ALL" = true ]; then
    if command -v docker &> /dev/null; then
        echo "Removing Docker images..."

        # Find all ocrmypdf images
        images=$(docker images "$DOCKER_IMAGE" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null)

        if [ -n "$images" ]; then
            echo "Found Docker images:"
            echo "$images"

            if [ "$NO_CONFIRM" = false ]; then
                read -p "Remove these Docker images? (y/n) " -n 1 -r
                echo ""
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    echo "$images" | xargs -r docker rmi
                    echo "✓ Docker images removed"
                else
                    echo "⚠️  Keeping Docker images"
                fi
            else
                echo "$images" | xargs -r docker rmi
                echo "✓ Docker images removed"
            fi
        else
            echo "⚠️  No Docker images found for: $DOCKER_IMAGE"
        fi
    else
        echo "⚠️  Docker not found, skipping image removal"
    fi
    echo ""
fi

# Cleanup logs
echo "Cleaning up installation logs..."
log_count=0
for log_file in install*.log .install_state.json; do
    if [ -f "$log_file" ]; then
        rm "$log_file"
        ((log_count++))
    fi
done

if [ "$log_count" -gt 0 ]; then
    echo "✓ Removed $log_count log/state file(s)"
else
    echo "⚠️  No log files found"
fi
echo ""

# Summary
echo "======================================="
echo "De-Installation Complete!"
echo "======================================="
echo ""
echo "The following have been removed:"
echo "  ✓ Virtual environment"
if [ "$KEEP_TEST_DATA" = false ] || [ "$ALL" = true ]; then
    echo "  ✓ Test PDF files"
else
    echo "  - Test PDF files (kept)"
fi
if [ "$KEEP_DOCKER" = false ] || [ "$ALL" = true ]; then
    echo "  ✓ Docker images"
else
    echo "  - Docker images (kept)"
fi
echo "  ✓ Installation logs"
echo ""
echo "The following were kept:"
echo "  - Source code (src/)"
echo "  - Documentation (docs/)"
echo "  - Configuration files"
echo ""
echo "To reinstall, run: ./scripts/install.sh"
echo ""
