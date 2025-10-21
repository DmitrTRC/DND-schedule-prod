"""
Exporter factory.

Creates exporter instances based on format type.
Author: DmitrTRC
"""

from schedule_dnd.domain.enums import ExportFormat
from schedule_dnd.domain.exceptions import UnsupportedFormatError
from schedule_dnd.infrastructure.exporters.base import BaseExporter
from schedule_dnd.infrastructure.exporters.csv_exporter import CSVExporter
from schedule_dnd.infrastructure.exporters.excel_exporter import ExcelExporter
from schedule_dnd.infrastructure.exporters.html_exporter import HTMLExporter
from schedule_dnd.infrastructure.exporters.json_exporter import JSONExporter
from schedule_dnd.infrastructure.exporters.markdown_exporter import MarkdownExporter


class ExporterFactory:
    """Factory for creating exporter instances."""

    _exporters: dict[ExportFormat, type[BaseExporter]] = {
        ExportFormat.JSON: JSONExporter,
        ExportFormat.EXCEL: ExcelExporter,
        ExportFormat.CSV: CSVExporter,
        ExportFormat.MARKDOWN: MarkdownExporter,
        ExportFormat.HTML: HTMLExporter,
    }

    @classmethod
    def create(cls, format_type: ExportFormat) -> BaseExporter:
        """
        Create an exporter instance for the specified format.

        Args:
            format_type: Export format

        Returns:
            Exporter instance

        Raises:
            UnsupportedFormatError: If format is not supported
        """
        exporter_class = cls._exporters.get(format_type)

        if exporter_class is None:
            supported_formats = [fmt.value for fmt in cls._exporters.keys()]
            raise UnsupportedFormatError(format_type.value, supported_formats)

        return exporter_class()

    @classmethod
    def get_supported_formats(cls) -> list[ExportFormat]:
        """
        Get list of supported export formats.

        Returns:
            List of supported formats
        """
        return list(cls._exporters.keys())

    @classmethod
    def is_supported(cls, format_type: ExportFormat) -> bool:
        """
        Check if a format is supported.

        Args:
            format_type: Export format to check

        Returns:
            True if format is supported
        """
        return format_type in cls._exporters
