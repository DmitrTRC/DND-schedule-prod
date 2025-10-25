# 🚀 Промпт для продолжения работы над Schedule DND

Скопируйте этот промпт в новый чат с Claude для продолжения работы над проектом:

---

## 📋 ПРОМПТ ДЛЯ CLAUDE:

```
Привет! Я продолжаю работу над проектом **Schedule DND** (Управление графиками дежурств ДНД).

## О проекте

**Schedule DND** - это Python CLI-приложение для управления графиками патрульных дежурств 8 подразделений Добровольных Народных Дружин (ДНД).

### Технологии:
- Python 3.11+
- Poetry (менеджер зависимостей)
- Clean Architecture (Domain → Application → Infrastructure → Presentation)
- Pydantic v2 (валидация данных)
- Pytest (тестирование)
- Rich (красивый CLI)

### Ключевые возможности:
- Интерактивное создание графиков дежурств
- Загрузка данных из JSON
- Экспорт в 5 форматов: JSON, Excel, CSV, Markdown, HTML
- Валидация данных по бизнес-правилам
- Статистика и отчеты

## Текущее состояние

### ✅ Реализовано (Phases 1-3):
- Domain Layer: модели, валидаторы, исключения
- Application Layer: сервисы (ScheduleService, ExportService)
- Infrastructure Layer: репозитории, экспортеры
- Presentation Layer: CLI-интерфейс
- Основные функции: создание, загрузка, экспорт графиков

### 🔄 В процессе (Phase 4):
- Написание unit-тестов для повышения coverage с 24% до 90%
- Создано 78 тестов для экспортеров
- Создано 60+ тестов для валидаторов
- Текущий coverage: ~24% → цель: 90%

### 📊 Метрики:
- Всего тестов: 191 (до исправлений)
- Coverage: 24.20% → Цель: 90%
- Компонентов с низким coverage:
  - Exporters: 16-37%
  - Validators: 19%
  - Services: 15-22%
  - CLI: 0%

## Структура проекта

```
DND-schedule-prod/
├── src/schedule_dnd/
│   ├── domain/           # Бизнес-логика
│   │   ├── models.py     # Shift, Unit, Schedule, ScheduleMetadata
│   │   ├── enums.py      # Month, DutyType, ExportFormat
│   │   ├── validators.py # Валидация данных
│   │   ├── exceptions.py # Исключения
│   │   └── constants.py  # Константы (UNITS, лимиты)
│   ├── application/      # Сервисы
│   │   ├── services/
│   │   │   ├── schedule_service.py
│   │   │   └── export_service.py
│   │   └── dto.py
│   ├── infrastructure/   # Внешние системы
│   │   ├── repositories/
│   │   │   └── json_repository.py
│   │   ├── exporters/    # CSV, JSON, Excel, MD, HTML
│   │   └── config/
│   └── presentation/     # CLI
│       └── cli/
├── tests/
│   ├── unit/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   └── presentation/
│   └── integration/
└── pyproject.toml
```

## Последние изменения

**Дата**: 2025-10-25

**Исправлено**:
- ImportError в test_exporters.py: `Metadata` → `ScheduleMetadata`
- Добавлено обязательное поле `id` для Unit в фикстурах
- Исправлен формат дат в тестах: YYYY-MM-DD → DD.MM.YYYY
- Использованы реальные имена подразделений из UNITS

**Созданные тесты**:
1. `tests/unit/infrastructure/test_exporters.py` (78 тестов):
   - CSV Exporter (10 тестов)
   - JSON Exporter (10 тестов)
   - Excel Exporter (10 тестов)
   - Markdown Exporter (9 тестов)
   - HTML Exporter (9 тестов)
   - Factory (7 тестов)
   - Integration (3 теста)

2. `tests/unit/domain/test_validators_extended.py` (60+ тестов):
   - Date validation
   - Time validation
   - Month/Year validation
   - Format/Parse functions

## Что нужно сделать дальше?

### Приоритет 1: Запустить тесты
```bash
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v
```

### Приоритет 2: Если coverage < 90%
- Дописать тесты для компонентов с низким покрытием
- Фокус на: Services, Repositories, CLI

### Приоритет 3: После достижения 90% coverage
- Обновить документацию
- Создать финальный отчет Phase 4
- Подготовить к production

## Ключевые команды

```bash
# Установка зависимостей
poetry install

# Запуск тестов
poetry run pytest -v

# Запуск с coverage
poetry run pytest --cov=src/schedule_dnd --cov-report=html

# Запуск приложения
poetry run schedule-dnd

# Форматирование кода
poetry run black src tests
poetry run isort src tests

# Линтер
poetry run ruff check src tests
```

## Важные файлы для контекста

Для быстрого погружения прочитай:
1. `src/schedule_dnd/domain/models.py` - основные модели
2. `src/schedule_dnd/domain/constants.py` - список UNITS и константы
3. `tests/unit/infrastructure/test_exporters.py` - примеры тестов
4. `ROADMAP.md` - полная история проекта

## GitHub репозиторий

- **Owner**: DmitrTRC
- **Repo**: https://github.com/DmitrTRC/schedule-dnd (предположительно)

## Запрос на помощь

Мне нужна помощь с:
[Опиши здесь свою задачу - например:]
- Проверить результаты тестов после исправлений
- Повысить coverage до 90%
- Дописать тесты для [конкретного компонента]
- Исправить ошибки в тестах
- Оптимизировать код
- Обновить документацию
```

---

## 📝 Как использовать этот промпт:

1. **Скопируйте** весь текст между тройными обратными кавычками
2. **Вставьте** в новый чат с Claude
3. **Добавьте** свою конкретную задачу в конце
4. **Прикрепите** файлы проекта или дайте доступ к директории

## 💡 Совет:

Вместе с промптом приложите:
- Последний лог тестов (`testres.log`)
- Coverage отчет (`htmlcov/index.html` или вывод терминала)
- Конкретные файлы, требующие внимания

---

**Этот промпт обновлен:** 2025-10-25
**Статус проекта:** Phase 4 - Testing & Documentation (in progress)
**Следующая цель:** Coverage 90%
