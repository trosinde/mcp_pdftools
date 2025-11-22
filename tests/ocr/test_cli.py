"""
Tests for OCR CLI
"""

import pytest
from pdftools.ocr.cli import parse_pages


class TestParsePages:
    """Test parse_pages function"""

    def test_parse_single_page(self):
        """Test parsing single page"""
        result = parse_pages("5")
        assert result == [5]

    def test_parse_multiple_pages(self):
        """Test parsing multiple pages"""
        result = parse_pages("1,3,5")
        assert result == [1, 3, 5]

    def test_parse_page_range(self):
        """Test parsing page range"""
        result = parse_pages("1-5")
        assert result == [1, 2, 3, 4, 5]

    def test_parse_mixed_format(self):
        """Test parsing mixed format"""
        result = parse_pages("1-3,5,7-9")
        assert result == [1, 2, 3, 5, 7, 8, 9]

    def test_parse_with_spaces(self):
        """Test parsing with spaces"""
        result = parse_pages("1, 3, 5-7")
        assert result == [1, 3, 5, 6, 7]

    def test_parse_removes_duplicates(self):
        """Test that duplicates are removed"""
        result = parse_pages("1,2,1-3")
        assert result == [1, 2, 3]

    def test_parse_sorts_pages(self):
        """Test that pages are sorted"""
        result = parse_pages("5,1,3")
        assert result == [1, 3, 5]
