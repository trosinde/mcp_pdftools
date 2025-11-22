"""
Unit tests for merge models
"""

import pytest
from pathlib import Path

from pdftools.merge.models import MergeConfig, MergeResult


class TestMergeConfig:
    """Tests for MergeConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = MergeConfig()

        assert config.keep_bookmarks is True
        assert config.add_toc is False
        assert config.skip_on_error is False
        assert config.progress_callback is None
        assert config.verbose is False

    def test_custom_config(self):
        """Test custom configuration"""
        callback = lambda x, y: None

        config = MergeConfig(
            keep_bookmarks=False,
            add_toc=True,
            skip_on_error=True,
            progress_callback=callback,
            verbose=True
        )

        assert config.keep_bookmarks is False
        assert config.add_toc is True
        assert config.skip_on_error is True
        assert config.progress_callback is callback
        assert config.verbose is True


class TestMergeResult:
    """Tests for MergeResult dataclass"""

    def test_successful_result(self):
        """Test successful merge result"""
        result = MergeResult(
            status='success',
            output_path=Path('merged.pdf'),
            message='Success',
            pages_merged=20,
            files_processed=2
        )

        assert result.success is True
        assert result.status == 'success'
        assert result.output_path == Path('merged.pdf')
        assert result.pages_merged == 20
        assert result.files_processed == 2
        assert result.skipped_files == []

    def test_error_result(self):
        """Test error merge result"""
        result = MergeResult(
            status='error',
            message='Failed'
        )

        assert result.success is False
        assert result.status == 'error'
        assert result.output_path is None

    def test_partial_result(self):
        """Test partial success result"""
        result = MergeResult(
            status='partial',
            output_path=Path('merged.pdf'),
            message='Partial success',
            pages_merged=10,
            files_processed=1,
            skipped_files=['corrupted.pdf']
        )

        assert result.success is False  # partial is not full success
        assert result.status == 'partial'
        assert len(result.skipped_files) == 1

    def test_metadata(self):
        """Test metadata dictionary"""
        result = MergeResult(
            status='success',
            metadata={'elapsed_time': 1.5, 'custom': 'value'}
        )

        assert 'elapsed_time' in result.metadata
        assert result.metadata['elapsed_time'] == 1.5
        assert result.metadata['custom'] == 'value'
