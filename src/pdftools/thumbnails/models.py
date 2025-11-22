"""
Data models for PDF thumbnail generation
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ThumbnailSize(Enum):
    """
    Predefined thumbnail sizes (width, height) in pixels.

    Attributes:
        SMALL: 150x150 pixels
        MEDIUM: 300x300 pixels
        LARGE: 600x600 pixels
    """
    SMALL = (150, 150)
    MEDIUM = (300, 300)
    LARGE = (600, 600)


class ThumbnailFormat(Enum):
    """
    Supported output image formats.

    Attributes:
        PNG: PNG format (lossless)
        JPG: JPEG format (lossy, configurable quality)
    """
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpg"  # Alias for JPG


@dataclass
class ThumbnailConfig:
    """
    Configuration for thumbnail generation.

    Attributes:
        size: Thumbnail dimensions (width, height) in pixels
        format: Output image format (PNG or JPG)
        quality: JPEG quality factor 1-100 (ignored for PNG)
        dpi: DPI for PDF rendering (higher = better quality, slower)
        verbose: Enable verbose logging
    """
    size: tuple[int, int]
    format: ThumbnailFormat
    quality: int = 85
    dpi: int = 200
    verbose: bool = False

    def __post_init__(self):
        """Validate configuration after initialization"""
        if not isinstance(self.size, tuple) or len(self.size) != 2:
            raise ValueError(f"Size must be tuple of (width, height), got: {self.size}")

        width, height = self.size
        if width <= 0 or height <= 0:
            raise ValueError(f"Size dimensions must be positive, got: {self.size}")

        if not isinstance(self.format, ThumbnailFormat):
            raise TypeError(f"Format must be ThumbnailFormat enum, got: {type(self.format)}")

        if not 1 <= self.quality <= 100:
            raise ValueError(f"Quality must be between 1 and 100, got: {self.quality}")

        if self.dpi <= 0:
            raise ValueError(f"DPI must be positive, got: {self.dpi}")


@dataclass
class ThumbnailResult:
    """
    Result of thumbnail generation operation.

    Attributes:
        status: Operation status ('success', 'error', or 'partial')
        thumbnails_created: Number of thumbnails successfully created
        thumbnail_paths: List of paths to created thumbnail files
        message: Status message or error description
        skipped_pages: List of page numbers that were skipped due to errors
        total_pages: Total number of pages in the PDF
    """
    status: str  # 'success' | 'error' | 'partial'
    thumbnails_created: int = 0
    thumbnail_paths: list[Path] = field(default_factory=list)
    message: str = ""
    skipped_pages: list[int] = field(default_factory=list)
    total_pages: int = 0

    @property
    def success(self) -> bool:
        """
        Returns True if generation was fully successful.

        Returns:
            bool: True if status is 'success', False otherwise
        """
        return self.status == 'success'

    @property
    def partial_success(self) -> bool:
        """
        Returns True if some thumbnails were created but some failed.

        Returns:
            bool: True if status is 'partial', False otherwise
        """
        return self.status == 'partial'
