"""
CSV export implementation.

Author: DmitrTRC
"""

import csv
from pathlib import Path
from typing import Optional

from schedule_dnd.domain.exceptions import ExportFailedError
from schedule_dnd.domain.models import Schedule
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.base import BaseExporter


class CSVExporter(BaseExporter):
    """Exporter for CSV format."""

    def __init__(self) -> None:
        """Initialize CSV exporter."""
        self.settings = get_settings()

    def export(self, schedule: Schedule, output_path: Optional[Path] = None) -> Path:
        """
        Export schedule to CSV file.

        Args:
            schedule: Schedule to export
            output_path: Optional output file path

        Returns:
            Path to the exported file

        Raises:
            ExportError: If export fails
        """
        self.validate_schedule(schedule)

        if output_path is None:
            filename = self.get_default_filename(schedule)
            output_path = self.settings.output_dir / filename

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(output_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)

                # Write header
                writer.writerow(
                    [
                        "Подразделение",
                        "Дата",
                        "День недели",
                        "Тип дежурства",
                        "Время",
                        "Примечания",
                    ]
                )

                # Write data
                for unit in schedule.units:
                    for shift in unit.shifts:
                        writer.writerow(
                            [
                                unit.unit_name,
                                shift.date,
                                shift.get_day_of_week(),
                                shift.duty_type.value,
                                shift.time,
                                shift.notes,
                            ]
                        )

            return output_path

        except Exception as e:
            raise ExportFailedError(
                format_type="CSV", reason=f"Failed to write CSV file: {str(e)}"
            ) from e

    def get_file_extension(self) -> str:
        """Get file extension for CSV."""
        return "csv"

    def get_format_name(self) -> str:
        """Get format name."""
        return "CSV"
