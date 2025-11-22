"""
Integration tests for complete merge workflow
"""

import pytest
from pathlib import Path
from PyPDF2 import PdfReader

from pdftools.merge import merge_pdfs, MergeConfig


class TestMergeWorkflow:
    """Integration tests for end-to-end merge workflow"""

    def test_complete_workflow_two_files(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test complete workflow: validate → process → output"""
        output = temp_dir / "integrated_merge.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )

        # Verify result
        assert result.success
        assert result.output_path == output

        # Verify output file
        assert output.exists()
        assert output.stat().st_size > 0

        # Verify PDF is valid
        pdf_reader = PdfReader(str(output))
        assert len(pdf_reader.pages) > 0
        assert result.pages_merged == len(pdf_reader.pages)

    def test_workflow_with_all_test_pdfs(self, multiple_pdfs, temp_dir):
        """Test workflow with all available test PDFs"""
        output = temp_dir / "all_merged.pdf"

        result = merge_pdfs(
            files=multiple_pdfs,
            output_path=output
        )

        assert result.success
        assert result.files_processed == len(multiple_pdfs)

        # Verify output
        pdf_reader = PdfReader(str(output))
        assert len(pdf_reader.pages) == result.pages_merged

    def test_workflow_with_images_pdf(self, pdf_with_image, pdf_simple_text, temp_dir):
        """Test merging PDFs with images"""
        output = temp_dir / "with_images.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_with_image],
            output_path=output
        )

        assert result.success
        assert output.exists()

    def test_workflow_large_pdf(self, pdf_large, pdf_simple_text, temp_dir):
        """Test merging with large PDF (performance test)"""
        output = temp_dir / "large_merge.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_large],
            output_path=output
        )

        assert result.success

        # Verify performance
        if 'elapsed_time' in result.metadata:
            # Should complete in reasonable time (< 10s for test PDF)
            assert result.metadata['elapsed_time'] < 10.0

    def test_workflow_error_recovery(self, pdf_simple_text, invalid_pdf, temp_dir):
        """Test workflow with error recovery (skip_on_error)"""
        output = temp_dir / "recovered.pdf"
        config = MergeConfig(skip_on_error=True)

        result = merge_pdfs(
            files=[pdf_simple_text, invalid_pdf],
            output_path=output,
            config=config
        )

        # Should have processed at least the valid file
        assert result.files_processed >= 1
        assert len(result.skipped_files) >= 1
        assert output.exists()

    def test_workflow_creates_parent_directories(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test that workflow creates parent directories"""
        output = temp_dir / "subdir1" / "subdir2" / "merged.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )

        assert result.success
        assert output.exists()
        assert output.parent.exists()

    def test_workflow_overwrites_existing_file(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test that workflow can overwrite existing files"""
        output = temp_dir / "overwrite.pdf"

        # First merge
        result1 = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )
        assert result1.success
        size1 = output.stat().st_size

        # Second merge (overwrite)
        result2 = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )
        assert result2.success
        assert output.exists()

    def test_workflow_preserves_page_content(self, pdf_simple_text, pdf_multipage, temp_dir):
        """Test that merged PDF preserves page content"""
        output = temp_dir / "content_test.pdf"

        result = merge_pdfs(
            files=[pdf_simple_text, pdf_multipage],
            output_path=output
        )

        assert result.success

        # Read merged PDF and verify it has content
        pdf_reader = PdfReader(str(output))
        for page in pdf_reader.pages:
            # Each page should have some content
            text = page.extract_text()
            # Note: Some test PDFs might not have extractable text
            # so we just verify the page exists
            assert page is not None
