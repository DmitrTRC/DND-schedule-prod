"""
Export orchestration service.

Handles export operations using exporters.
Author: DmitrTRC
"""

from pathlib import Path
from typing import Optional

from schedule_dnd.application.dto import ExportRequestDTO, ExportResultDTO
from schedule_dnd.domain.enums import ExportFormat
from schedule_dnd.domain.exceptions import ExportFailedError, ScheduleNotFoundError
from schedule_dnd.domain.models import Schedule
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.factory import ExporterFactory
from schedule_dnd.infrastructure.repositories.base import ScheduleRepository


class ExportService:
    """Service for exporting schedules to various formats."""

    def __init__(self, repository: ScheduleRepository) -> None:
        """
        Initialize export service.

        Args:
            repository: Repository for loading schedules
        """
        self.repository = repository
        self.settings = get_settings()

    def export_schedule(
        self,
        schedule: Schedule,
        format_type: ExportFormat,
        output_path: Optional[Path] = None,
    ) -> ExportResultDTO:
        """
        Export a schedule to a specific format.

        Args:
            schedule: Schedule to export
            format_type: Export format
            output_path: Optional custom output path

        Returns:
            Export result with file information

        Raises:
            ExportFailedError: If export fails
        """
        try:
            # Create exporter
            exporter = ExporterFactory.create(format_type)

            # Export schedule
            result_path = exporter.export(schedule, output_path)

            # Get file size
            file_size = result_path.stat().st_size if result_path.exists() else None

            return ExportResultDTO(
                success=True,
                format=format_type.value,
                output_path=str(result_path),
                file_size=file_size,
            )

        except Exception as e:
            return ExportResultDTO(
                success=False,
                format=format_type.value,
                output_path=str(output_path) if output_path else "",
                error=str(e),
            )

    def export_from_file(self, request: ExportRequestDTO) -> ExportResultDTO:
        """
        Export a schedule from a file.

        Args:
            request: Export request with schedule ID and format

        Returns:
            Export result

        Raises:
            ScheduleNotFoundError: If schedule file not found
            ExportFailedError: If export fails
        """
        # Resolve schedule file path
        if request.schedule_id:
            schedule_path = self._resolve_schedule_path(request.schedule_id)
        else:
            raise ValueError("Schedule ID is required")

        # Check if file exists
        if not self.repository.exists(schedule_path):
            raise ScheduleNotFoundError(request.schedule_id)

        # Load schedule
        schedule = self.repository.load(schedule_path)

        # Parse format
        try:
            format_type = ExportFormat(request.format.lower())
        except ValueError:
            supported = [f.value for f in ExporterFactory.get_supported_formats()]
            from schedule_dnd.domain.exceptions import UnsupportedFormatError

            raise UnsupportedFormatError(request.format, supported)

        # Prepare output path
        output_path = Path(request.output_path) if request.output_path else None

        # Export
        return self.export_schedule(schedule, format_type, output_path)

    def export_to_all_formats(
        self, schedule: Schedule, base_output_dir: Optional[Path] = None
    ) -> list[ExportResultDTO]:
        """
        Export a schedule to all supported formats.

        Args:
            schedule: Schedule to export
            base_output_dir: Base directory for output files (uses default if None)

        Returns:
            List of export results for each format
        """
        results: list[ExportResultDTO] = []
        output_dir = base_output_dir or self.settings.output_dir

        for format_type in ExporterFactory.get_supported_formats():
            try:
                exporter = ExporterFactory.create(format_type)
                filename = exporter.get_default_filename(schedule)
                output_path = output_dir / filename

                result = self.export_schedule(schedule, format_type, output_path)
                results.append(result)

            except Exception as e:
                results.append(
                    ExportResultDTO(
                        success=False,
                        format=format_type.value,
                        output_path="",
                        error=str(e),
                    )
                )

        return results

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported export formats.

        Returns:
            List of format names
        """
        return [fmt.value for fmt in ExporterFactory.get_supported_formats()]

    def get_export_path(self, schedule: Schedule, format_type: ExportFormat) -> Path:
        """
        Get the default export path for a schedule and format.

        Args:
            schedule: Schedule
            format_type: Export format

        Returns:
            Path where file would be exported
        """
        exporter = ExporterFactory.create(format_type)
        filename = exporter.get_default_filename(schedule)
        return self.settings.output_dir / filename

    def _resolve_schedule_path(self, schedule_id: str) -> Path:
        """Resolve schedule ID to full path."""
        # If it's already a path, use it
        if "/" in schedule_id or "\\" in schedule_id:
            return Path(schedule_id)

        # If it's just a filename, look in data directory
        if schedule_id.endswith(".json"):
            return self.settings.data_dir / schedule_id

        # If it's year_month format, construct filename
        if "_" in schedule_id:
            return self.settings.data_dir / f"schedule_{schedule_id}.json"

        # Default: treat as filename
        return self.settings.data_dir / schedule_id
