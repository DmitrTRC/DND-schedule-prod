"""
Unit tests for ExportService.

Comprehensive testing of export operations.
Author: DmitrTRC
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from schedule_dnd.application.dto import ExportRequestDTO, ExportResultDTO
from schedule_dnd.application.services.export_service import ExportService
from schedule_dnd.domain.enums import DutyType, ExportFormat, Month
from schedule_dnd.domain.exceptions import (
    ExportFailedError,
    ScheduleNotFoundError,
    UnsupportedFormatError,
)
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit
from schedule_dnd.infrastructure.exporters.base import ScheduleExporter
from schedule_dnd.infrastructure.repositories.base import ScheduleRepository

# ═══════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def mock_repository() -> Mock:
    """Create a mock repository."""
    repo = MagicMock(spec=ScheduleRepository)
    repo.load = Mock()
    repo.exists = Mock(return_value=True)
    return repo


@pytest.fixture
def mock_exporter() -> Mock:
    """Create a mock exporter."""
    exporter = MagicMock(spec=ScheduleExporter)
    exporter.export = Mock()
    exporter.get_default_filename = Mock(return_value="schedule_2025_10.json")
    return exporter


@pytest.fixture
def export_service(mock_repository: Mock) -> ExportService:
    """Create an ExportService instance with mocked repository."""
    return ExportService(repository=mock_repository)


@pytest.fixture
def sample_schedule() -> Schedule:
    """Create a sample schedule for testing."""
    metadata = ScheduleMetadata(month=Month.OCTOBER, year=2025)
    unit = Unit(
        id=1,
        unit_name="ДНД «Всеволожский дозор»",
        shifts=[
            Shift(date="07.10.2025", duty_type=DutyType.UUP),
            Shift(date="15.10.2025", duty_type=DutyType.PDN),
        ],
    )
    return Schedule(metadata=metadata, units=[unit])


@pytest.fixture
def export_request() -> ExportRequestDTO:
    """Create a sample export request."""
    return ExportRequestDTO(
        schedule_id="schedule_2025_10.json",
        format="json",
        output_path=None,
    )


# ═══════════════════════════════════════════════════════════
# Export Schedule Tests
# ═══════════════════════════════════════════════════════════


class TestExportSchedule:
    """Test cases for exporting schedules."""

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_schedule_success(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_exporter: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successfully exporting a schedule."""
        # Arrange
        output_path = tmp_path / "output.json"
        output_path.write_text("{}")  # Create file
        mock_exporter.export.return_value = output_path
        mock_factory.create.return_value = mock_exporter

        # Act
        result = export_service.export_schedule(
            schedule=sample_schedule,
            format_type=ExportFormat.JSON,
            output_path=output_path,
        )

        # Assert
        assert isinstance(result, ExportResultDTO)
        assert result.success is True
        assert result.format == "json"
        assert result.output_path == str(output_path)
        assert result.file_size is not None
        assert result.error is None

        mock_factory.create.assert_called_once_with(ExportFormat.JSON)
        mock_exporter.export.assert_called_once_with(sample_schedule, output_path)

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_schedule_all_formats(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
    ) -> None:
        """Test exporting to all supported formats."""
        # Arrange
        formats = [
            ExportFormat.JSON,
            ExportFormat.EXCEL,
            ExportFormat.CSV,
            ExportFormat.MARKDOWN,
            ExportFormat.HTML,
        ]

        for fmt in formats:
            mock_exporter = MagicMock(spec=ScheduleExporter)
            mock_exporter.export.return_value = Path(f"test.{fmt.value}")
            mock_factory.create.return_value = mock_exporter

            # Act
            result = export_service.export_schedule(
                schedule=sample_schedule,
                format_type=fmt,
            )

            # Assert
            assert result.success is True
            assert result.format == fmt.value

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_schedule_failure(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_exporter: Mock,
    ) -> None:
        """Test export failure handling."""
        # Arrange
        mock_exporter.export.side_effect = Exception("Export failed")
        mock_factory.create.return_value = mock_exporter

        # Act
        result = export_service.export_schedule(
            schedule=sample_schedule,
            format_type=ExportFormat.JSON,
        )

        # Assert
        assert result.success is False
        assert result.error == "Export failed"
        assert result.file_size is None

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_schedule_without_output_path(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_exporter: Mock,
        tmp_path: Path,
    ) -> None:
        """Test exporting without specifying output path."""
        # Arrange
        default_path = tmp_path / "default_output.json"
        default_path.write_text("{}")
        mock_exporter.export.return_value = default_path
        mock_factory.create.return_value = mock_exporter

        # Act
        result = export_service.export_schedule(
            schedule=sample_schedule,
            format_type=ExportFormat.JSON,
            output_path=None,  # No output path specified
        )

        # Assert
        assert result.success is True
        mock_exporter.export.assert_called_once_with(sample_schedule, None)


