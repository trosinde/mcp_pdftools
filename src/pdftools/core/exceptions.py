"""
Custom exceptions for PDF Tools
"""


class PDFToolsError(Exception):
    """Base exception for all PDF Tools errors"""
    pass


class PDFNotFoundError(PDFToolsError):
    """Raised when a PDF file is not found"""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"PDF file not found: {path}")


class PDFProcessingError(PDFToolsError):
    """Base exception for PDF processing errors"""
    pass


class PDFCorruptedError(PDFProcessingError):
    """Raised when a PDF file is corrupted or invalid"""

    def __init__(self, path: str, reason: str = "Unknown"):
        self.path = path
        self.reason = reason
        super().__init__(f"PDF file is corrupted: {path} (Reason: {reason})")


class PDFEncryptedError(PDFProcessingError):
    """Raised when a PDF file is encrypted and cannot be processed"""

    def __init__(self, path: str):
        self.path = path
        super().__init__(f"PDF file is encrypted: {path}")


class ValidationError(PDFToolsError):
    """Base exception for validation errors"""
    pass


class InvalidPathError(ValidationError):
    """Raised when a file path is invalid"""

    def __init__(self, path: str, reason: str = "Invalid path"):
        self.path = path
        self.reason = reason
        super().__init__(f"{reason}: {path}")


class InvalidParameterError(ValidationError):
    """Raised when a parameter value is invalid"""

    def __init__(self, param_name: str, param_value, reason: str):
        self.param_name = param_name
        self.param_value = param_value
        self.reason = reason
        super().__init__(
            f"Invalid parameter '{param_name}' = {param_value}: {reason}"
        )


class InvalidRangeError(ValidationError):
    """Raised when a page range is invalid"""
    pass


class InsufficientPermissionsError(PDFToolsError):
    """Raised when there are insufficient permissions for file operations"""

    def __init__(self, path: str, operation: str = "access"):
        self.path = path
        self.operation = operation
        super().__init__(
            f"Insufficient permissions to {operation}: {path}"
        )


class OCRProcessingError(PDFProcessingError):
    """Base exception for OCR processing errors"""
    pass


class TesseractNotFoundError(OCRProcessingError):
    """Raised when Tesseract OCR is not installed"""

    def __init__(self):
        super().__init__(
            "Tesseract OCR not found. Please install tesseract-ocr or use Docker container."
        )


class LanguageNotAvailableError(OCRProcessingError):
    """Raised when required OCR language data is not available"""

    def __init__(self, language: str):
        self.language = language
        super().__init__(
            f"Language '{language}' not available. Please install tessdata-{language}"
        )


class ImageConversionError(OCRProcessingError):
    """Raised when PDF to image conversion fails"""

    def __init__(self, page_num: int, reason: str = "Unknown"):
        self.page_num = page_num
        self.reason = reason
        super().__init__(
            f"Failed to convert page {page_num} to image: {reason}"
        )
