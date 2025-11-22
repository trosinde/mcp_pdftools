"""
PDF Split module - Split PDFs into multiple files.
"""

from pdftools.split.core import split_pdf
from pdftools.split.models import SplitMode, SplitConfig, SplitResult
from pdftools.split.validators import parse_ranges

__all__ = [
    # Main function
    'split_pdf',

    # Models
    'SplitMode',
    'SplitConfig',
    'SplitResult',

    # Helpers
    'parse_ranges',
]

__version__ = '1.0.0'
