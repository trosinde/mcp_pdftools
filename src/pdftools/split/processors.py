"""
PDF split processors for different split modes.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from pypdf import PdfReader, PdfWriter

from pdftools.core.exceptions import PDFProcessingError, ValidationError
from pdftools.split.models import SplitMode, SplitResult
from pdftools.split.validators import validate_ranges, validate_pages


logger = logging.getLogger('pdftools.split.processors')


def generate_output_filename(
    prefix: str,
    mode: SplitMode,
    page_num: Optional[int] = None,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    part_num: Optional[int] = None
) -> str:
    """
    Generate output filename based on split mode.

    Args:
        prefix: File prefix (usually original filename)
        mode: Split mode
        page_num: Page number (for PAGES or SPECIFIC_PAGES mode)
        start_page, end_page: Range (for RANGES mode)
        part_num: Part number (for PARTS mode)

    Returns:
        Filename string

    Example:
        >>> generate_output_filename("doc", SplitMode.PAGES, page_num=1)
        'doc_page_001.pdf'

        >>> generate_output_filename("doc", SplitMode.RANGES, start_page=1, end_page=5)
        'doc_pages_001-005.pdf'
    """
    if mode == SplitMode.PAGES or mode == SplitMode.SPECIFIC_PAGES:
        if page_num is None:
            raise ValueError("page_num required for PAGES or SPECIFIC_PAGES mode")
        return f"{prefix}_page_{page_num:03d}.pdf"

    elif mode == SplitMode.RANGES:
        if start_page is None or end_page is None:
            raise ValueError("start_page and end_page required for RANGES mode")
        return f"{prefix}_pages_{start_page:03d}-{end_page:03d}.pdf"

    elif mode == SplitMode.PARTS:
        if part_num is None:
            raise ValueError("part_num required for PARTS mode")
        return f"{prefix}_part_{part_num}.pdf"

    else:
        raise ValueError(f"Unknown split mode: {mode}")


def calculate_parts_ranges(
    total_pages: int,
    num_parts: int
) -> list[tuple[int, int]]:
    """
    Calculate page ranges for splitting into N equal parts.

    Args:
        total_pages: Total number of pages in PDF
        num_parts: Desired number of parts

    Returns:
        List of (start, end) tuples (1-indexed, inclusive)

    Raises:
        ValidationError: If num_parts is invalid

    Example:
        >>> calculate_parts_ranges(100, 5)
        [(1, 20), (21, 40), (41, 60), (61, 80), (81, 100)]

        >>> calculate_parts_ranges(102, 5)
        [(1, 21), (22, 42), (43, 63), (64, 84), (85, 102)]
    """
    if num_parts < 1:
        raise ValidationError(f"num_parts must be >= 1, got {num_parts}")

    if num_parts > total_pages:
        raise ValidationError(
            f"num_parts ({num_parts}) cannot be greater than total_pages ({total_pages})"
        )

    # Calculate pages per part
    pages_per_part = total_pages // num_parts
    remainder = total_pages % num_parts

    ranges = []
    current_page = 1

    for part_num in range(num_parts):
        # Add extra page to first 'remainder' parts
        part_size = pages_per_part + (1 if part_num < remainder else 0)

        start = current_page
        end = current_page + part_size - 1

        ranges.append((start, end))
        current_page = end + 1

    return ranges


class BaseSplitter(ABC):
    """Abstract base class for PDF splitters."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        verbose: bool = False
    ):
        """
        Initialize splitter.

        Args:
            input_path: Path to input PDF
            output_dir: Directory for output files
            prefix: Prefix for output filenames
            verbose: Enable verbose logging
        """
        self.input_path = input_path
        self.output_dir = output_dir
        self.prefix = prefix
        self.verbose = verbose
        self.logger = logging.getLogger(f'pdftools.split.{self.__class__.__name__}')

    @abstractmethod
    def split(self) -> SplitResult:
        """
        Perform the split operation.

        Returns:
            SplitResult object

        Raises:
            PDFProcessingError: If splitting fails
        """
        pass

    def _create_single_page_pdf(
        self,
        pdf_reader: PdfReader,
        page_num: int,
        output_path: Path
    ) -> None:
        """
        Helper: Extract single page to new PDF.

        Args:
            pdf_reader: PyPDF PdfReader object
            page_num: Page number to extract (0-indexed)
            output_path: Path for output PDF
        """
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf_reader.pages[page_num])

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

    def _create_multi_page_pdf(
        self,
        pdf_reader: PdfReader,
        start_page: int,
        end_page: int,
        output_path: Path
    ) -> None:
        """
        Helper: Extract page range to new PDF.

        Args:
            pdf_reader: PyPDF PdfReader object
            start_page: Start page (0-indexed, inclusive)
            end_page: End page (0-indexed, inclusive)
            output_path: Path for output PDF
        """
        pdf_writer = PdfWriter()

        for page_num in range(start_page, end_page + 1):
            pdf_writer.add_page(pdf_reader.pages[page_num])

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

    def _show_progress(self, current: int, total: int, message: str = "Splitting") -> None:
        """
        Display progress in CLI (only if verbose).

        Args:
            current: Current progress
            total: Total items
            message: Progress message
        """
        if self.verbose:
            percent = int((current / total) * 100)
            bar_length = 20
            filled = int((current / total) * bar_length)
            bar = '=' * filled + '>' + ' ' * (bar_length - filled - 1)

            print(f"\r{message}: [{bar}] {current}/{total} ({percent}%)", end='', flush=True)

            # Newline at 100%
            if current == total:
                print()


