"""
Unit tests for PDF Split models.
"""

import pytest
from pathlib import Path

from pdftools.split.models import SplitMode, SplitConfig, SplitResult
from pdftools.core.exceptions import ValidationError


class TestSplitMode:
    """Tests for SplitMode enum."""

    def test_split_mode_values(self):
        """Test SplitMode enum values."""
        assert SplitMode.PAGES == "pages"
        assert SplitMode.RANGES == "ranges"
        assert SplitMode.PARTS == "parts"
        assert SplitMode.SPECIFIC_PAGES == "specific"


class TestSplitConfig:
    """Tests for SplitConfig dataclass."""

    def test_config_with_pages_mode(self):
        """Test creating config with PAGES mode."""
        config = SplitConfig(
            input_path=Path("test.pdf"),
            mode=SplitMode.PAGES
        )
        assert config.mode == SplitMode.PAGES
        assert config.prefix == "test"
        assert config.output_dir == Path(".")

    def test_config_with_ranges_mode_valid(self):
        """Test creating config with RANGES mode and ranges."""
        config = SplitConfig(
            input_path=Path("test.pdf"),
            mode=SplitMode.RANGES,
            ranges=[(1, 5), (10, 15)]
        )
        assert config.mode == SplitMode.RANGES
        assert config.ranges == [(1, 5), (10, 15)]

    def test_config_with_ranges_mode_missing_ranges(self):
        """Test creating config with RANGES mode but no ranges raises error."""
        with pytest.raises(ValidationError, match="ranges required"):
            SplitConfig(
                input_path=Path("test.pdf"),
                mode=SplitMode.RANGES
            )

    def test_config_with_parts_mode_valid(self):
        """Test creating config with PARTS mode and num_parts."""
        config = SplitConfig(
            input_path=Path("test.pdf"),
            mode=SplitMode.PARTS,
            num_parts=5
        )
        assert config.mode == SplitMode.PARTS
        assert config.num_parts == 5

    def test_config_with_parts_mode_missing_num_parts(self):
        """Test creating config with PARTS mode but no num_parts raises error."""
        with pytest.raises(ValidationError, match="num_parts required"):
            SplitConfig(
                input_path=Path("test.pdf"),
                mode=SplitMode.PARTS
            )

    def test_config_with_specific_pages_mode_valid(self):
        """Test creating config with SPECIFIC_PAGES mode and pages."""
        config = SplitConfig(
            input_path=Path("test.pdf"),
            mode=SplitMode.SPECIFIC_PAGES,
            pages=[1, 5, 10]
        )
        assert config.mode == SplitMode.SPECIFIC_PAGES
        assert config.pages == [1, 5, 10]

    def test_config_with_specific_pages_mode_missing_pages(self):
        """Test creating config with SPECIFIC_PAGES mode but no pages raises error."""
        with pytest.raises(ValidationError, match="pages required"):
            SplitConfig(
                input_path=Path("test.pdf"),
                mode=SplitMode.SPECIFIC_PAGES
            )

    def test_config_invalid_num_parts(self):
        """Test creating config with invalid num_parts raises error."""
        with pytest.raises(ValidationError, match="must be >= 1"):
            SplitConfig(
                input_path=Path("test.pdf"),
                mode=SplitMode.PARTS,
                num_parts=0
            )

    def test_config_custom_prefix(self):
        """Test creating config with custom prefix."""
        config = SplitConfig(
            input_path=Path("test.pdf"),
            prefix="custom"
        )
        assert config.prefix == "custom"

    def test_config_string_paths_converted(self):
        """Test that string paths are converted to Path objects."""
        config = SplitConfig(
            input_path="test.pdf",
            output_dir="./output"
        )
        assert isinstance(config.input_path, Path)
        assert isinstance(config.output_dir, Path)


class TestSplitResult:
    """Tests for SplitResult dataclass."""

    def test_result_success(self):
        """Test creating successful result."""
        result = SplitResult(
            status='success',
            num_files=10,
            output_files=[Path(f"page_{i}.pdf") for i in range(10)]
        )
        assert result.success is True
        assert result.num_files == 10
        assert len(result.output_files) == 10

    def test_result_error(self):
        """Test creating error result."""
        result = SplitResult(
            status='error',
            message="Something went wrong"
        )
        assert result.success is False
        assert result.num_files == 0
        assert result.message == "Something went wrong"

    def test_result_str_success(self):
        """Test string representation of successful result."""
        result = SplitResult(status='success', num_files=5)
        assert "Split successful: 5 files created" in str(result)

    def test_result_str_error(self):
        """Test string representation of error result."""
        result = SplitResult(status='error', message="Test error")
        assert "Split failed: Test error" in str(result)

    def test_result_with_metadata(self):
        """Test result with metadata."""
        result = SplitResult(
            status='success',
            num_files=5,
            metadata={'total_pages': 100, 'mode': 'pages'}
        )
        assert result.metadata['total_pages'] == 100
        assert result.metadata['mode'] == 'pages'
