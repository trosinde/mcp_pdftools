"""
PDF thumbnail generation using pdf2image and Pillow
"""

import logging
from pathlib import Path
from typing import Optional, Callable

try:
    from pdf2image import convert_from_path
    from pdf2image.exceptions import (
        PDFInfoNotInstalledError,
        PDFPageCountError,
        PDFSyntaxError
    )
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False
    convert_from_path = None
    PDFInfoNotInstalledError = Exception
    PDFPageCountError = Exception
    PDFSyntaxError = Exception

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

from pdftools.core.exceptions import PDFProcessingError
from .models import ThumbnailConfig

logger = logging.getLogger('pdftools.thumbnails')


class PDFThumbnailGenerator:
    """
    Generator for creating thumbnails from PDF pages.

    Uses pdf2image for PDF→Image conversion and Pillow (PIL) for resizing.

    Attributes:
        config: Thumbnail generation configuration
    """

    def __init__(
        self,
        config: ThumbnailConfig,
        pdf_converter: Optional[Callable] = None
    ):
        """
        Initialize generator with configuration.

        Args:
            config: ThumbnailConfig object
            pdf_converter: Optional custom PDF converter (for testing)

        Raises:
            ImportError: If pdf2image or Pillow is not installed
        """
        if not PDF2IMAGE_AVAILABLE:
            raise ImportError(
                "pdf2image is not installed. Install it with: pip install pdf2image\n"
                "Also ensure poppler-utils is installed on your system."
            )

        if not PIL_AVAILABLE:
            raise ImportError(
                "Pillow is not installed. Install it with: pip install Pillow"
            )

        self.config = config
        self._pdf_converter = pdf_converter or convert_from_path

    def generate(
        self,
        pdf_path: Path,
        pages: Optional[list[int]] = None
    ) -> list[Image.Image]:
        """
        Convert PDF pages to PIL Images.

        Args:
            pdf_path: Path to PDF file
            pages: Page numbers to convert (1-indexed), None = all pages

        Returns:
            list[Image.Image]: List of PIL Image objects

        Raises:
            PDFProcessingError: If PDF conversion fails
        """
        try:
            if self.config.verbose:
                logger.info(f"Converting PDF pages: {pdf_path}")

            # Convert specified pages or all pages
            images = self._pdf_converter(
                pdf_path=str(pdf_path),
                dpi=self.config.dpi,
                fmt='ppm',  # Internal format for conversion
                first_page=min(pages) if pages else None,
                last_page=max(pages) if pages else None
            )

            if self.config.verbose:
                logger.info(f"Converted {len(images)} pages from PDF")

            # If specific pages were requested, filter them
            if pages:
                # pdf2image returns sequential pages from first_page to last_page
                # We need to map them back to the requested page numbers
                first_page = min(pages)
                requested_indices = [p - first_page for p in pages]
                images = [images[i] for i in requested_indices if i < len(images)]

            return images

        except PDFInfoNotInstalledError:
            raise PDFProcessingError(
                "poppler-utils is not installed. Please install it:\n"
                "  Ubuntu/Debian: sudo apt-get install poppler-utils\n"
                "  macOS: brew install poppler\n"
                "  Windows: Download from https://github.com/oschwartz10612/poppler-windows/releases"
            )
        except (PDFPageCountError, PDFSyntaxError) as e:
            raise PDFProcessingError(f"PDF file is corrupted or invalid: {e}")
        except Exception as e:
            raise PDFProcessingError(f"Failed to convert PDF to images: {e}")

    def resize_image(self, image: Image.Image) -> Image.Image:
        """
        Resize image to target size maintaining aspect ratio.

        The image is scaled to fit within the target size while preserving
        aspect ratio. No cropping is performed.

        Args:
            image: PIL Image object to resize

        Returns:
            Image.Image: Resized PIL Image

        Example:
            For a 1000x800 image and target size 300x300:
            - Result will be 300x240 (width-limited)

            For a 800x1000 image and target size 300x300:
            - Result will be 240x300 (height-limited)
        """
        target_width, target_height = self.config.size

        # Get original dimensions
        orig_width, orig_height = image.size

        if self.config.verbose:
            logger.debug(
                f"Resizing image from {orig_width}x{orig_height} "
                f"to fit within {target_width}x{target_height}"
            )

        # Calculate scaling factor to fit within target size
        width_ratio = target_width / orig_width
        height_ratio = target_height / orig_height
        scale_factor = min(width_ratio, height_ratio)

        # Calculate new dimensions
        new_width = int(orig_width * scale_factor)
        new_height = int(orig_height * scale_factor)

        # Resize using high-quality resampling
        resized = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        if self.config.verbose:
            logger.debug(f"Resized to {new_width}x{new_height}")

        return resized

    def save_thumbnail(
        self,
        image: Image.Image,
        output_path: Path
    ) -> None:
        """
        Save image to file with specified format and quality.

        Args:
            image: PIL Image object to save
            output_path: Path where thumbnail will be saved

        Raises:
            PDFProcessingError: If image save fails
        """
        try:
            # Determine save parameters based on format
            save_kwargs = {}

            if self.config.format.value == 'png':
                save_kwargs['format'] = 'PNG'
                save_kwargs['optimize'] = True
            elif self.config.format.value == 'jpg':
                # Convert RGBA to RGB for JPEG
                if image.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    if image.mode == 'P':
                        image = image.convert('RGBA')
                    background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                    image = background

                save_kwargs['format'] = 'JPEG'
                save_kwargs['quality'] = self.config.quality
                save_kwargs['optimize'] = True

            # Save the image
            image.save(output_path, **save_kwargs)

            if self.config.verbose:
                logger.info(f"Saved thumbnail: {output_path}")

        except Exception as e:
            raise PDFProcessingError(f"Failed to save thumbnail to {output_path}: {e}")

    def generate_and_save(
        self,
        pdf_path: Path,
        output_dir: Path,
        pages: Optional[list[int]] = None
    ) -> list[Path]:
        """
        Generate thumbnails and save them to output directory.

        This is a convenience method that combines generate(), resize_image(),
        and save_thumbnail().

        Args:
            pdf_path: Path to PDF file
            output_dir: Directory where thumbnails will be saved
            pages: Page numbers to process (1-indexed), None = all pages

        Returns:
            list[Path]: Paths to created thumbnail files

        Raises:
            PDFProcessingError: If generation or saving fails
        """
        # Generate images from PDF
        images = self.generate(pdf_path, pages)

        # Prepare output paths
        thumbnail_paths = []
        base_name = pdf_path.stem
        extension = self.config.format.value

        # Process each image
        for idx, image in enumerate(images):
            # Determine page number
            if pages:
                page_num = pages[idx] if idx < len(pages) else idx + 1
            else:
                page_num = idx + 1

            # Create output filename
            output_filename = f"{base_name}_page_{page_num:03d}.{extension}"
            output_path = output_dir / output_filename

            # Resize and save
            resized_image = self.resize_image(image)
            self.save_thumbnail(resized_image, output_path)

            thumbnail_paths.append(output_path)

        return thumbnail_paths
