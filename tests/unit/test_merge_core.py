"""
Unit tests for merge core functionality
"""

import pytest
from pathlib import Path

from pdftools.merge.core import merge_pdfs
from pdftools.merge.models import MergeConfig, MergeResult
from pdftools.core.exceptions import InvalidParameterError


class TestMergePDFs:
    """Tests for merge_pdfs function"""

    def test_merge_two_simple_pdfs(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test merging two simple PDFs"""
        output = temp_dir / "merged.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )

        assert result.success
        assert result.status == 'success'
        assert result.output_path == output
        assert output.exists()
        assert result.files_processed == 2
        assert result.pages_merged > 0
        assert len(result.skipped_files) == 0

    def test_merge_with_default_output_path(self, pdf_simple_text, pdf_multipage):
        """Test merge with auto-generated output path"""
        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage]
        )

        assert result.success
        assert result.output_path is not None
        assert result.output_path.exists()
        assert '_merged.pdf' in result.output_path.name

    def test_merge_with_custom_config(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test merge with custom configuration"""
        output = temp_dir / "merged.pdf"
        config = MergeConfig(
            keep_bookmarks=False,
            verbose=True
        )

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output,
            config=config
        )

        assert result.success
        assert 'keep_bookmarks' in result.metadata
        assert result.metadata['keep_bookmarks'] is False

    def test_merge_multiple_pdfs(self, multiple_pdfs, temp_dir):
        """Test merging multiple PDFs"""
        output = temp_dir / "merged.pdf"

        result = merge_pdfs(
            files=multiple_pdfs,
            output_path=output
        )

        assert result.success
        assert result.files_processed == len(multiple_pdfs)

    def test_merge_with_insufficient_files(self, pdf_simple_text):
        """Test that merging single file fails"""
        result = merge_pdfs(files=[pdf_simple_text])

        assert not result.success
        assert result.status == 'error'
        assert 'At least 2' in result.message

    def test_merge_with_nonexistent_file(self, pdf_simple_text, non_existent_pdf, temp_dir):
        """Test merge with non-existent file"""
        output = temp_dir / "merged.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, non_existent_pdf],
            output_path=output
        )

        assert not result.success
        assert result.status == 'error'

    def test_merge_with_skip_on_error(self, pdf_simple_text, invalid_pdf, temp_dir):
        """Test merge with skip_on_error enabled"""
        output = temp_dir / "merged.pdf"
        config = MergeConfig(skip_on_error=True)

        result = merge_pdfs(
            files=[pdf_simple_text, invalid_pdf],
            output_path=output,
            config=config
        )

        # Should have partial success
        assert result.status in ['success', 'partial']
        assert result.files_processed >= 1

    def test_merge_with_progress_callback(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test merge with progress callback"""
        output = temp_dir / "merged.pdf"
        progress_calls = []

        def progress_callback(current, total):
            progress_calls.append((current, total))

        config = MergeConfig(progress_callback=progress_callback)

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output,
            config=config
        )

        assert result.success
        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == progress_calls[-1][1]  # Last call should be 100%

    def test_merge_measures_elapsed_time(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test that merge measures elapsed time"""
        output = temp_dir / "merged.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )

        assert result.success
        assert 'elapsed_time' in result.metadata
        assert result.metadata['elapsed_time'] > 0
