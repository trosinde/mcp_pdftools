"""
Test PDF Generator for MCP PDF Tools

Generates various types of PDF files for testing purposes:
- Simple text PDFs
- Multi-page PDFs
- PDFs with images
- PDFs without OCR text layer (scanned images)
- PDFs with OCR text layer
- Large PDFs for performance testing
- Encrypted/protected PDFs
- Corrupted PDFs
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageDraw, ImageFont
import PyPDF2
from PyPDF2 import PdfWriter, PdfReader
import io


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


class TestPDFGenerator:
    """Generator for test PDF files"""

    def __init__(self, output_dir: Path):
        """
        Initialize generator

        Args:
            output_dir: Directory where test PDFs will be created
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_simple_text_pdf(self) -> Path:
        """Generate a simple single-page PDF with text"""
        output_path = self.output_dir / "test_simple_text.pdf"

        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "Simple Test PDF")
        c.drawString(100, 730, "This is a basic single-page PDF with text only.")
        c.drawString(100, 710, "Created for testing purposes.")
        c.drawString(100, 690, "Page 1 of 1")
        c.showPage()
        c.save()

        logger.info(f"Created: {output_path}")
        return output_path

    def generate_multipage_pdf(self, num_pages: int = 10) -> Path:
        """
        Generate a multi-page PDF

        Args:
            num_pages: Number of pages to generate
        """
        output_path = self.output_dir / f"test_multipage_{num_pages}p.pdf"

        c = canvas.Canvas(str(output_path), pagesize=A4)

        for page_num in range(1, num_pages + 1):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, f"Page {page_num} of {num_pages}")

            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"This is test content for page {page_num}.")
            c.drawString(100, 730, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
            c.drawString(100, 710, "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

            # Add some more lines
            y_pos = 670
            for i in range(10):
                c.drawString(100, y_pos, f"Line {i+1}: Additional test content for variety.")
                y_pos -= 20

            c.showPage()

        c.save()

        logger.info(f"Created: {output_path} ({num_pages} pages)")
        return output_path

    def generate_pdf_with_image(self, include_ocr_text: bool = False) -> Path:
        """
        Generate PDF with embedded image

        Args:
            include_ocr_text: If True, includes invisible text layer (simulating OCR)
        """
        suffix = "_with_ocr" if include_ocr_text else "_no_ocr"
        output_path = self.output_dir / f"test_image{suffix}.pdf"

        # Create a test image with text
        img = Image.new('RGB', (600, 400), color='white')
        draw = ImageDraw.Draw(img)

        # Draw some text on the image
        try:
            # Try to use a default font
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            # Fall back to default font
            font = ImageFont.load_default()

        draw.text((50, 150), "This is an image with text", fill='black', font=font)
        draw.text((50, 200), "It simulates a scanned document", fill='black', font=font)

        # Save image to bytes
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Create PDF
        c = canvas.Canvas(str(output_path), pagesize=letter)

        # Add the image
        c.drawImage(ImageReader(img_buffer), 100, 400, width=400, height=267)

        if include_ocr_text:
            # Add invisible text layer (simulating OCR)
            c.setFillColorRGB(1, 1, 1, alpha=0)  # Transparent text
            c.setFont("Helvetica", 12)
            c.drawString(100, 600, "This is an image with text")
            c.drawString(100, 580, "It simulates a scanned document")

        c.showPage()
        c.save()

        logger.info(f"Created: {output_path} (OCR: {include_ocr_text})")
        return output_path

    def generate_large_pdf(self, num_pages: int = 100) -> Path:
        """
        Generate a large PDF for performance testing

        Args:
            num_pages: Number of pages (default: 100)
        """
        output_path = self.output_dir / f"test_large_{num_pages}p.pdf"

        c = canvas.Canvas(str(output_path), pagesize=A4)

        for page_num in range(1, num_pages + 1):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, f"Page {page_num} of {num_pages}")

            c.setFont("Helvetica", 10)

            # Add lots of text to increase file size
            y_position = 750
            for i in range(40):
                text = f"Line {i+1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor."
                c.drawString(100, y_position, text)
                y_position -= 15

                if y_position < 50:  # Avoid going off page
                    break

            c.showPage()

            # Progress indicator
            if page_num % 10 == 0:
                logger.info(f"  Generated {page_num}/{num_pages} pages...")

        c.save()

        logger.info(f"Created: {output_path} ({num_pages} pages)")
        return output_path

    def generate_empty_pdf(self) -> Path:
        """Generate an empty PDF (no content)"""
        output_path = self.output_dir / "test_empty.pdf"

        c = canvas.Canvas(str(output_path), pagesize=letter)
        c.showPage()
        c.save()

        logger.info(f"Created: {output_path}")
        return output_path

    def generate_encrypted_pdf(self) -> Path:
        """Generate an encrypted/protected PDF"""
        # First create a simple PDF
        temp_path = self.output_dir / "temp_for_encryption.pdf"
        c = canvas.Canvas(str(temp_path), pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "This is an encrypted PDF")
        c.drawString(100, 730, "Password: test123")
        c.showPage()
        c.save()

        # Encrypt it
        output_path = self.output_dir / "test_encrypted.pdf"
        reader = PdfReader(str(temp_path))
        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        # Encrypt with password
        writer.encrypt(
            user_password="test123",
            owner_password="owner123",
            permissions_flag=0  # No permissions
        )

        with open(output_path, "wb") as output_file:
            writer.write(output_file)

        # Clean up temp file
        temp_path.unlink()

        logger.info(f"Created: {output_path} (Password: test123)")
        return output_path

    def generate_corrupted_pdf(self) -> Path:
        """Generate a corrupted/invalid PDF file"""
        output_path = self.output_dir / "test_corrupted.pdf"

        # Write invalid PDF content
        with open(output_path, 'w') as f:
            f.write("%PDF-1.4\n")
            f.write("This is not a valid PDF structure!\n")
            f.write("Just some random text to make it corrupted.\n")
            f.write("%%EOF\n")

        logger.info(f"Created: {output_path} (intentionally corrupted)")
        return output_path

    def generate_all(self, include_large: bool = False) -> List[Path]:
        """
        Generate all test PDFs

        Args:
            include_large: If True, generates large PDFs (takes longer)

        Returns:
            List of created file paths
        """
        logger.info("Generating all test PDFs...")

        created_files = []

        created_files.append(self.generate_simple_text_pdf())
        created_files.append(self.generate_multipage_pdf(10))
        created_files.append(self.generate_pdf_with_image(include_ocr_text=False))
        created_files.append(self.generate_pdf_with_image(include_ocr_text=True))
        created_files.append(self.generate_empty_pdf())
        created_files.append(self.generate_encrypted_pdf())
        created_files.append(self.generate_corrupted_pdf())

        if include_large:
            created_files.append(self.generate_large_pdf(100))
            created_files.append(self.generate_large_pdf(500))

        logger.info(f"\nGenerated {len(created_files)} test PDFs in: {self.output_dir}")
        return created_files


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate test PDF files for testing PDF tools'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='tests/fixtures',
        help='Output directory for test PDFs'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate all test PDFs'
    )
    parser.add_argument(
        '--large',
        action='store_true',
        help='Include large PDFs (slower)'
    )
    parser.add_argument(
        '--simple',
        action='store_true',
        help='Generate simple text PDF'
    )
    parser.add_argument(
        '--multipage',
        type=int,
        metavar='N',
        help='Generate multipage PDF with N pages'
    )
    parser.add_argument(
        '--with-image',
        action='store_true',
        help='Generate PDF with image (no OCR)'
    )
    parser.add_argument(
        '--with-ocr',
        action='store_true',
        help='Generate PDF with image and OCR text'
    )
    parser.add_argument(
        '--encrypted',
        action='store_true',
        help='Generate encrypted PDF'
    )
    parser.add_argument(
        '--corrupted',
        action='store_true',
        help='Generate corrupted PDF'
    )

    args = parser.parse_args()

    # Initialize generator
    generator = TestPDFGenerator(args.output)

    # Generate requested PDFs
    if args.all:
        generator.generate_all(include_large=args.large)
    else:
        generated_any = False

        if args.simple:
            generator.generate_simple_text_pdf()
            generated_any = True

        if args.multipage:
            generator.generate_multipage_pdf(args.multipage)
            generated_any = True

        if args.with_image:
            generator.generate_pdf_with_image(include_ocr_text=False)
            generated_any = True

        if args.with_ocr:
            generator.generate_pdf_with_image(include_ocr_text=True)
            generated_any = True

        if args.encrypted:
            generator.generate_encrypted_pdf()
            generated_any = True

        if args.corrupted:
            generator.generate_corrupted_pdf()
            generated_any = True

        if args.large:
            generator.generate_large_pdf(100)
            generated_any = True

        if not generated_any:
            parser.print_help()
            logger.warning("\nNo test PDFs specified. Use --all or specify individual types.")
            sys.exit(1)


if __name__ == "__main__":
    main()
