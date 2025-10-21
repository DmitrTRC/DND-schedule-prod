"""
HTML export implementation.

Author: DmitrTRC
"""

from pathlib import Path
from typing import Optional

from schedule_dnd.domain.exceptions import ExportFailedError
from schedule_dnd.domain.models import Schedule
from schedule_dnd.infrastructure.config.settings import get_settings
from schedule_dnd.infrastructure.exporters.base import BaseExporter


class HTMLExporter(BaseExporter):
    """Exporter for HTML format."""

    def __init__(self) -> None:
        """Initialize HTML exporter."""
        self.settings = get_settings()

    def export(self, schedule: Schedule, output_path: Optional[Path] = None) -> Path:
        """
        Export schedule to HTML file.

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
            content = self._generate_html(schedule)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)

            return output_path

        except Exception as e:
            raise ExportFailedError(
                format_type="HTML", reason=f"Failed to write HTML file: {str(e)}"
            ) from e

    def get_file_extension(self) -> str:
        """Get file extension for HTML."""
        return "html"

    def get_format_name(self) -> str:
        """Get format name."""
        return "HTML"

    def _generate_html(self, schedule: Schedule) -> str:
        """Generate HTML content."""
        month_name = schedule.metadata.month.display_name()
        title = f"График дежурств ДНД - {month_name} {schedule.metadata.year}"

        # Calculate statistics
        total_shifts = schedule.get_total_shifts()
        shifts_by_type = schedule.get_shifts_by_type()

        html = f"""<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}

        .header .subtitle {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}

        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .stat-card .number {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}

        .stat-card .label {{
            color: #6c757d;
            font-size: 0.9em;
        }}

        .content {{
            padding: 30px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
        }}

        thead {{
            background: #667eea;
            color: white;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}

        th {{
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85em;
            letter-spacing: 0.5px;
        }}

        tbody tr:hover {{
            background: #f8f9fa;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge-pdn {{
            background: #e3f2fd;
            color: #1976d2;
        }}

        .badge-ppsp {{
            background: #f3e5f5;
            color: #7b1fa2;
        }}

        .badge-uup {{
            background: #fff3e0;
            color: #f57c00;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #6c757d;
            font-size: 0.9em;
            border-top: 1px solid #e9ecef;
        }}

        .metadata {{
            background: #f8f9fa;
            padding: 20px;
            margin-top: 30px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}

        .metadata h3 {{
            margin-bottom: 15px;
            color: #495057;
        }}

        .metadata p {{
            margin: 8px 0;
            color: #6c757d;
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .header {{
                background: #667eea !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}

            .stats {{
                break-inside: avoid;
            }}

            thead {{
                background: #667eea !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>График дежурств ДНД</h1>
            <div class="subtitle">{month_name} {schedule.metadata.year}</div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{len(schedule.units)}</div>
                <div class="label">Подразделений</div>
            </div>
            <div class="stat-card">
                <div class="number">{total_shifts}</div>
                <div class="label">Всего дежурств</div>
            </div>"""

        # Add type statistics
        for duty_type, count in shifts_by_type.items():
            html += f"""
            <div class="stat-card">
                <div class="number">{count}</div>
                <div class="label">{duty_type}</div>
            </div>"""

        html += """
        </div>

        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>Подразделение</th>
                        <th>Дата</th>
                        <th>День недели</th>
                        <th>Тип дежурства</th>
                        <th>Время</th>
                        <th>Примечания</th>
                    </tr>
                </thead>
                <tbody>"""

        # Add table rows
        for unit in schedule.units:
            for shift in unit.shifts:
                duty_badge_class = f"badge-{shift.duty_type.value.lower()}"
                html += f"""
                    <tr>
                        <td><strong>{unit.unit_name}</strong></td>
                        <td>{shift.date}</td>
                        <td>{shift.get_day_of_week()}</td>
                        <td><span class="badge {duty_badge_class}">{shift.duty_type.value}</span></td>
                        <td>{shift.time}</td>
                        <td>{shift.notes}</td>
                    </tr>"""

        html += """
                </tbody>
            </table>"""

        # Add metadata if enabled
        if self.settings.include_metadata:
            html += f"""
            <div class="metadata">
                <h3>Информация о документе</h3>
                <p><strong>Создано:</strong> {schedule.metadata.created_at.strftime('%d.%m.%Y %H:%M')}</p>"""

            if schedule.metadata.source:
                html += f"""
                <p><strong>Источник:</strong> {schedule.metadata.source}</p>"""

            if schedule.metadata.signatory:
                html += f"""
                <p><strong>Подписант:</strong> {schedule.metadata.signatory}</p>"""

            if schedule.metadata.note:
                html += f"""
                <p><strong>Примечание:</strong> {schedule.metadata.note}</p>"""

            html += """
            </div>"""

        html += f"""
        </div>

        <div class="footer">
            Документ создан автоматически системой Schedule DND v{self.settings.app_version}
        </div>
    </div>
</body>
</html>"""

        return html
