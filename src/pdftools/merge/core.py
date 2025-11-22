"""
Core PDF merge functionality
"""

from pathlib import Path
from typing import List, Optional
import logging
import time

from .models import MergeResult, MergeConfig
from .validators import validate_input_files
from .processors import PDFMerger
from ..core.validators import validate_output_path
from ..core.utils import generate_output_path
from ..core.exceptions import PDFNotFoundError, PDFCorruptedError, PDFProcessingError


logger = logging.getLogger('pdftools.merge')


def merge_pdfs(
    files: List[Path],
    output_path: Optional[Path] = None,
    config: Optional[MergeConfig] = None
) -> MergeResult:
    """
    Merge multiple PDF files into a single document

    Args:
        files: List of PDF file paths to merge (minimum 2)
        output_path: Output path for merged PDF.
                    If None, creates 'merged.pdf' in directory of first file.
        config: Optional configuration (bookmarks, progress callback, etc.)

    Returns:
        MergeResult: Object containing status, output path, and metadata

    Raises:
        PDFNotFoundError: If any input file doesn't exist
        InvalidParameterError: If less than 2 files provided
        PDFProcessingError: If merge fails

    Example:
        >>> from pathlib import Path
        >>> result = merge_pdfs(
        ...     files=[Path("f1.pdf"), Path("f2.pdf")],
        ...     output_path=Path("merged.pdf")
        ... )
        >>> print(result.status)
        'success'
    """
    start_time = time.time()

    # Use default config if none provided
    if config is None:
        config = MergeConfig()

    # Setup logging level
    if config.verbose:
        logger.setLevel(logging.DEBUG)

    logger.info(f"Starting PDF merge of {len(files)} files")

    try:
        # Validate input files
        validated_files = validate_input_files(files, must_exist=True)

        # Determine output path
        if output_path is None:
            output_path = generate_output_path(
                validated_files[0],
                suffix="_merged",
                extension=".pdf"
            )
        else:
            output_path = validate_output_path(
                output_path,
                create_dirs=True,
                overwrite=True
            )

        logger.info(f"Output path: {output_path}")

        # Create merger
        merger = PDFMerger()

        # Process each file
        files_processed = 0
        skipped_files = []

        for idx, file_path in enumerate(validated_files, 1):
            try:
                # Progress callback
                if config.progress_callback:
                    config.progress_callback(idx, len(validated_files))

                logger.info(f"Processing {idx}/{len(validated_files)}: {file_path.name}")

                # Add PDF to merger
                pages_added = merger.add_pdf(
                    file_path,
                    keep_bookmarks=config.keep_bookmarks
                )

                files_processed += 1
                logger.debug(f"Added {pages_added} pages from {file_path.name}")

            except PDFCorruptedError as e:
                if config.skip_on_error:
                    logger.warning(f"Skipping corrupted file: {file_path.name}")
                    skipped_files.append(str(file_path))
                else:
                    raise

        # Check if any files were successfully processed
        if files_processed == 0:
            return MergeResult(
                status="error",
                message="No files could be processed",
                skipped_files=skipped_files
            )

        # Write merged PDF
        merger.write(output_path)

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Determine status
        if skipped_files:
            status = "partial"
            message = f"Merged {files_processed} PDFs with {len(skipped_files)} files skipped"
        else:
            status = "success"
            message = f"Successfully merged {files_processed} PDFs"

        logger.info(f"Merge completed in {elapsed_time:.2f}s")

        return MergeResult(
            status=status,
            output_path=output_path,
            message=message,
            pages_merged=merger.total_pages,
            files_processed=files_processed,
            skipped_files=skipped_files,
            metadata={
                'elapsed_time': elapsed_time,
                'keep_bookmarks': config.keep_bookmarks,
            }
        )

    except (PDFNotFoundError, PDFCorruptedError, PDFProcessingError) as e:
        logger.error(f"Merge failed: {e}")
        return MergeResult(
            status="error",
            message=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error during merge: {e}", exc_info=True)
        return MergeResult(
            status="error",
            message=f"Unexpected error: {e}"
        )
