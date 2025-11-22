"""
E2E tests for CLI tools
"""

import pytest
import subprocess
import sys
from pathlib import Path


class TestCLIAvailability:
    """Test that all CLI tools are available"""

    @pytest.mark.parametrize("tool", [
        "pdfmerge",
        "pdfsplit",
        "pdfgettxt",
        "ocrutil",
        "pdfprotect",
        "pdfthumbnails",
        "pdfrename",
    ])
    def test_cli_tool_exists(self, tool):
        """Test that CLI tool is installed and accessible"""
        result = subprocess.run(
            ["which", tool],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0, f"{tool} not found in PATH"
        assert tool in result.stdout


class TestPDFMergeCLI:
    """E2E tests for pdfmerge CLI"""

    def test_pdfmerge_help(self):
        """Test pdfmerge --help"""
        result = subprocess.run(
            ["pdfmerge", "--help"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "Merge multiple PDF files" in result.stdout
        assert "--files" in result.stdout or "-f" in result.stdout
        assert "--output" in result.stdout or "-o" in result.stdout

    def test_pdfmerge_version(self):
        """Test pdfmerge --version"""
        result = subprocess.run(
            ["pdfmerge", "--version"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0
        assert "1.0" in result.stdout


class TestStubCLITools:
    """E2E tests for stub CLI tools"""

    @pytest.mark.parametrize("tool,feature_name", [
        ("pdfsplit", "PDF Split"),
        ("pdfgettxt", "PDF Text Extraction"),
        ("ocrutil", "OCR Processing"),
        ("pdfprotect", "PDF Protection"),
        ("pdfthumbnails", "Thumbnail Generation"),
        ("pdfrename", "Invoice Renaming"),
    ])
    def test_stub_shows_coming_soon_message(self, tool, feature_name):
        """Test stub tools show 'coming soon' message"""
        result = subprocess.run(
            [tool],
            capture_output=True,
            text=True
        )

        # Stub tools should exit with code 1
        assert result.returncode == 1

        # Should show feature name
        assert feature_name in result.stdout

        # Should show warning
        assert "not yet implemented" in result.stdout

        # Should reference documentation
        assert "docs/" in result.stdout
        assert "DEVELOPMENT_PROCESS.md" in result.stdout

    @pytest.mark.parametrize("tool", [
        "pdfsplit",
        "pdfgettxt",
        "ocrutil",
        "pdfprotect",
        "pdfthumbnails",
        "pdfrename",
    ])
    def test_stub_mentions_workflow(self, tool):
        """Test stub tools mention 9-phase workflow"""
        result = subprocess.run(
            [tool],
            capture_output=True,
            text=True
        )

        assert "9-phase development process" in result.stdout
        assert "1. Create requirement document" in result.stdout
        assert "Team review" in result.stdout
        assert "Testing" in result.stdout
