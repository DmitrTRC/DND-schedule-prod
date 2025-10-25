#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Schedule DND infrastructure.

Проверяет работоспособность всех основных компонентов:
- Domain models
- Repositories
- Services
- Exporters

Author: DmitrTRC
"""

import sys
from datetime import datetime
from pathlib import Path

# Добавляем src в path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_domain_models():
    """Тест доменных моделей."""
    print("\n" + "=" * 60)
    print("1️⃣  Тестирование Domain Models")
    print("=" * 60)

    from schedule_dnd.domain.enums import DutyType, Month
    from schedule_dnd.domain.models import Schedule, ScheduleMetadata, Shift, Unit

    # Создание метаданных
    metadata = ScheduleMetadata(
        month=Month.OCTOBER, year=2025, created_at=datetime.now()
    )
    print(f"✓ Метаданные созданы: {metadata.get_period_string()}")

    # Создание смены
    shift1 = Shift(
        date="07.10.2025",
        duty_type=DutyType.UUP,
        time="18:00-22:00",
        notes="Тестовое дежурство",
    )
    print(f"✓ Смена создана: {shift1}")
    print(f"  День недели: {shift1.get_day_of_week()}")

    # Создание подразделения
    unit = Unit(id=1, unit_name="ДНД «Всеволожский дозор»", shifts=[shift1])
    print(f"✓ Подразделение создано: {unit}")

    # Добавление еще одной смены
    shift2 = Shift(
        date="15.10.2025", duty_type=DutyType.PDN, time="18:00-22:00", notes="Тест 2"
    )
    unit.add_shift(shift2)
    print(f"✓ Добавлена вторая смена")

    # Статистика подразделения
    stats = unit.get_shifts_by_type()
    print(f"  Статистика: {stats}")

    # Создание графика
    schedule = Schedule(metadata=metadata, units=[unit])
    print(f"✓ График создан: {schedule}")
    print(f"  Всего смен: {schedule.get_total_shifts()}")
    print(f"  Статистика: {schedule.get_shifts_by_type()}")

    return schedule


def test_repository(schedule):
    """Тест репозитория."""
    print("\n" + "=" * 60)
    print("2️⃣  Тестирование Repository")
    print("=" * 60)

    from schedule_dnd.infrastructure.repositories.json_repository import JSONRepository

    repo = JSONRepository()
    print(f"✓ Репозиторий инициализирован")
    print(f"  Директория данных: {repo.base_dir}")

    # Сохранение
    saved_path = repo.save(schedule)
    print(f"✓ График сохранен: {saved_path}")

    # Проверка существования
    exists = repo.exists(saved_path)
    print(f"✓ Файл существует: {exists}")

    # Получение метаданных
    metadata = repo.get_schedule_metadata(saved_path)
    print(f"✓ Метаданные получены:")
    print(f"  Месяц: {metadata['month']}")
    print(f"  Год: {metadata['year']}")
    print(f"  Подразделений: {metadata['unit_count']}")
    print(f"  Смен: {metadata['total_shifts']}")

    # Загрузка
    loaded_schedule = repo.load(saved_path)
    print(f"✓ График загружен: {loaded_schedule}")

    # Список графиков
    schedules = repo.list_schedules()
    print(f"✓ Найдено графиков: {len(schedules)}")

    return saved_path


def test_services(schedule):
    """Тест сервисов."""
    print("\n" + "=" * 60)
    print("3️⃣  Тестирование Services")
    print("=" * 60)

    from schedule_dnd.application.services.export_service import ExportService
    from schedule_dnd.application.services.schedule_service import ScheduleService
    from schedule_dnd.infrastructure.repositories.json_repository import JSONRepository

    repo = JSONRepository()

    # Schedule Service
    schedule_service = ScheduleService(repo)
    print(f"✓ ScheduleService инициализирован")

    # Список графиков
    schedules = schedule_service.list_schedules()
    print(f"✓ Список графиков получен: {len(schedules)} шт.")

    # Статистика
    if schedules:
        stats = schedule_service.get_schedule_statistics(schedules[0].filename)
        print(f"✓ Статистика получена:")
        print(f"  Подразделений: {stats.total_units}")
        print(f"  Всего смен: {stats.total_shifts}")
        print(f"  По типам: {stats.shifts_by_type}")

    # Export Service
    export_service = ExportService(repo)
    print(f"✓ ExportService инициализирован")

    supported = export_service.get_supported_formats()
    print(f"✓ Поддерживаемые форматы: {', '.join(supported)}")


def test_exporters(schedule):
    """Тест экспортеров."""
    print("\n" + "=" * 60)
    print("4️⃣  Тестирование Exporters")
    print("=" * 60)

    from schedule_dnd.application.services.export_service import ExportService
    from schedule_dnd.infrastructure.repositories.json_repository import JSONRepository

    repo = JSONRepository()
    export_service = ExportService(repo)

    # Экспорт во все форматы
    results = export_service.export_to_all_formats(schedule)

    print(f"✓ Экспорт завершен:")
    for result in results:
        status = "✓" if result.success else "✗"
        size = f"{result.file_size:,} bytes" if result.file_size else "N/A"
        print(f"  {status} {result.format.upper():10} → {size}")
        if result.success:
            print(f"     {result.output_path}")
        else:
            print(f"     Ошибка: {result.error}")


def test_settings():
    """Тест настроек."""
    print("\n" + "=" * 60)
    print("5️⃣  Тестирование Settings")
    print("=" * 60)

    from schedule_dnd.infrastructure.config.settings import get_settings

    settings = get_settings()
    print(f"✓ Настройки загружены:")
    print(f"  Приложение: {settings.app_name} v{settings.app_version}")
    print(f"  Окружение: {settings.environment.value}")
    print(f"  Директория данных: {settings.data_dir}")
    print(f"  Директория экспорта: {settings.output_dir}")
    print(f"  Автосохранение: {settings.enable_autosave}")
    print(f"  Бэкапы: {settings.enable_backup} (max: {settings.max_backups})")


def main():
    """Основная функция тестирования."""
    print("\n" + "=" * 60)
    print("🚀  Schedule DND - Infrastructure Test")
    print("=" * 60)

    try:
        # 1. Тест моделей
        schedule = test_domain_models()

        # 2. Тест репозитория
        saved_path = test_repository(schedule)

        # 3. Тест сервисов
        test_services(schedule)

        # 4. Тест экспортеров
        test_exporters(schedule)

        # 5. Тест настроек
        test_settings()

        # Итоги
        print("\n" + "=" * 60)
        print("✅  ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("\n📁 Проверьте созданные файлы:")
        print(f"   - data/schedule_2025_10.json")
        print(f"   - output/schedule_2025_10.json")
        print(f"   - output/schedule_2025_10.xlsx")
        print(f"   - output/schedule_2025_10.csv")
        print(f"   - output/schedule_2025_10.md")
        print(f"   - output/schedule_2025_10.html")
        print("\n💡 Откройте HTML файл в браузере для просмотра!")

        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌  ОШИБКА ПРИ ТЕСТИРОВАНИИ")
        print("=" * 60)
        print(f"\n{type(e).__name__}: {e}")

        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
