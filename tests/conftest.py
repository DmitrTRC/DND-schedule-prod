"""
Pytest configuration and shared fixtures.

Author: DmitrTRC
"""

from datetime import datetime
from pathlib import Path
from typing import Generator

import pytest

from schedule_dnd.domain.enums import DutyType, Month
from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit

# ═══════════════════════════════════════════════════════════
# Fixtures: Domain Models
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def sample_shift() -> Shift:
    """Provide a sample shift for testing."""
    return Shift(
        date="07.10.2025",
        duty_type=DutyType.UUP,
        time="18:00-22:00",
        notes="Test shift",
    )


@pytest.fixture
def sample_shifts() -> list[Shift]:
    """Provide multiple sample shifts for testing."""
    return [
        Shift(date="07.10.2025", duty_type=DutyType.UUP),
        Shift(date="15.10.2025", duty_type=DutyType.PDN),
        Shift(date="22.10.2025", duty_type=DutyType.PPSP),
    ]


@pytest.fixture
def sample_unit() -> Unit:
    """Provide a sample unit for testing."""
    return Unit(id=1, unit_name="ДНД «Всеволожский дозор»", shifts=[])


@pytest.fixture
def sample_unit_with_shifts(sample_shifts: list[Shift]) -> Unit:
    """Provide a unit with shifts for testing."""
    unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»", shifts=sample_shifts)
    return unit


@pytest.fixture
def sample_metadata() -> ScheduleMetadata:
    """Provide sample schedule metadata for testing."""
    return ScheduleMetadata(month=Month.OCTOBER, year=2025, created_by="test_user")


@pytest.fixture
def sample_schedule(sample_metadata: ScheduleMetadata) -> Schedule:
    """Provide a sample schedule for testing."""
    return Schedule(metadata=sample_metadata, units=[])


@pytest.fixture
def sample_schedule_with_data(
    sample_metadata: ScheduleMetadata, sample_unit_with_shifts: Unit
) -> Schedule:
    """Provide a schedule with data for testing."""
    schedule = Schedule(metadata=sample_metadata)
    schedule.add_unit(sample_unit_with_shifts)
    return schedule


# ═══════════════════════════════════════════════════════════
# Fixtures: Test Data
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def valid_unit_names() -> list[str]:
    """Provide list of valid unit names."""
    return [
        "ДНД «Всеволожский дозор»",
        "ДНД «Заневское ГП»",
        "ДНД «Правопорядок Лукоморье»",
        "ДНД «Колтушский патруль»",
        "ДНД «Новодевяткинское СП»",
        "ДНД «Русич»",
        "ДНД «Сертоловское ГП»",
        "ДНД «Северный оплот»",
    ]


@pytest.fixture
def test_dates() -> list[str]:
    """Provide list of test dates."""
    return [
        "07.10.2025",
        "15.10.2025",
        "22.10.2025",
        "28.10.2025",
    ]


# ═══════════════════════════════════════════════════════════
# Fixtures: File System
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide temporary data directory for testing."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    yield data_dir
    # Cleanup is automatic with tmp_path


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide temporary output directory for testing."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    yield output_dir
    # Cleanup is automatic with tmp_path


# ═══════════════════════════════════════════════════════════
# Fixtures: Configuration
# ═══════════════════════════════════════════════════════════


@pytest.fixture
def test_config() -> dict[str, any]:
    """Provide test configuration."""
    return {
        "environment": "testing",
        "debug": True,
        "log_level": "DEBUG",
        "data_dir": "./test_data",
        "output_dir": "./test_output",
    }


# ═══════════════════════════════════════════════════════════
# Pytest Configuration
# ═══════════════════════════════════════════════════════════


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    """Modify test collection to add markers automatically."""
    for item in items:
        # Auto-mark tests based on their location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
