"""
Unit tests for PDF Split validators.
"""

import pytest
from pathlib import Path

from pdftools.split.validators import (
    parse_ranges,
    validate_ranges,
    validate_pages
)
from pdftools.core.exceptions import InvalidRangeError


class TestParseRanges:
    """Tests for parse_ranges function."""

    def test_parse_single_range(self):
        """Test parsing a single range."""
        result = parse_ranges("1-5")
        assert result == [(1, 5)]

    def test_parse_multiple_ranges(self):
        """Test parsing multiple ranges."""
        result = parse_ranges("1-5,10-15,20-25")
        assert result == [(1, 5), (10, 15), (20, 25)]

    def test_parse_single_page(self):
        """Test parsing a single page number."""
        result = parse_ranges("5")
        assert result == [(5, 5)]

    def test_parse_mixed(self):
        """Test parsing mixed ranges and single pages."""
        result = parse_ranges("1-3,5,7-9")
        assert result == [(1, 3), (5, 5), (7, 9)]

    def test_parse_with_spaces(self):
        """Test parsing with spaces."""
        result = parse_ranges(" 1-5 , 10-15 ")
        assert result == [(1, 5), (10, 15)]

    def test_parse_empty_string(self):
        """Test parsing empty string raises error."""
        with pytest.raises(InvalidRangeError, match="empty"):
            parse_ranges("")

    def test_parse_invalid_format(self):
        """Test parsing invalid format raises error."""
        with pytest.raises(InvalidRangeError, match="Invalid"):
            parse_ranges("abc")

    def test_parse_invalid_range(self):
        """Test parsing invalid range (start > end) raises error."""
        with pytest.raises(InvalidRangeError, match="start must be <= end"):
            parse_ranges("10-5")

    def test_parse_zero_page(self):
        """Test parsing page 0 raises error."""
        with pytest.raises(InvalidRangeError, match="must be >= 1"):
            parse_ranges("0-5")

    def test_parse_negative_page(self):
        """Test parsing negative page raises error."""
        with pytest.raises(InvalidRangeError, match="Invalid"):
            parse_ranges("-5")


class TestValidateRanges:
    """Tests for validate_ranges function."""

    def test_validate_valid_ranges(self):
        """Test validating valid ranges."""
        ranges = [(1, 5), (10, 15)]
        validate_ranges(ranges, total_pages=20)
        # Should not raise

    def test_validate_range_out_of_bounds_start(self):
        """Test validating range with start page out of bounds."""
        ranges = [(0, 5)]
        with pytest.raises(InvalidRangeError, match="out of bounds"):
            validate_ranges(ranges, total_pages=10)

    def test_validate_range_out_of_bounds_end(self):
        """Test validating range with end page out of bounds."""
        ranges = [(1, 20)]
        with pytest.raises(InvalidRangeError, match="out of bounds"):
            validate_ranges(ranges, total_pages=10)

    def test_validate_start_greater_than_end(self):
        """Test validating range with start > end."""
        ranges = [(10, 5)]
        with pytest.raises(InvalidRangeError, match="start must be <= end"):
            validate_ranges(ranges, total_pages=20)

    def test_validate_overlapping_ranges_allowed(self):
        """Test overlapping ranges are allowed by default."""
        ranges = [(1, 5), (3, 7)]
        validate_ranges(ranges, total_pages=10, allow_overlap=True)
        # Should not raise

    def test_validate_overlapping_ranges_not_allowed(self):
        """Test overlapping ranges raise error when not allowed."""
        ranges = [(1, 5), (3, 7)]
        with pytest.raises(InvalidRangeError, match="Overlapping"):
            validate_ranges(ranges, total_pages=10, allow_overlap=False)

    def test_validate_empty_ranges(self):
        """Test validating empty ranges list raises error."""
        with pytest.raises(InvalidRangeError, match="empty"):
            validate_ranges([], total_pages=10)


class TestValidatePages:
    """Tests for validate_pages function."""

    def test_validate_valid_pages(self):
        """Test validating valid page numbers."""
        pages = [1, 5, 10]
        validate_pages(pages, total_pages=15)
        # Should not raise

    def test_validate_page_out_of_bounds(self):
        """Test validating page number out of bounds."""
        pages = [1, 20]
        with pytest.raises(InvalidRangeError, match="does not exist"):
            validate_pages(pages, total_pages=10)

    def test_validate_page_zero(self):
        """Test validating page 0 raises error."""
        pages = [0, 5]
        with pytest.raises(InvalidRangeError, match="must be >= 1"):
            validate_pages(pages, total_pages=10)

    def test_validate_negative_page(self):
        """Test validating negative page raises error."""
        pages = [-1, 5]
        with pytest.raises(InvalidRangeError, match="must be >= 1"):
            validate_pages(pages, total_pages=10)

    def test_validate_empty_pages(self):
        """Test validating empty pages list raises error."""
        with pytest.raises(InvalidRangeError, match="empty"):
            validate_pages([], total_pages=10)
