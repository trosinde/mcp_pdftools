"""
Unit tests for merge processors
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock

from pdftools.merge.processors import PDFMerger, DefaultPDFReader
from pdftools.core.exceptions import PDFCorruptedError


class MockPDFReader:
    """Mock PDF reader for testing"""

    def __init__(self, num_pages=10, has_outline=False):
        self.num_pages = num_pages
        self.has_outline = has_outline
        self.read_called = False

    def read(self, path: Path):
        """Mock read method"""
        self.read_called = True

        # Create mock PdfReader
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock() for _ in range(self.num_pages)]

        if self.has_outline:
            mock_reader.outline = ['bookmark1', 'bookmark2']
        else:
            mock_reader.outline = None

        return mock_reader


class TestDefaultPDFReader:
    """Tests for DefaultPDFReader"""

    def test_read_valid_pdf(self, pdf_simple_text):
        """Test reading a valid PDF"""
        reader = DefaultPDFReader()
        pdf_reader = reader.read(pdf_simple_text)

        assert pdf_reader is not None
        assert hasattr(pdf_reader, 'pages')
        assert len(pdf_reader.pages) > 0

    def test_read_invalid_pdf_raises_error(self, invalid_pdf):
        """Test that invalid PDF raises PDFCorruptedError"""
        reader = DefaultPDFReader()

        with pytest.raises(PDFCorruptedError):
            reader.read(invalid_pdf)


class TestPDFMerger:
    """Tests for PDFMerger class"""

    def test_init_with_default_reader(self):
        """Test initialization with default reader"""
        merger = PDFMerger()

        assert merger.reader is not None
        assert isinstance(merger.reader, DefaultPDFReader)
        assert merger.total_pages == 0

    def test_init_with_custom_reader(self):
        """Test initialization with custom reader (DI)"""
        mock_reader = MockPDFReader()
        merger = PDFMerger(reader=mock_reader)

        assert merger.reader is mock_reader

    def test_add_pdf_with_mock_reader(self, temp_dir):
        """Test adding PDF with mock reader"""
        mock_reader = MockPDFReader(num_pages=5)
        merger = PDFMerger(reader=mock_reader)

        test_file = temp_dir / "test.pdf"
        test_file.touch()  # Create empty file

        pages_added = merger.add_pdf(test_file, keep_bookmarks=False)

        assert mock_reader.read_called
        assert pages_added == 5
        assert merger.total_pages == 5

    def test_add_multiple_pdfs(self, temp_dir):
        """Test adding multiple PDFs"""
        mock_reader = MockPDFReader(num_pages=10)
        merger = PDFMerger(reader=mock_reader)

        for i in range(3):
            test_file = temp_dir / f"test{i}.pdf"
            test_file.touch()
            merger.add_pdf(test_file, keep_bookmarks=False)

        assert merger.total_pages == 30  # 3 files × 10 pages

    def test_add_pdf_with_bookmarks(self, temp_dir):
        """Test adding PDF with bookmarks"""
        mock_reader = MockPDFReader(num_pages=5, has_outline=True)
        merger = PDFMerger(reader=mock_reader)

        test_file = temp_dir / "test.pdf"
        test_file.touch()

        # Should not raise even with bookmarks
        pages_added = merger.add_pdf(test_file, keep_bookmarks=True)
        assert pages_added == 5

    def test_write_to_file(self, temp_dir):
        """Test writing merged PDF to file"""
        mock_reader = MockPDFReader(num_pages=5)
        merger = PDFMerger(reader=mock_reader)

        # Add a PDF
        test_input = temp_dir / "input.pdf"
        test_input.touch()
        merger.add_pdf(test_input, keep_bookmarks=False)

        # Write output
        output_file = temp_dir / "output.pdf"
        merger.write(output_file)

        assert output_file.exists()
