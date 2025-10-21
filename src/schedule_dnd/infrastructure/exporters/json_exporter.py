"""
JSON export implementation.

Author: DmitrTRC
"""

import json
from pathlib import Path
from typing import Any, Optional

from schedule_dnd.domain.exceptions import ExportFailedError
from schedule_dnd.domain.models import Schedule
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.base import BaseExporter


class JSONExporter(BaseExporter):
    """Exporter for JSON format."""

    def __init__(self) -> None:
        """Initialize JSON exporter."""
        self.settings = get_settings()

    def export(self, schedule: Schedule, output_path: Optional[Path] = None) -> Path:
        """
        Export schedule to JSON file.

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
            data = self._schedule_to_dict(schedule)

            with open(output_path, "w", encoding="utf-8") as f:
                if self.settings.pretty_json:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                else:
                    json.dump(data, f, ensure_ascii=False)

            return output_path

        except Exception as e:
            raise ExportFailedError(
                format_type="JSON", reason=f"Failed to write JSON file: {str(e)}"
            ) from e

    def get_file_extension(self) -> str:
        """Get file extension for JSON."""
        return "json"

    def get_format_name(self) -> str:
        """Get format name."""
        return "JSON"

    def _schedule_to_dict(self, schedule: Schedule) -> dict[str, Any]:
        """Convert Schedule to dictionary."""
        return {
            "metadata": {
                "document_type": schedule.metadata.document_type,
                "month": schedule.metadata.month.display_name(),
                "year": schedule.metadata.year,
                "created_at": schedule.metadata.created_at.isoformat(),
                "created_by": schedule.metadata.created_by,
                "source": schedule.metadata.source,
                "signatory": schedule.metadata.signatory,
                "note": schedule.metadata.note,
            },
            "schedule": [
                {
                    "id": unit.id,
                    "unit_name": unit.unit_name,
                    "shifts": [
                        {
                            "date": shift.date,
                            "duty_type": shift.duty_type.value,
                            "time": shift.time,
                            "notes": shift.notes,
                        }
                        for shift in unit.shifts
                    ],
                }
                for unit in schedule.units
            ],
        }
