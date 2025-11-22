"""
Unit tests for merge validators
"""

import pytest
from pathlib import Path

from pdftools.merge.validators import validate_input_files
from pdftools.core.exceptions import InvalidParameterError, PDFNotFoundError


class TestValidateInputFiles:
    """Tests for validate_input_files function"""

    def test_valid_two_files(self, pdf_simple_text, pdf_multipage):
        """Test validation with 2 valid files"""
        files = [pdf_simple_text, pdf_multipage]
        result = validate_input_files(files)

        assert len(result) == 2
        assert all(isinstance(f, Path) for f in result)

    def test_valid_multiple_files(self, multiple_pdfs):
        """Test validation with multiple valid files"""
        result = validate_input_files(multiple_pdfs)

        assert len(result) == len(multiple_pdfs)
        assert all(isinstance(f, Path) for f in result)

    def test_empty_list(self):
        """Test that empty list raises error"""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_input_files([])

        assert "cannot be empty" in str(exc_info.value)

    def test_single_file_raises_error(self, pdf_simple_text):
        """Test that single file raises error"""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_input_files([pdf_simple_text])

        assert "At least 2 PDF files required" in str(exc_info.value)

    def test_nonexistent_file_raises_error(self, non_existent_pdf):
        """Test that non-existent file raises error"""
        files = [non_existent_pdf, non_existent_pdf]

        with pytest.raises(PDFNotFoundError):
            validate_input_files(files, must_exist=True)

    def test_mixed_valid_and_invalid(self, pdf_simple_text, non_existent_pdf):
        """Test with mix of valid and invalid files"""
        files = [pdf_simple_text, non_existent_pdf]

        with pytest.raises(PDFNotFoundError):
            validate_input_files(files, must_exist=True)

    def test_must_exist_false_allows_nonexistent(self, temp_dir):
        """Test that must_exist=False doesn't check file existence"""
        files = [
            temp_dir / "file1.pdf",
            temp_dir / "file2.pdf"
        ]

        # Should not raise even though files don't exist
        # (but will still validate that they're PDF paths)
        result = validate_input_files(files, must_exist=False)
        assert len(result) == 2
