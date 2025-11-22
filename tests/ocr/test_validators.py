"""
Tests for OCR validators
"""

import pytest
from pathlib import Path
from pdftools.ocr.validators import (
    validate_pdf,
    validate_language,
    validate_pages,
)
from pdftools.ocr.models import OCRLanguage
from pdftools.core.exceptions import (
    PDFNotFoundError,
    InvalidParameterError,
)


class TestValidatePDF:
    """Test validate_pdf function"""

    def test_validate_existing_pdf(self, tmp_path):
        """Test validation of existing PDF file"""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_text("dummy pdf")

        result = validate_pdf(pdf_file)
        assert result == pdf_file

    def test_validate_nonexistent_pdf(self, tmp_path):
        """Test validation of non-existent PDF"""
        pdf_file = tmp_path / "nonexistent.pdf"

        with pytest.raises(PDFNotFoundError):
            validate_pdf(pdf_file)

    def test_validate_non_pdf_extension(self, tmp_path):
        """Test validation of file with wrong extension"""
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("not a pdf")

        with pytest.raises(InvalidParameterError) as exc_info:
            validate_pdf(txt_file)
        assert "must be a PDF" in str(exc_info.value)


class TestValidateLanguage:
    """Test validate_language function"""

    def test_validate_single_language_enum(self):
        """Test validation with single OCRLanguage enum"""
        result = validate_language(OCRLanguage.GERMAN)
        assert result == ["deu"]

    def test_validate_single_language_string(self):
        """Test validation with single language string"""
        result = validate_language("deu")
        assert result == ["deu"]

        result = validate_language("eng")
        assert result == ["eng"]

    def test_validate_multiple_languages(self):
        """Test validation with multiple languages"""
        result = validate_language([OCRLanguage.GERMAN, OCRLanguage.ENGLISH])
        assert set(result) == {"deu", "eng"}

    def test_validate_language_name(self):
        """Test validation with language name"""
        result = validate_language("GERMAN")
        assert result == ["deu"]

        result = validate_language("english")
        assert result == ["eng"]

    def test_validate_invalid_language(self):
        """Test validation with invalid language"""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_language("invalid")
        assert "Unsupported language" in str(exc_info.value)

    def test_validate_mixed_languages(self):
        """Test validation with mixed language types"""
        result = validate_language([OCRLanguage.GERMAN, "eng", "fra"])
        assert set(result) == {"deu", "eng", "fra"}


class TestValidatePages:
    """Test validate_pages function"""

    def test_validate_empty_pages(self):
        """Test with empty pages list returns all pages"""
        result = validate_pages([], total_pages=10)
        assert result == list(range(1, 11))

    def test_validate_valid_pages(self):
        """Test with valid page numbers"""
        result = validate_pages([1, 3, 5], total_pages=10)
        assert result == [1, 3, 5]

    def test_validate_duplicate_pages(self):
        """Test that duplicates are removed"""
        result = validate_pages([1, 1, 2, 2, 3], total_pages=10)
        assert result == [1, 2, 3]

    def test_validate_unsorted_pages(self):
        """Test that pages are sorted"""
        result = validate_pages([5, 1, 3], total_pages=10)
        assert result == [1, 3, 5]

    def test_validate_page_out_of_range_low(self):
        """Test with page number too low"""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_pages([0, 1, 2], total_pages=10)
        assert "out of range" in str(exc_info.value)

    def test_validate_page_out_of_range_high(self):
        """Test with page number too high"""
        with pytest.raises(InvalidParameterError) as exc_info:
            validate_pages([1, 2, 11], total_pages=10)
        assert "out of range" in str(exc_info.value)
