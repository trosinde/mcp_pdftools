"""Text extraction implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from PyPDF2 import PdfReader

from .models import ExtractionConfig, ExtractionResult, PageText


class BaseExtractor(ABC):
    """Abstract base class for text extractors."""

    def __init__(self, config: ExtractionConfig):
        """Initialize extractor with configuration."""
        self.config = config
        self.reader: Optional[PdfReader] = None

    @abstractmethod
    def extract(self) -> ExtractionResult:
        """
        Extract text from PDF.

        Returns:
            ExtractionResult with extracted text
        """
        pass

    def _open_pdf(self) -> PdfReader:
        """Open PDF file for reading."""
        return PdfReader(self.config.input_path)

    def _extract_page_text(self, page, page_num: int) -> PageText:
        """
        Extract text from a single page.

        Args:
            page: PyPDF2 page object
            page_num: Page number (1-based)

        Returns:
            PageText object
        """
        text = page.extract_text()

        metadata = {}
        if self.config.include_metadata:
            # Extract page-level metadata if available
            if hasattr(page, 'mediabox'):
                metadata['width'] = float(page.mediabox.width)
                metadata['height'] = float(page.mediabox.height)

        return PageText(
            page_num=page_num,
            text=text,
            char_count=len(text),
            metadata=metadata
        )

    def _show_progress(self, current: int, total: int, message: str = "Extracting"):
        """Display progress indicator."""
        if self.config.verbose:
            percent = (current / total) * 100
            bar_length = 40
            filled = int(bar_length * current / total)
            bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)
            print(f"\r{message}: [{bar}] {current}/{total} ({percent:.1f}%)", end='', flush=True)
            if current == total:
                print()  # New line when done

    def _extract_pdf_metadata(self, reader: PdfReader) -> dict:
        """Extract PDF document metadata."""
        metadata = {}
        if self.config.include_metadata and reader.metadata:
            for key, value in reader.metadata.items():
                # Remove leading '/' from keys
                clean_key = key.lstrip('/')
                metadata[clean_key] = str(value)
        return metadata


class SimpleExtractor(BaseExtractor):
    """Simple text extraction (all text concatenated)."""

    def extract(self) -> ExtractionResult:
        """Extract all text as single string."""
        reader = self._open_pdf()
        pages_data = []
        all_text = []

        # Determine which pages to extract
        if self.config.pages:
            page_nums = self.config.pages
            total = len(page_nums)
        else:
            total = len(reader.pages)
            page_nums = range(1, total + 1)

        for idx, page_num in enumerate(page_nums, 1):
            # Convert to 0-based for PyPDF2
            page_idx = page_num - 1
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num)
            pages_data.append(page_text)
            all_text.append(page_text.text)

            self._show_progress(idx, total, "Extracting text")

        combined_text = "\n\n".join(all_text)
        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            text=combined_text,
            pages=pages_data,
            metadata=metadata,
            char_count=len(combined_text)
        )


class LayoutExtractor(BaseExtractor):
    """Layout-preserving text extraction."""

    def extract(self) -> ExtractionResult:
        """Extract text while preserving layout."""
        reader = self._open_pdf()
        pages_data = []
        all_text = []

        if self.config.pages:
            page_nums = self.config.pages
            total = len(page_nums)
        else:
            total = len(reader.pages)
            page_nums = range(1, total + 1)

        for idx, page_num in enumerate(page_nums, 1):
            page_idx = page_num - 1
            page = reader.pages[page_idx]

            # Use layout mode for extraction (PyPDF2 default preserves layout better)
            page_text = self._extract_page_text(page, page_num)
            pages_data.append(page_text)
            all_text.append(page_text.text)

            self._show_progress(idx, total, "Extracting text (layout mode)")

        # Preserve page breaks with form feed
        combined_text = "\f\n".join(all_text)
        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            text=combined_text,
            pages=pages_data,
            metadata=metadata,
            char_count=len(combined_text)
        )


class PerPageExtractor(BaseExtractor):
    """Extract text to separate file per page."""

    def extract(self) -> ExtractionResult:
        """Extract text with one file per page."""
        reader = self._open_pdf()
        pages_data = []

        if self.config.pages:
            page_nums = self.config.pages
            total = len(page_nums)
        else:
            total = len(reader.pages)
            page_nums = range(1, total + 1)

        # Ensure output directory exists
        output_dir = self.config.output_path or Path(".")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get base name for files
        base_name = self.config.input_path.stem

        for idx, page_num in enumerate(page_nums, 1):
            page_idx = page_num - 1
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num)
            pages_data.append(page_text)

            # Write individual file
            output_file = output_dir / f"{base_name}_page_{page_num:03d}.txt"
            output_file.write_text(page_text.text, encoding=self.config.encoding)

            self._show_progress(idx, total, "Extracting pages")

        metadata = self._extract_pdf_metadata(reader)

        return ExtractionResult(
            status="success",
            pages=pages_data,
            metadata=metadata,
            message=f"Extracted {len(pages_data)} pages to {output_dir}"
        )


class StructuredExtractor(BaseExtractor):
    """Extract text with structure and metadata."""

    def extract(self) -> ExtractionResult:
        """Extract text as structured data."""
        reader = self._open_pdf()
        pages_data = []

        if self.config.pages:
            page_nums = self.config.pages
            total = len(page_nums)
        else:
            total = len(reader.pages)
            page_nums = range(1, total + 1)

        for idx, page_num in enumerate(page_nums, 1):
            page_idx = page_num - 1
            page = reader.pages[page_idx]

            page_text = self._extract_page_text(page, page_num)
            pages_data.append(page_text)

            self._show_progress(idx, total, "Extracting structured data")

        metadata = self._extract_pdf_metadata(reader)
        metadata['total_pages'] = len(reader.pages)
        metadata['extracted_pages'] = len(pages_data)

        return ExtractionResult(
            status="success",
            pages=pages_data,
            metadata=metadata
        )
