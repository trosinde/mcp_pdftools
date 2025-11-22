"""Output formatters for extracted text."""

from abc import ABC, abstractmethod
import json
from typing import Any

from .models import ExtractionResult, OutputFormat


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, result: ExtractionResult) -> str:
        """Format extraction result to string."""
        pass


class TxtFormatter(BaseFormatter):
    """Plain text formatter."""

    def format(self, result: ExtractionResult) -> str:
        """Format as plain text."""
        if result.text:
            return result.text
        else:
            # Combine pages
            return "\n\n".join(p.text for p in result.pages)


class JsonFormatter(BaseFormatter):
    """JSON formatter with metadata."""

    def format(self, result: ExtractionResult) -> str:
        """Format as JSON."""
        data = {
            "status": result.status,
            "metadata": result.metadata,
            "char_count": result.char_count,
            "pages": [
                {
                    "page_num": p.page_num,
                    "text": p.text,
                    "char_count": p.char_count,
                    "metadata": p.metadata
                }
                for p in result.pages
            ]
        }

        if result.message:
            data["message"] = result.message

        return json.dumps(data, indent=2, ensure_ascii=False)


class MarkdownFormatter(BaseFormatter):
    """Markdown formatter."""

    def format(self, result: ExtractionResult) -> str:
        """Format as Markdown."""
        lines = []

        # Add metadata section if available
        if result.metadata:
            lines.append("# PDF Metadata\n")
            for key, value in result.metadata.items():
                lines.append(f"**{key}**: {value}  ")
            lines.append("\n---\n")

        # Add content
        if result.text:
            lines.append("# Content\n")
            lines.append(result.text)
        else:
            for page in result.pages:
                lines.append(f"## Page {page.page_num}\n")
                lines.append(page.text)
                lines.append("\n---\n")

        return "\n".join(lines)


def get_formatter(format: OutputFormat) -> BaseFormatter:
    """Factory function to get appropriate formatter."""
    formatters = {
        OutputFormat.TXT: TxtFormatter,
        OutputFormat.JSON: JsonFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter
    }
    return formatters[format]()
