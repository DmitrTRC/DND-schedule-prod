"""
Markdown export implementation.

Author: DmitrTRC
"""

from pathlib import Path
from typing import Optional

from schedule_dnd.domain.exceptions import ExportFailedError
from schedule_dnd.domain.models import Schedule
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.base import BaseExporter


class MarkdownExporter(BaseExporter):
    """Exporter for Markdown format."""

    def __init__(self) -> None:
        """Initialize Markdown exporter."""
        self.settings = get_settings()

    def export(self, schedule: Schedule, output_path: Optional[Path] = None) -> Path:
        """
        Export schedule to Markdown file.

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
            content = self._generate_markdown(schedule)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return output_path

        except Exception as e:
            raise ExportFailedError(
                format_type="Markdown",
                reason=f"Failed to write Markdown file: {str(e)}",
            ) from e

    def get_file_extension(self) -> str:
        """Get file extension for Markdown."""
        return "md"

    def get_format_name(self) -> str:
        """Get format name."""
        return "Markdown"

    def _generate_markdown(self, schedule: Schedule) -> str:
        """Generate Markdown content."""
        lines: list[str] = []

        # Title
        month_name = schedule.metadata.month.display_name()
        lines.append(f"# График дежурств ДНД - {month_name} {schedule.metadata.year}")
        lines.append("")

        # Metadata
        if self.settings.include_metadata:
            lines.append("## Информация о документе")
            lines.append("")
            lines.append(f"- **Месяц:** {month_name}")
            lines.append(f"- **Год:** {schedule.metadata.year}")
            lines.append(
                f"- **Создано:** {schedule.metadata.created_at.strftime('%d.%m.%Y %H:%M')}"
            )

            if schedule.metadata.source:
                lines.append(f"- **Источник:** {schedule.metadata.source}")

            if schedule.metadata.signatory:
                lines.append(f"- **Подписант:** {schedule.metadata.signatory}")

            lines.append("")

        # Statistics
        total_shifts = schedule.get_total_shifts()
        shifts_by_type = schedule.get_shifts_by_type()

        lines.append("## Статистика")
        lines.append("")
        lines.append(f"- **Всего подразделений:** {len(schedule.units)}")
        lines.append(f"- **Всего дежурств:** {total_shifts}")
        lines.append("")
        lines.append("**По типам:**")
        for duty_type, count in shifts_by_type.items():
            lines.append(f"- {duty_type}: {count}")
        lines.append("")

        # Schedule table
        lines.append("## График дежурств")
        lines.append("")

        # Table header
        lines.append(
            "| Подразделение | Дата | День недели | Тип дежурства | Время | Примечания |"
        )
        lines.append(
            "|---------------|------|-------------|---------------|-------|------------|"
        )

        # Table rows
        for unit in schedule.units:
            for shift in unit.shifts:
                lines.append(
                    f"| {unit.unit_name} | {shift.date} | {shift.get_day_of_week()} | "
                    f"{shift.duty_type.value} | {shift.time} | {shift.notes} |"
                )

        lines.append("")

        # Additional note
        if schedule.metadata.note:
            lines.append("## Примечание")
            lines.append("")
            lines.append(schedule.metadata.note)
            lines.append("")

        # Footer
        lines.append("---")
        lines.append("")
        lines.append(
            f"*Документ создан автоматически системой Schedule DND v{self.settings.app_version}*"
        )

        return "\n".join(lines)
