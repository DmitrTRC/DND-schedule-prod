"""
Domain constants for Schedule DND application.

This module defines immutable constants used throughout the domain layer.
Author: DmitrTRC
"""

from typing import Final

# ═══════════════════════════════════════════════════════════
# DND Units (Voluntary People's Squads)
# ═══════════════════════════════════════════════════════════

UNITS: Final[tuple[str, ...]] = (
    "ДНД «Всеволожский дозор»",
    "ДНД «Заневское ГП»",
    "ДНД «Правопорядок Лукоморье»",
    "ДНД «Колтушский патруль»",
    "ДНД «Новодевяткинское СП»",
    "ДНД «Русич»",
    "ДНД «Сертоловское ГП»",
    "ДНД «Северный оплот»",
)

# ═══════════════════════════════════════════════════════════
# Default Values
# ═══════════════════════════════════════════════════════════

DEFAULT_SHIFT_TIME: Final[str] = "18:00-22:00"
DEFAULT_SHIFT_NOTE: Final[str] = "Получение инструкций в ОП. Время: 17:30"

# ═══════════════════════════════════════════════════════════
# Date/Time Formats
# ═══════════════════════════════════════════════════════════

DATE_FORMAT: Final[str] = "%d.%m.%Y"
DATE_FORMAT_DISPLAY: Final[str] = "DD.MM.YYYY"
TIME_FORMAT: Final[str] = "%H:%M"
TIME_RANGE_FORMAT: Final[str] = "HH:MM-HH:MM"

# ═══════════════════════════════════════════════════════════
# Validation Constraints
# ═══════════════════════════════════════════════════════════

MIN_YEAR_OFFSET: Final[int] = 0  # Current year
MAX_YEAR_OFFSET: Final[int] = 5  # Max 5 years in future
MIN_DAY: Final[int] = 1
MAX_DAY: Final[int] = 31
MIN_MONTH: Final[int] = 1
MAX_MONTH: Final[int] = 12

# Maximum shifts per unit per month
MAX_SHIFTS_PER_UNIT: Final[int] = 50

# ═══════════════════════════════════════════════════════════
# Document Metadata
# ═══════════════════════════════════════════════════════════

DOCUMENT_SOURCE: Final[str] = "УМВД России по Всеволожскому району ЛО"
DOCUMENT_SIGNATORY: Final[str] = "Начальник УМВД, полковник полиции С.В. Колонистов"
DOCUMENT_NOTE: Final[str] = (
    "На основе поступающей информации об оперативной обстановке "
    "могут быть внесены корректировы в график выхода народных дружин."
)

# ═══════════════════════════════════════════════════════════
# Application Metadata
# ═══════════════════════════════════════════════════════════

APP_NAME: Final[str] = "Schedule DND"
APP_VERSION: Final[str] = "2.0.0"
APP_AUTHOR: Final[str] = "DmitrTRC"
APP_REPOSITORY: Final[str] = "https://github.com/DmitrTRC/schedule-dnd"


def is_valid_unit(unit_name: str) -> bool:
    """
    Check if unit name is valid.

    Args:
        unit_name: Name of the unit to check

    Returns:
        True if unit name is in the list of valid units
    """
    return unit_name in UNITS


def get_unit_index(unit_name: str) -> int:
    """
    Get index of unit in the UNITS tuple.

    Args:
        unit_name: Name of the unit

    Returns:
        Zero-based index of the unit

    Raises:
        ValueError: If unit name is not found
    """
    try:
        return UNITS.index(unit_name)
    except ValueError as e:
        raise ValueError(f"Unknown unit: {unit_name}") from e


def get_unit_by_index(index: int) -> str:
    """
    Get unit name by index.

    Args:
        index: Zero-based index

    Returns:
        Name of the unit

    Raises:
        IndexError: If index is out of range
    """
    return UNITS[index]
