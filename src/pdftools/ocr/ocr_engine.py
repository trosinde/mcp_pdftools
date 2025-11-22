"""
Tesseract OCR Engine implementation
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image
import logging

from pdftools.core.exceptions import (
    TesseractNotFoundError,
    ImageConversionError,
)

logger = logging.getLogger(__name__)


class TesseractEngine:
    """
    Tesseract OCR Engine for processing images and extracting text.

    This class provides a wrapper around pytesseract for OCR operations,
    including PDF to image conversion and text extraction.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        """
        Initialize Tesseract engine.

        Args:
            tesseract_cmd: Optional path to tesseract binary
                         (uses system default if not provided)

        Raises:
            TesseractNotFoundError: If Tesseract is not available
        """
        self.tesseract_cmd = tesseract_cmd
        self._configure_tesseract()
        self._verify_tesseract()

    def _configure_tesseract(self) -> None:
        """Configure pytesseract with custom binary path if provided"""
        if self.tesseract_cmd:
            try:
                import pytesseract
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd
                logger.info(f"Using custom Tesseract binary: {self.tesseract_cmd}")
            except ImportError as e:
                raise TesseractNotFoundError() from e

    def _verify_tesseract(self) -> None:
        """
        Verify that Tesseract is available.

        Raises:
            TesseractNotFoundError: If Tesseract is not installed or not working
        """
        try:
            import pytesseract
            version = pytesseract.get_tesseract_version()
            logger.info(f"Tesseract OCR version: {version}")
        except Exception as e:
            logger.error(f"Tesseract verification failed: {e}")
            raise TesseractNotFoundError() from e

    def process_image(
        self,
        image: Image.Image,
        language: str,
        config: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single image with OCR.

        Args:
            image: PIL Image object to process
            language: Tesseract language code (e.g., 'deu', 'eng')
            config: Optional Tesseract configuration string

        Returns:
            dict: Dictionary with 'text' and 'confidence' keys
                - text (str): Extracted text
                - confidence (float): Average confidence score (0.0 - 1.0)

        Raises:
            TesseractNotFoundError: If pytesseract is not available
        """
        try:
            import pytesseract

            # Extract text
            text = pytesseract.image_to_string(
                image,
                lang=language,
                config=config or ''
            )

            # Get detailed data for confidence calculation
            data = pytesseract.image_to_data(
                image,
                lang=language,
                config=config or '',
                output_type=pytesseract.Output.DICT
            )

            # Calculate average confidence
            confidences = [c for c in data['conf'] if c != -1]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            avg_confidence = avg_confidence / 100.0  # Normalize to 0-1

            return {
                'text': text,
                'confidence': avg_confidence
            }

        except ImportError as e:
            raise TesseractNotFoundError() from e
        except Exception as e:
            logger.error(f"OCR processing failed: {e}")
            raise

    def pdf_to_images(
        self,
        pdf_path: Path,
        dpi: int = 300,
        pages: Optional[List[int]] = None
    ) -> List[Image.Image]:
        """
        Convert PDF pages to images.

        Args:
            pdf_path: Path to PDF file
            dpi: DPI for image conversion (default: 300)
            pages: Specific pages to convert (None = all pages)

        Returns:
            List[Image.Image]: List of PIL Image objects

        Raises:
            ImageConversionError: If conversion fails
        """
        try:
            from pdf2image import convert_from_path

            logger.debug(f"Converting PDF to images: {pdf_path} (DPI: {dpi})")

            # Convert PDF to images
            if pages:
                # pdf2image uses 1-indexed pages
                images = convert_from_path(
                    pdf_path,
                    dpi=dpi,
                    first_page=min(pages),
                    last_page=max(pages)
                )
                # Filter only requested pages
                page_set = set(pages)
                images = [
                    img for i, img in enumerate(images, start=min(pages))
                    if i in page_set
                ]
            else:
                images = convert_from_path(pdf_path, dpi=dpi)

            logger.info(f"Converted {len(images)} pages to images")
            return images

        except ImportError as e:
            raise ImageConversionError(
                0,
                "pdf2image not installed. Please install pdf2image package."
            ) from e
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            raise ImageConversionError(0, str(e)) from e

    def process_pdf_page(
        self,
        pdf_path: Path,
        page_num: int,
        language: str,
        dpi: int = 300,
        config: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a single PDF page with OCR.

        Args:
            pdf_path: Path to PDF file
            page_num: Page number (1-indexed)
            language: Tesseract language code
            dpi: DPI for image conversion
            config: Optional Tesseract configuration

        Returns:
            dict: OCR result with 'text' and 'confidence'

        Raises:
            ImageConversionError: If page conversion fails
        """
        try:
            # Convert single page to image
            images = self.pdf_to_images(pdf_path, dpi=dpi, pages=[page_num])

            if not images:
                raise ImageConversionError(
                    page_num,
                    "No image generated from PDF page"
                )

            # Process image with OCR
            result = self.process_image(images[0], language, config)

            # Clean up
            images[0].close()

            return result

        except ImageConversionError:
            raise
        except Exception as e:
            logger.error(f"Failed to process PDF page {page_num}: {e}")
            raise ImageConversionError(page_num, str(e)) from e

    def get_available_languages(self) -> List[str]:
        """
        Get list of installed Tesseract languages.

        Returns:
            List[str]: List of language codes (e.g., ['deu', 'eng', 'fra'])

        Raises:
            TesseractNotFoundError: If pytesseract is not available
        """
        try:
            import pytesseract
            languages = pytesseract.get_languages(config='')
            logger.debug(f"Available languages: {languages}")
            return languages
        except ImportError as e:
            raise TesseractNotFoundError() from e
        except Exception as e:
            logger.error(f"Failed to get available languages: {e}")
            raise TesseractNotFoundError() from e
