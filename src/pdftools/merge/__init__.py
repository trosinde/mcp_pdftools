"""
PDF Merge Module

Provides functionality to merge multiple PDF files into a single document.
"""

from .core import merge_pdfs
from .models import MergeResult, MergeConfig

__all__ = [
    'merge_pdfs',
    'MergeResult',
    'MergeConfig',
]

__version__ = '1.0.0'
