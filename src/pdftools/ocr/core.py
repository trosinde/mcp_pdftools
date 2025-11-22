"""
Core OCR processing logic
"""

from pathlib import Path
from typing import Optional, List, Union
import json
import time
import logging

from pdftools.ocr.models import OCRConfig, OCRResult, OCRLanguage, OutputMode
from pdftools.ocr.validators import (
    validate_pdf,
    validate_language,
    check_tesseract,
    check_language_available,
)
from pdftools.ocr.ocr_engine import TesseractEngine
from pdftools.core.exceptions import (
    PDFNotFoundError,
    OCRProcessingError,
)

logger = logging.getLogger(__name__)


def perform_ocr(
    input_path: Path,
    output_path: Optional[Path] = None,
    language: Union[OCRLanguage, List[OCRLanguage], str, List[str]] = OCRLanguage.GERMAN,
    output_mode: OutputMode = OutputMode.TXT,
    config: Optional[OCRConfig] = None
) -> OCRResult:
    """
    Perform OCR on a PDF document.

    Args:
        input_path: Path to input PDF file
        output_path: Output path. If None, creates '{filename}_ocr.{ext}'
        language: OCR language(s) - single or multiple (default: German)
        output_mode: Output format (TXT, PDF, JSON) (default: TXT)
        config: Optional configuration (pages, DPI, etc.)

    Returns:
        OCRResult: Object containing status, output path, and metadata

    Raises:
        PDFNotFoundError: If input file doesn't exist
        TesseractNotFoundError: If Tesseract is not installed
        LanguageNotAvailableError: If language data not found
        OCRProcessingError: If OCR fails

    Example:
        >>> result = perform_ocr(
        ...     input_path=Path("scan.pdf"),
        ...     output_path=Path("output.txt"),
        ...     language=OCRLanguage.GERMAN
        ... )
        >>> print(result.status)
        'success'
    """
    start_time = time.time()

    try:
        # Use default config if not provided
        if config is None:
            config = OCRConfig()

        # Validate input
        input_path = validate_pdf(input_path)

        # Check Tesseract availability
        check_tesseract()

        # Validate and normalize language
        languages = validate_language(language)
        language_code = '+'.join(languages)  # Tesseract format for multiple languages

        # Check language availability
        for lang in languages:
            check_language_available(lang)

        # Generate output path if not provided
        if output_path is None:
            output_path = _generate_output_path(input_path, output_mode)

        # Log start
        logger.info(f"Starting OCR: {input_path} -> {output_path}")
        logger.info(f"Language: {language_code}, Mode: {output_mode.value}")

        # Initialize OCR engine
        engine = TesseractEngine()

        # Convert PDF to images
        logger.info("Converting PDF to images...")
        images = engine.pdf_to_images(
            input_path,
            dpi=config.dpi,
            pages=config.pages
        )

        total_pages = len(images)
        logger.info(f"Processing {total_pages} pages")

        # Process each page
        ocr_results = []
        for i, image in enumerate(images, start=1):
            try:
                if config.verbose:
                    logger.info(f"Processing page {i}/{total_pages}...")

                # Progress callback
                if config.progress_callback:
                    config.progress_callback(i, total_pages)

                # Process image
                result = engine.process_image(
                    image,
                    language_code,
                    config.tesseract_config
                )

                ocr_results.append({
                    'page_number': i,
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'word_count': len(result['text'].split())
                })

                # Log low confidence warning
                if result['confidence'] < 0.7:
                    logger.warning(
                        f"Low OCR confidence on page {i}: {result['confidence']:.2%}"
                    )

                # Clean up image
                image.close()

            except Exception as e:
                logger.error(f"Failed to process page {i}: {e}")
                if not config.progress_callback:
                    raise OCRProcessingError(f"OCR failed on page {i}: {e}") from e

        # Write output
        logger.info(f"Writing output to {output_path}...")
        _write_output(ocr_results, output_path, output_mode, input_path)

        # Calculate metadata
        processing_time = time.time() - start_time
        avg_confidence = sum(r['confidence'] for r in ocr_results) / len(ocr_results)
        total_words = sum(r['word_count'] for r in ocr_results)

        # Create result
        result = OCRResult(
            status='success',
            output_path=output_path,
            message=f"OCR completed successfully for {total_pages} pages",
            pages_processed=total_pages,
            total_pages=total_pages,
            metadata={
                'avg_confidence': avg_confidence,
                'processing_time_seconds': processing_time,
                'total_words': total_words,
                'language': language_code,
                'dpi': config.dpi,
            }
        )

        logger.info(
            f"OCR completed: {total_pages} pages in {processing_time:.2f}s "
            f"(avg confidence: {avg_confidence:.2%})"
        )

        return result

    except (PDFNotFoundError, OCRProcessingError):
        raise
    except Exception as e:
        logger.error(f"OCR processing failed: {e}", exc_info=True)
        return OCRResult(
            status='error',
            message=f"OCR failed: {str(e)}",
            total_pages=0,
            pages_processed=0
        )


