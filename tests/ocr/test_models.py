"""
Tests for OCR models
"""

import pytest
from pathlib import Path
from pdftools.ocr.models import (
    OCRLanguage,
    OutputMode,
    OCRConfig,
    OCRResult,
)


class TestOCRLanguage:
    """Test OCRLanguage enum"""

    def test_language_values(self):
        """Test that language enum has correct values"""
        assert OCRLanguage.GERMAN == "deu"
        assert OCRLanguage.ENGLISH == "eng"
        assert OCRLanguage.FRENCH == "fra"
        assert OCRLanguage.ITALIAN == "ita"
        assert OCRLanguage.SPANISH == "spa"

    def test_language_from_string(self):
        """Test creating language from string"""
        assert OCRLanguage("deu") == OCRLanguage.GERMAN
        assert OCRLanguage("eng") == OCRLanguage.ENGLISH


class TestOutputMode:
    """Test OutputMode enum"""

    def test_output_mode_values(self):
        """Test that output mode enum has correct values"""
        assert OutputMode.TXT == "txt"
        assert OutputMode.PDF == "pdf"
        assert OutputMode.JSON == "json"


class TestOCRConfig:
    """Test OCRConfig dataclass"""

    def test_default_config(self):
        """Test default configuration"""
        config = OCRConfig()
        assert config.pages is None
        assert config.dpi == 300
        assert config.tesseract_config is None
        assert config.progress_callback is None
        assert config.verbose is False

    def test_custom_config(self):
        """Test custom configuration"""
        config = OCRConfig(
            pages=[1, 2, 3],
            dpi=600,
            verbose=True
        )
        assert config.pages == [1, 2, 3]
        assert config.dpi == 600
        assert config.verbose is True


class TestOCRResult:
    """Test OCRResult dataclass"""

    def test_successful_result(self):
        """Test successful OCR result"""
        result = OCRResult(
            status='success',
            output_path=Path('output.txt'),
            message='OCR completed',
            pages_processed=5,
            total_pages=5
        )
        assert result.success is True
        assert result.output_path == Path('output.txt')
        assert result.pages_processed == 5

    def test_error_result(self):
        """Test error OCR result"""
        result = OCRResult(
            status='error',
            message='OCR failed'
        )
        assert result.success is False
        assert result.output_path is None

    def test_partial_result(self):
        """Test partial OCR result"""
        result = OCRResult(
            status='partial',
            pages_processed=3,
            total_pages=5
        )
        assert result.success is False
        assert result.pages_processed == 3
        assert result.total_pages == 5

    def test_metadata(self):
        """Test result metadata"""
        result = OCRResult(
            status='success',
            metadata={
                'avg_confidence': 0.95,
                'processing_time_seconds': 12.5,
                'total_words': 430
            }
        )
        assert result.metadata['avg_confidence'] == 0.95
        assert result.metadata['processing_time_seconds'] == 12.5
        assert result.metadata['total_words'] == 430