# ═══════════════════════════════════════════════════════════
# Export from File Tests
# ═══════════════════════════════════════════════════════════


class TestExportFromFile:
    """Test cases for exporting from file."""

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_from_file_success(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        export_request: ExportRequestDTO,
        mock_repository: Mock,
        mock_exporter: Mock,
        tmp_path: Path,
    ) -> None:
        """Test successfully exporting from file."""
        # Arrange
        output_path = tmp_path / "output.json"
        output_path.write_text("{}")
        mock_repository.load.return_value = sample_schedule
        mock_exporter.export.return_value = output_path
        mock_factory.create.return_value = mock_exporter

        # Act
        result = export_service.export_from_file(export_request)

        # Assert
        assert result.success is True
        assert result.format == "json"
        mock_repository.load.assert_called_once()
        mock_exporter.export.assert_called_once()

    def test_export_from_file_schedule_not_found(
        self,
        export_service: ExportService,
        export_request: ExportRequestDTO,
        mock_repository: Mock,
    ) -> None:
        """Test export when schedule file doesn't exist."""
        # Arrange
        mock_repository.exists.return_value = False

        # Act & Assert
        with pytest.raises(ScheduleNotFoundError):
            export_service.export_from_file(export_request)

    def test_export_from_file_no_schedule_id(
        self,
        export_service: ExportService,
    ) -> None:
        """Test export without schedule ID raises error."""
        # Arrange
        request = ExportRequestDTO(
            schedule_id=None,  # Missing ID
            format="json",
        )

        # Act & Assert
        with pytest.raises(ValueError):
            export_service.export_from_file(request)

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_from_file_unsupported_format(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_repository: Mock,
    ) -> None:
        """Test export with unsupported format."""
        # Arrange
        mock_repository.load.return_value = sample_schedule
        request = ExportRequestDTO(
            schedule_id="test.json",
            format="unsupported_format",
        )

        # Act & Assert
        with pytest.raises(UnsupportedFormatError):
            export_service.export_from_file(request)

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_from_file_with_custom_output_path(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_repository: Mock,
        mock_exporter: Mock,
        tmp_path: Path,
    ) -> None:
        """Test export with custom output path."""
        # Arrange
        custom_path = tmp_path / "custom" / "output.json"
        custom_path.parent.mkdir(parents=True, exist_ok=True)
        custom_path.write_text("{}")

        mock_repository.load.return_value = sample_schedule
        mock_exporter.export.return_value = custom_path
        mock_factory.create.return_value = mock_exporter

        request = ExportRequestDTO(
            schedule_id="test.json",
            format="json",
            output_path=str(custom_path),
        )

        # Act
        result = export_service.export_from_file(request)

        # Assert
        assert result.success is True
        assert result.output_path == str(custom_path)
        mock_exporter.export.assert_called_once_with(sample_schedule, custom_path)


# ═══════════════════════════════════════════════════════════
# Export to All Formats Tests
# ═══════════════════════════════════════════════════════════


class TestExportToAllFormats:
    """Test cases for exporting to all formats."""

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_to_all_formats_success(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        tmp_path: Path,
    ) -> None:
        """Test exporting to all supported formats."""
        # Arrange
        mock_exporter = MagicMock(spec=ScheduleExporter)
        output_file = tmp_path / "test.json"
        output_file.write_text("{}")
        mock_exporter.export.return_value = output_file
        mock_exporter.get_default_filename.return_value = "test.json"
        mock_factory.create.return_value = mock_exporter

        supported_formats = [
            ExportFormat.JSON,
            ExportFormat.EXCEL,
            ExportFormat.CSV,
            ExportFormat.MARKDOWN,
            ExportFormat.HTML,
        ]
        mock_factory.get_supported_formats.return_value = supported_formats

        # Act
        results = export_service.export_to_all_formats(
            schedule=sample_schedule,
            base_output_dir=tmp_path,
        )

        # Assert
        assert len(results) == 5
        assert all(isinstance(r, ExportResultDTO) for r in results)
        successful = [r for r in results if r.success]
        assert len(successful) == 5

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_to_all_formats_partial_failure(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        tmp_path: Path,
    ) -> None:
        """Test exporting to all formats with some failures."""

        # Arrange
        def create_exporter(format_type: ExportFormat):
            mock_exp = MagicMock(spec=ScheduleExporter)
            if format_type == ExportFormat.JSON:
                # JSON export succeeds
                output = tmp_path / "test.json"
                output.write_text("{}")
                mock_exp.export.return_value = output
            else:
                # Other formats fail
                mock_exp.export.side_effect = Exception("Export failed")
            mock_exp.get_default_filename.return_value = f"test.{format_type.value}"
            return mock_exp

        mock_factory.create.side_effect = create_exporter
        supported_formats = [
            ExportFormat.JSON,
            ExportFormat.EXCEL,
            ExportFormat.CSV,
        ]
        mock_factory.get_supported_formats.return_value = supported_formats

        # Act
        results = export_service.export_to_all_formats(sample_schedule)

        # Assert
        assert len(results) == 3
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        assert len(successful) == 1  # Only JSON succeeds
        assert len(failed) == 2

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_export_to_all_formats_empty_list(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
    ) -> None:
        """Test exporting when no formats are supported."""
        # Arrange
        mock_factory.get_supported_formats.return_value = []

        # Act
        results = export_service.export_to_all_formats(sample_schedule)

        # Assert
        assert len(results) == 0


