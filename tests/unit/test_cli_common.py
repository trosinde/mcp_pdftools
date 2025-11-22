"""
Unit tests for CLI common utilities
"""

import pytest
import sys
from io import StringIO
from unittest.mock import patch

# Add scripts to path for imports
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pdftools.cli.common import (
    print_success,
    print_error,
    print_warning,
    create_stub_message,
    setup_logging,
)


class TestPrintFunctions:
    """Tests for colored print functions"""

    def test_print_success_with_color(self, capsys):
        """Test success message with colors"""
        print_success("Test successful", use_color=True)
        captured = capsys.readouterr()
        assert "✓" in captured.out
        assert "Test successful" in captured.out

    def test_print_success_without_color(self, capsys):
        """Test success message without colors"""
        print_success("Test successful", use_color=False)
        captured = capsys.readouterr()
        assert "✓ Test successful" in captured.out
        assert "\033" not in captured.out  # No ANSI codes

    def test_print_error_with_color(self, capsys):
        """Test error message with colors"""
        print_error("Test failed", use_color=True)
        captured = capsys.readouterr()
        assert "✗" in captured.err
        assert "Test failed" in captured.err

    def test_print_error_without_color(self, capsys):
        """Test error message without colors"""
        print_error("Test failed", use_color=False)
        captured = capsys.readouterr()
        assert "✗ Test failed" in captured.err
        assert "\033" not in captured.err  # No ANSI codes

    def test_print_warning_with_color(self, capsys):
        """Test warning message with colors"""
        print_warning("Test warning", use_color=True)
        captured = capsys.readouterr()
        assert "⚠" in captured.out
        assert "Test warning" in captured.out

    def test_print_warning_without_color(self, capsys):
        """Test warning message without colors"""
        print_warning("Test warning", use_color=False)
        captured = capsys.readouterr()
        assert "⚠ Test warning" in captured.out
        assert "\033" not in captured.out  # No ANSI codes


class TestStubMessage:
    """Tests for stub message creation"""

    def test_create_stub_message(self):
        """Test stub message creation"""
        msg = create_stub_message("pdfsplit", "PDF Split")

        assert "pdfsplit" in msg
        assert "PDF Split" in msg
        assert "not yet implemented" in msg
        assert "docs/requirements/" in msg
        assert "docs/TRACEABILITY_MATRIX.md" in msg
        assert "docs/DEVELOPMENT_PROCESS.md" in msg

    def test_stub_message_contains_workflow_steps(self):
        """Test stub message contains development workflow info"""
        msg = create_stub_message("ocrutil", "OCR Processing")

        assert "9-phase development process" in msg
        assert "1. Create requirement document" in msg
        assert "2. Team review" in msg
        assert "9. Release decision" in msg


class TestSetupLogging:
    """Tests for logging setup"""

    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode"""
        import logging

        setup_logging(verbose=True)
        logger = logging.getLogger()

        assert logger.level == logging.DEBUG

    def test_setup_logging_not_verbose(self):
        """Test logging setup without verbose mode"""
        import logging

        setup_logging(verbose=False)
        logger = logging.getLogger()

        assert logger.level == logging.WARNING
