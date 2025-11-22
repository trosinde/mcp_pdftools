"""
PDF merge processing logic
"""

from pathlib import Path
from typing import Protocol, Optional
import logging

from PyPDF2 import PdfReader, PdfWriter

from ..core.exceptions import PDFProcessingError, PDFCorruptedError


logger = logging.getLogger('pdftools.merge')


class PDFReaderInterface(Protocol):
    """Interface for PDF readers (enables dependency injection and mocking)"""

    def read(self, path: Path) -> PdfReader:
        """Read a PDF file and return a PdfReader object"""
        ...


class DefaultPDFReader:
    """Default PDF reader implementation using PyPDF2"""

    def read(self, path: Path) -> PdfReader:
        """
        Read a PDF file using PyPDF2

        Args:
            path: Path to PDF file

        Returns:
            PdfReader object

        Raises:
            PDFCorruptedError: If PDF is corrupted or invalid
        """
        try:
            return PdfReader(str(path))
        except Exception as e:
            raise PDFCorruptedError(str(path), str(e))


class PDFMerger:
    """
    Handles the actual PDF merging logic

    This class uses dependency injection for the PDF reader,
    making it easily testable with mocks.
    """

    def __init__(self, reader: Optional[PDFReaderInterface] = None):
        """
        Initialize merger with optional PDF reader

        Args:
            reader: PDF reader implementation (for DI/testing).
                   If None, uses DefaultPDFReader
        """
        self.reader = reader or DefaultPDFReader()
        self.writer = PdfWriter()
        self.total_pages = 0

    def add_pdf(
        self,
        path: Path,
        keep_bookmarks: bool = True
    ) -> int:
        """
        Add a PDF file to the merge queue

        Args:
            path: Path to PDF file
            keep_bookmarks: Whether to preserve bookmarks

        Returns:
            Number of pages added

        Raises:
            PDFCorruptedError: If PDF cannot be read
        """
        logger.debug(f"Adding PDF: {path}")

        pdf_reader = self.reader.read(path)
        pages_added = 0

        # Add all pages
        for page in pdf_reader.pages:
            self.writer.add_page(page)
            pages_added += 1

        self.total_pages += pages_added
        logger.debug(f"Added {pages_added} pages from {path.name}")

        # Add bookmarks if requested
        if keep_bookmarks and hasattr(pdf_reader, 'outline') and pdf_reader.outline:
            try:
                self._add_bookmarks(pdf_reader.outline, path.name)
            except Exception as e:
                logger.warning(f"Could not add bookmarks from {path.name}: {e}")

        return pages_added

    def write(self, output_path: Path) -> None:
        """
        Write merged PDF to file

        Args:
            output_path: Destination path

        Raises:
            PDFProcessingError: If write fails
        """
        try:
            logger.debug(f"Writing merged PDF to: {output_path}")
            with open(output_path, 'wb') as output_file:
                self.writer.write(output_file)
            logger.info(f"Successfully wrote merged PDF: {output_path}")
        except Exception as e:
            raise PDFProcessingError(f"Failed to write merged PDF: {e}")

    def _add_bookmarks(self, outline, source_name: str) -> None:
        """
        Add bookmarks from source PDF

        Args:
            outline: Outline/bookmarks from source PDF
            source_name: Name of source file (for logging)

        Note: This is a simplified implementation.
              Full bookmark preservation with correct page offsets
              would require more complex logic.
        """
        # TODO: Implement full bookmark support with page offset tracking
        # For now, just log that bookmarks were found
        logger.debug(f"Found bookmarks in {source_name}, but full preservation not yet implemented")
        pass
