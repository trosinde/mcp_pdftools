"""
PDF Protection Module.

This module provides functionality for protecting PDF files with
password encryption and configurable permissions.

Public API:
    - protect_pdf: Main function to protect a PDF file
    - protect_pdf_with_config: Protect using a configuration object
    - ProtectionConfig: Configuration dataclass
    - ProtectionResult: Result dataclass
    - PermissionLevel: Enum for permission levels
"""

from .core import protect_pdf, protect_pdf_with_config
from .models import ProtectionConfig, ProtectionResult, PermissionLevel

__all__ = [
    'protect_pdf',
    'protect_pdf_with_config',
    'ProtectionConfig',
    'ProtectionResult',
    'PermissionLevel',
]

__version__ = '1.0.0'
