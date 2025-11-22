"""
Data models for PDF protection operations.

This module defines the data structures used for PDF protection,
including configuration, results, and permission levels.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List
from enum import Enum


class PermissionLevel(Enum):
    """
    PDF permission levels.

    These permissions control what users can do with a protected PDF.
    """
    PRINT = "print"
    COPY = "copy"
    MODIFY = "modify"
    ANNOTATE = "annotate"

    @classmethod
    def from_string(cls, value: str) -> 'PermissionLevel':
        """
        Create PermissionLevel from string.

        Args:
            value: String representation of permission

        Returns:
            PermissionLevel enum value

        Raises:
            ValueError: If value is not a valid permission
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid = [p.value for p in cls]
            raise ValueError(
                f"Invalid permission: {value}. "
                f"Valid permissions: {', '.join(valid)}"
            )


@dataclass
class ProtectionConfig:
    """
    Configuration for PDF protection operation.

    Attributes:
        user_password: Password required to open the PDF (optional)
        owner_password: Password required to change permissions (optional)
        permissions: List of allowed permissions (default: all denied)
        use_128bit: Use 128-bit encryption (default: True)
        verbose: Enable verbose output (default: False)
    """
    user_password: Optional[str] = None
    owner_password: Optional[str] = None
    permissions: Optional[List[PermissionLevel]] = None
    use_128bit: bool = True
    verbose: bool = False

    def __post_init__(self):
        """Validate configuration after initialization."""
        if not self.user_password and not self.owner_password:
            raise ValueError("At least one password (user or owner) must be provided")

        if self.permissions is None:
            self.permissions = []


@dataclass
class ProtectionResult:
    """
    Result of PDF protection operation.

    Attributes:
        status: Operation status ('success' | 'error')
        output_path: Path to protected PDF file (if successful)
        message: Human-readable message describing the result
        encryption_applied: Whether encryption was successfully applied
        permissions_set: List of permissions that were set
    """
    status: str
    output_path: Optional[Path] = None
    message: str = ""
    encryption_applied: bool = False
    permissions_set: List[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """
        Check if operation was successful.

        Returns:
            True if status is 'success', False otherwise
        """
        return self.status == 'success'

    @classmethod
    def create_success(
        cls,
        output_path: Path,
        permissions: List[PermissionLevel]
    ) -> 'ProtectionResult':
        """
        Create a successful result.

        Args:
            output_path: Path to protected PDF
            permissions: Permissions that were set

        Returns:
            ProtectionResult indicating success
        """
        perm_names = [p.value for p in permissions]
        return cls(
            status='success',
            output_path=output_path,
            message=f"PDF protected successfully: {output_path}",
            encryption_applied=True,
            permissions_set=perm_names
        )

    @classmethod
    def create_error(cls, message: str) -> 'ProtectionResult':
        """
        Create an error result.

        Args:
            message: Error message

        Returns:
            ProtectionResult indicating error
        """
        return cls(
            status='error',
            message=message,
            encryption_applied=False
        )
