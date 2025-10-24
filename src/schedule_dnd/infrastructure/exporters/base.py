"""
Abstract exporter base class.

Defines the contract for schedule exporters.
Author: DmitrTRC
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from schedule_dnd.domain.models import Schedule


class BaseExporter(ABC):
    """Abstract base class for schedule exporters."""

    @abstractmethod
    def export(self, schedule: Schedule, output_path: Optional[Path] = None) -> Path:
        """
        Export a schedule to a file.

        Args:
            schedule: Schedule to export
            output_path: Optional output file path

        Returns:
            Path to the exported file

        Raises:
            ExportError: If export fails
        """
        pass

    @abstractmethod
    def get_file_extension(self) -> str:
        """
        Get the file extension for this exporter.

        Returns:
            File extension (e.g., 'json', 'xlsx', 'csv')
        """
        pass

    @abstractmethod
    def get_format_name(self) -> str:
        """
        Get the human-readable format name.

        Returns:
            Format name (e.g., 'JSON', 'Excel', 'CSV')
        """
        pass

    def get_default_filename(self, schedule: Schedule) -> str:
        """
        Get default filename for a schedule.

        Args:
            schedule: Schedule to export

        Returns:
            Default filename
        """
        month_num = schedule.metadata.month.to_number()
        year = schedule.metadata.year
        ext = self.get_file_extension()
        return f"schedule_{year}_{month_num:02d}.{ext}"

    def validate_schedule(self, schedule: Schedule) -> bool:
        """
        Validate that the schedule can be exported.

        Args:
            schedule: Schedule to validate

        Returns:
            True if valid

        Raises:
            ValidationError: If schedule is invalid
        """
        if not schedule.units:
            from schedule_dnd.domain.exceptions import ValidationError

            raise ValidationError("Cannot export schedule with no units")

        return True