class PagesSplitter(BaseSplitter):
    """Splits PDF into individual pages (one page per file)."""

    def split(self) -> SplitResult:
        """
        Split PDF into individual pages.

        Returns:
            SplitResult with num_files = total_pages

        Raises:
            PDFProcessingError: If PDF cannot be read
        """
        output_files = []

        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

                for page_num in range(total_pages):
                    output_filename = generate_output_filename(
                        self.prefix,
                        SplitMode.PAGES,
                        page_num=page_num + 1  # 1-indexed for filename
                    )
                    output_path = self.output_dir / output_filename

                    self._create_single_page_pdf(pdf_reader, page_num, output_path)
                    output_files.append(output_path)

                    # Progress
                    self._show_progress(page_num + 1, total_pages, "Splitting pages")

                    if self.verbose:
                        self.logger.info(f"Created: {output_filename}")

            return SplitResult(
                status='success',
                num_files=len(output_files),
                output_files=output_files,
                message=f"Successfully split into {len(output_files)} pages",
                metadata={'total_pages': total_pages, 'mode': 'pages'}
            )

        except Exception as e:
            self.logger.error(f"Failed to split PDF: {e}")
            raise PDFProcessingError(f"Failed to split PDF: {e}") from e


class RangesSplitter(BaseSplitter):
    """Splits PDF by user-defined page ranges."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        ranges: list[tuple[int, int]],
        verbose: bool = False
    ):
        super().__init__(input_path, output_dir, prefix, verbose)
        self.ranges = ranges

    def split(self) -> SplitResult:
        """
        Split PDF by ranges.

        Returns:
            SplitResult with num_files = len(ranges)

        Raises:
            ValidationError: If ranges are invalid
            PDFProcessingError: If PDF cannot be read
        """
        output_files = []

        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

                # Validate ranges
                validate_ranges(self.ranges, total_pages, allow_overlap=True)

                # Process each range
                for idx, (start, end) in enumerate(self.ranges):
                    output_filename = generate_output_filename(
                        self.prefix,
                        SplitMode.RANGES,
                        start_page=start,
                        end_page=end
                    )
                    output_path = self.output_dir / output_filename

                    # Create PDF with pages in range (convert to 0-indexed)
                    self._create_multi_page_pdf(
                        pdf_reader,
                        start - 1,  # Convert to 0-indexed
                        end - 1,    # Convert to 0-indexed
                        output_path
                    )

                    output_files.append(output_path)

                    # Progress
                    self._show_progress(idx + 1, len(self.ranges), "Splitting ranges")

                    if self.verbose:
                        self.logger.info(f"Created: {output_filename} (pages {start}-{end})")

            return SplitResult(
                status='success',
                num_files=len(output_files),
                output_files=output_files,
                message=f"Successfully split into {len(output_files)} ranges",
                metadata={
                    'total_pages': total_pages,
                    'mode': 'ranges',
                    'ranges': self.ranges
                }
            )

        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            self.logger.error(f"Failed to split PDF by ranges: {e}")
            raise PDFProcessingError(f"Failed to split PDF by ranges: {e}") from e


class PartsSplitter(BaseSplitter):
    """Splits PDF into N equal parts."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        num_parts: int,
        verbose: bool = False
    ):
        super().__init__(input_path, output_dir, prefix, verbose)
        self.num_parts = num_parts

    def split(self) -> SplitResult:
        """
        Split PDF into N equal parts.

        Returns:
            SplitResult with num_files = num_parts

        Raises:
            ValidationError: If num_parts is invalid
            PDFProcessingError: If PDF cannot be read
        """
        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

                # Calculate ranges automatically
                ranges = calculate_parts_ranges(total_pages, self.num_parts)

                if self.verbose:
                    self.logger.info(
                        f"Calculated {len(ranges)} parts: {ranges}"
                    )

                # Delegate to RangesSplitter with calculated ranges
                ranges_splitter = RangesSplitter(
                    self.input_path,
                    self.output_dir,
                    self.prefix,
                    ranges,
                    self.verbose
                )

                result = ranges_splitter.split()

                # Update metadata for parts mode
                result.metadata['mode'] = 'parts'
                result.metadata['num_parts'] = self.num_parts
                result.message = f"Successfully split into {self.num_parts} equal parts"

                return result

        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            self.logger.error(f"Failed to split PDF into parts: {e}")
            raise PDFProcessingError(f"Failed to split PDF into parts: {e}") from e


