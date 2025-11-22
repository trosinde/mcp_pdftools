"""
Data models for PDF merge operations
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List


@dataclass
class MergeConfig:
    """
    Configuration for PDF merge operation

    Attributes:
        keep_bookmarks: Whether to preserve bookmarks from source PDFs
        add_toc: Whether to add a table of contents
        skip_on_error: If True, skip corrupted files; if False, abort on error
        progress_callback: Optional callback function(current, total)
        verbose: Enable verbose logging
    """
    keep_bookmarks: bool = True
    add_toc: bool = False
    skip_on_error: bool = False
    progress_callback: Optional[Callable[[int, int], None]] = None
    verbose: bool = False


@dataclass
class MergeResult:
    """
    Result of PDF merge operation

    Attributes:
        status: 'success', 'error', or 'partial'
        output_path: Path to the created merged PDF
        message: Status message or error description
        pages_merged: Total number of pages in merged PDF
        files_processed: Number of files successfully processed
        skipped_files: List of files that were skipped
        metadata: Additional metadata about the operation
    """
    status: str  # 'success' | 'error' | 'partial'
    output_path: Optional[Path] = None
    message: str = ""
    pages_merged: int = 0
    files_processed: int = 0
    skipped_files: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        """Returns True if merge was successful"""
        return self.status == 'success'
