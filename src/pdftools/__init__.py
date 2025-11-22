"""
MCP PDF Tools - Modular PDF Processing Suite
"""

__version__ = "2.0.0"
__author__ = "MCP PDF Tools Team"

from . import core
from . import merge
from . import split
from . import ocr
from . import protection
from . import text_extraction
from . import thumbnails
from . import renaming

__all__ = [
    'core',
    'merge',
    'split',
    'ocr',
    'protection',
    'text_extraction',
    'thumbnails',
    'renaming',
]