class SpecificPagesSplitter(BaseSplitter):
    """Extracts specific pages to separate files."""

    def __init__(
        self,
        input_path: Path,
        output_dir: Path,
        prefix: str,
        pages: list[int],
        verbose: bool = False
    ):
        super().__init__(input_path, output_dir, prefix, verbose)
        self.pages = pages

    def split(self) -> SplitResult:
        """
        Extract specific pages.

        Returns:
            SplitResult with num_files = len(pages)

        Raises:
            ValidationError: If page numbers are invalid
            PDFProcessingError: If PDF cannot be read
        """
        output_files = []

        try:
            with open(self.input_path, 'rb') as pdf_file:
                pdf_reader = PdfReader(pdf_file)
                total_pages = len(pdf_reader.pages)

                # Validate pages
                validate_pages(self.pages, total_pages)

                # Extract each page
                for idx, page_num in enumerate(self.pages):
                    output_filename = generate_output_filename(
                        self.prefix,
                        SplitMode.SPECIFIC_PAGES,
                        page_num=page_num
                    )
                    output_path = self.output_dir / output_filename

                    # Create PDF with single page (convert to 0-indexed)
                    self._create_single_page_pdf(
                        pdf_reader,
                        page_num - 1,
                        output_path
                    )

                    output_files.append(output_path)

                    # Progress
                    self._show_progress(idx + 1, len(self.pages), "Extracting pages")

                    if self.verbose:
                        self.logger.info(f"Created: {output_filename} (page {page_num})")

            return SplitResult(
                status='success',
                num_files=len(output_files),
                output_files=output_files,
                message=f"Successfully extracted {len(output_files)} pages",
                metadata={
                    'total_pages': total_pages,
                    'mode': 'specific_pages',
                    'pages': self.pages
                }
            )

        except ValidationError:
            raise  # Re-raise validation errors
        except Exception as e:
            self.logger.error(f"Failed to extract pages: {e}")
            raise PDFProcessingError(f"Failed to extract pages: {e}") from e