# ═══════════════════════════════════════════════════════════
# Utility Methods Tests
# ═══════════════════════════════════════════════════════════


class TestUtilityMethods:
    """Test cases for utility methods."""

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_get_supported_formats(
        self,
        mock_factory: Mock,
        export_service: ExportService,
    ) -> None:
        """Test getting list of supported formats."""
        # Arrange
        supported = [
            ExportFormat.JSON,
            ExportFormat.EXCEL,
            ExportFormat.CSV,
            ExportFormat.MARKDOWN,
            ExportFormat.HTML,
        ]
        mock_factory.get_supported_formats.return_value = supported

        # Act
        result = export_service.get_supported_formats()

        # Assert
        assert len(result) == 5
        assert "json" in result
        assert "excel" in result
        assert "csv" in result
        assert "markdown" in result
        assert "html" in result

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_get_export_path(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_exporter: Mock,
    ) -> None:
        """Test getting default export path."""
        # Arrange
        mock_exporter.get_default_filename.return_value = "schedule_2025_10.json"
        mock_factory.create.return_value = mock_exporter

        # Act
        result = export_service.get_export_path(sample_schedule, ExportFormat.JSON)

        # Assert
        assert isinstance(result, Path)
        assert result.name == "schedule_2025_10.json"
        assert "output" in str(result)

    def test_resolve_schedule_path_full_path(
        self, export_service: ExportService
    ) -> None:
        """Test resolving full path."""
        # Act
        result = export_service._resolve_schedule_path("/full/path/to/schedule.json")

        # Assert
        assert str(result) == "/full/path/to/schedule.json"

    def test_resolve_schedule_path_filename(
        self, export_service: ExportService
    ) -> None:
        """Test resolving just filename."""
        # Act
        result = export_service._resolve_schedule_path("schedule_2025_10.json")

        # Assert
        assert result.name == "schedule_2025_10.json"
        assert "data" in str(result)

    def test_resolve_schedule_path_year_month_format(
        self, export_service: ExportService
    ) -> None:
        """Test resolving year_month format."""
        # Act
        result = export_service._resolve_schedule_path("2025_10")

        # Assert
        assert result.name == "schedule_2025_10.json"


# ═══════════════════════════════════════════════════════════
# Integration-style Tests
# ═══════════════════════════════════════════════════════════


class TestExportWorkflow:
    """Test cases for complete export workflows."""

    @patch("schedule_dnd.application.services.export_service.ExporterFactory")
    def test_complete_export_workflow(
        self,
        mock_factory: Mock,
        export_service: ExportService,
        sample_schedule: Schedule,
        mock_repository: Mock,
        mock_exporter: Mock,
        tmp_path: Path,
    ) -> None:
        """Test a complete export workflow from request to result."""
        # Arrange
        output_path = tmp_path / "schedule_2025_10.json"
        output_path.write_text('{"test": "data"}')

        mock_repository.load.return_value = sample_schedule
        mock_exporter.export.return_value = output_path
        mock_factory.create.return_value = mock_exporter

        request = ExportRequestDTO(
            schedule_id="schedule_2025_10.json",
            format="json",
            output_path=str(output_path),
        )

        # Act
        result = export_service.export_from_file(request)

        # Assert
        assert result.success is True
        assert result.format == "json"
        assert Path(result.output_path).exists()
        assert result.file_size > 0

        # Verify all mocks were called correctly
        mock_repository.exists.assert_called_once()
        mock_repository.load.assert_called_once()
        mock_factory.create.assert_called_once()
        mock_exporter.export.assert_called_once()
