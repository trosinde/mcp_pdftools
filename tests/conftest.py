"""
Pytest configuration and shared fixtures for MCP PDF Tools
"""

import os
import shutil
from pathlib import Path
from typing import Generator
import pytest
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from PIL import Image
import io


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "requires_docker: Tests requiring Docker")


# ============================================================================
# DIRECTORY FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Return the test data directory"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def ensure_fixtures_dir(test_data_dir: Path) -> Path:
    """Ensure fixtures directory exists"""
    test_data_dir.mkdir(parents=True, exist_ok=True)
    return test_data_dir


@pytest.fixture
def temp_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary directory for test outputs"""
    yield tmp_path
    # Cleanup after test
    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)


@pytest.fixture
def output_dir(temp_dir: Path) -> Path:
    """Create an output directory in temp directory"""
    output = temp_dir / "output"
    output.mkdir(parents=True, exist_ok=True)
    return output


# ============================================================================
# PDF GENERATION FIXTURES
# ============================================================================

@pytest.fixture(scope="session")
def pdf_simple_text(ensure_fixtures_dir: Path) -> Path:
    """
    Generate a simple single-page PDF with text

    Returns:
        Path to generated PDF file
    """
    pdf_path = ensure_fixtures_dir / "test_simple_text.pdf"

    if not pdf_path.exists():
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "This is a simple test PDF.")
        c.drawString(100, 730, "It contains only text on a single page.")
        c.drawString(100, 710, "Created for testing purposes.")
        c.showPage()
        c.save()

    return pdf_path


@pytest.fixture(scope="session")
def pdf_multipage(ensure_fixtures_dir: Path) -> Path:
    """
    Generate a multi-page PDF (10 pages)

    Returns:
        Path to generated PDF file
    """
    pdf_path = ensure_fixtures_dir / "test_multipage.pdf"

    if not pdf_path.exists():
        c = canvas.Canvas(str(pdf_path), pagesize=A4)

        for page_num in range(1, 11):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, f"Page {page_num} of 10")
            c.setFont("Helvetica", 12)
            c.drawString(100, 750, f"This is test content for page {page_num}.")
            c.drawString(100, 730, "Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
            c.showPage()

        c.save()

    return pdf_path


@pytest.fixture(scope="session")
def pdf_with_image(ensure_fixtures_dir: Path) -> Path:
    """
    Generate a PDF containing an image (without OCR text layer)

    Returns:
        Path to generated PDF file
    """
    pdf_path = ensure_fixtures_dir / "test_with_image.pdf"

    if not pdf_path.exists():
        # Create a simple test image
        img = Image.new('RGB', (200, 200), color='red')
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_buffer.seek(0)

        # Create PDF with image
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(100, 750, "PDF with embedded image:")

        # Save temp image file
        temp_img = ensure_fixtures_dir / "temp_test_image.png"
        img.save(temp_img)

        c.drawImage(str(temp_img), 100, 500, width=200, height=200)
        c.showPage()
        c.save()

        # Cleanup temp image
        temp_img.unlink()

    return pdf_path


@pytest.fixture(scope="session")
def pdf_large(ensure_fixtures_dir: Path) -> Path:
    """
    Generate a large PDF (100+ pages) for performance testing

    Returns:
        Path to generated PDF file
    """
    pdf_path = ensure_fixtures_dir / "test_large.pdf"

    if not pdf_path.exists():
        c = canvas.Canvas(str(pdf_path), pagesize=A4)

        for page_num in range(1, 101):
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, f"Page {page_num} of 100")
            c.setFont("Helvetica", 10)

            # Add more text to increase file size
            y_position = 750
            for i in range(30):
                c.drawString(100, y_position, f"Line {i+1}: Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
                y_position -= 15

            c.showPage()

        c.save()

    return pdf_path


@pytest.fixture(scope="session")
def pdf_empty(ensure_fixtures_dir: Path) -> Path:
    """
    Generate an empty PDF (no content)

    Returns:
        Path to generated PDF file
    """
    pdf_path = ensure_fixtures_dir / "test_empty.pdf"

    if not pdf_path.exists():
        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        c.showPage()
        c.save()

    return pdf_path


# ============================================================================
# CORRUPTED/INVALID FILE FIXTURES
# ============================================================================

@pytest.fixture
def invalid_pdf(temp_dir: Path) -> Path:
    """
    Create an invalid/corrupted PDF file

    Returns:
        Path to invalid PDF file
    """
    pdf_path = temp_dir / "invalid.pdf"

    # Write invalid content
    with open(pdf_path, 'w') as f:
        f.write("This is not a valid PDF file!")

    return pdf_path


@pytest.fixture
def non_existent_pdf(temp_dir: Path) -> Path:
    """
    Return path to a non-existent PDF file

    Returns:
        Path that doesn't exist
    """
    return temp_dir / "non_existent.pdf"


# ============================================================================
# COLLECTION FIXTURES
# ============================================================================

@pytest.fixture
def multiple_pdfs(pdf_simple_text: Path, pdf_multipage: Path, pdf_with_image: Path) -> list[Path]:
    """
    Return a list of multiple PDF files for batch testing

    Returns:
        List of PDF file paths
    """
    return [pdf_simple_text, pdf_multipage, pdf_with_image]


# ============================================================================
# MOCK FIXTURES
# ============================================================================

@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger for testing logging output"""
    import logging

    class MockHandler(logging.Handler):
        def __init__(self):
            super().__init__()
            self.messages = []

        def emit(self, record):
            self.messages.append(self.format(record))

    handler = MockHandler()
    logger = logging.getLogger('pdftools')
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    yield handler

    logger.removeHandler(handler)


# ============================================================================
# PERFORMANCE FIXTURES
# ============================================================================

@pytest.fixture
def benchmark_timer():
    """Simple timer for benchmarking tests"""
    import time

    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None

        def start(self):
            self.start_time = time.time()

        def stop(self):
            self.end_time = time.time()

        @property
        def elapsed(self) -> float:
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return 0.0

    return Timer()


# ============================================================================
# CLEANUP
# ============================================================================

def pytest_sessionfinish(session, exitstatus):
    """Cleanup after all tests are done"""
    # Optional: Clean up large test files if needed
    pass