def _generate_output_path(input_path: Path, output_mode: OutputMode) -> Path:
    """
    Generate output path based on input path and output mode.

    Args:
        input_path: Input PDF path
        output_mode: Output format mode

    Returns:
        Path: Generated output path
    """
    base_name = input_path.stem
    extension = output_mode.value
    output_path = input_path.parent / f"{base_name}_ocr.{extension}"

    logger.debug(f"Generated output path: {output_path}")
    return output_path


def _write_output(
    ocr_results: List[dict],
    output_path: Path,
    output_mode: OutputMode,
    input_path: Path
) -> None:
    """
    Write OCR results to output file.

    Args:
        ocr_results: List of OCR results per page
        output_path: Output file path
        output_mode: Output format mode
        input_path: Original input PDF path

    Raises:
        OCRProcessingError: If writing fails
    """
    try:
        if output_mode == OutputMode.TXT:
            _write_txt_output(ocr_results, output_path)
        elif output_mode == OutputMode.JSON:
            _write_json_output(ocr_results, output_path, input_path)
        elif output_mode == OutputMode.PDF:
            _write_pdf_output(ocr_results, output_path, input_path)
        else:
            raise OCRProcessingError(f"Unsupported output mode: {output_mode}")

    except Exception as e:
        logger.error(f"Failed to write output: {e}")
        raise OCRProcessingError(f"Failed to write output: {e}") from e


def _write_txt_output(ocr_results: List[dict], output_path: Path) -> None:
    """Write OCR results as plain text file"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for i, result in enumerate(ocr_results, start=1):
            f.write(f"Page {i}:\n")
            f.write(result['text'])
            f.write("\n\f\n")  # Form feed separator


def _write_json_output(
    ocr_results: List[dict],
    output_path: Path,
    input_path: Path
) -> None:
    """Write OCR results as JSON file"""
    output_data = {
        'file': str(input_path),
        'total_pages': len(ocr_results),
        'processed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'pages': ocr_results,
        'metadata': {
            'avg_confidence': sum(r['confidence'] for r in ocr_results) / len(ocr_results),
            'total_words': sum(r['word_count'] for r in ocr_results),
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def _write_pdf_output(
    ocr_results: List[dict],
    output_path: Path,
    input_path: Path
) -> None:
    """
    Write OCR results as searchable PDF.

    Note: This is a simplified implementation that creates a new PDF with text.
    A full implementation would overlay text on the original scanned images.
    """
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4

        # Create PDF with text
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4

        for result in ocr_results:
            # Write text on page
            text_object = c.beginText(50, height - 50)
            text_object.setFont("Helvetica", 10)

            # Add text line by line
            for line in result['text'].split('\n'):
                if line.strip():
                    text_object.textLine(line)

            c.drawText(text_object)
            c.showPage()

        c.save()

    except ImportError:
        # Fallback: Write as TXT if reportlab not available
        logger.warning("reportlab not available, falling back to TXT output")
        txt_path = output_path.with_suffix('.txt')
        _write_txt_output(ocr_results, txt_path)
        raise OCRProcessingError(
            "PDF output requires reportlab. Install with: pip install reportlab"
        )
