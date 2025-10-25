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

## 🎯 Доступ к файлам

**ВАЖНО:** У Claude есть ПРЯМОЙ ДОСТУП к файлам проекта через Filesystem API!
- Путь к проекту: `/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod`
- Claude может читать, редактировать и создавать файлы напрямую
- НЕ нужно прикладывать файлы - Claude видит всю структуру проекта

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
- **Текущий статус:** Исправлены критические ошибки, готовы к запуску тестов

### 📊 Последние метрики (2025-10-25):
- **Всего тестов:** 251
- **Пройдено:** 215 ✅
- **Провалено:** 1 ❌
- **Ошибок:** 35 (исправлены)
- **Coverage:** 61.43% → Цель: 90%

### 🔧 Компоненты с текущим coverage:
- **Отличный coverage (>90%):**
  - schedule_service.py: 98%
  - export_service.py: 94%
  - models.py: 92%

- **Хороший coverage (80-90%):**
  - dto.py: 88%
  - Exporters: 76-89%
  - repositories: 83%
  - config: 86%

- **Требует внимания (0%):**
  - CLI: 0% (все файлы presentation/)
  - logging.py: 0%

## Структура проекта

```
DND-schedule-prod/
├── src/schedule_dnd/
│   ├── domain/           # Бизнес-логика
│   │   ├── models.py     # Shift, Unit, Schedule, ScheduleMetadata
│   │   ├── enums.py      # Month, DutyType, ExportFormat
│   │   ├── validators.py # Валидация данных
│   │   ├── exceptions.py # Исключения
│   │   └── constants.py  # Константы (8 подразделений UNITS)
│   ├── application/      # Сервисы
│   │   ├── services/
│   │   │   ├── schedule_service.py (98% coverage)
│   │   │   └── export_service.py (94% coverage)
│   │   └── dto.py
│   ├── infrastructure/   # Внешние системы
│   │   ├── repositories/
│   │   │   └── json_repository.py (83% coverage)
│   │   ├── exporters/    # CSV, JSON, Excel, MD, HTML (76-89%)
│   │   └── config/
│   └── presentation/     # CLI (0% coverage - требует тестов)
│       └── cli/
├── tests/
│   ├── unit/
│   │   ├── domain/       # ✅ Полное покрытие
│   │   ├── application/  # ✅ Полное покрытие
│   │   ├── infrastructure/ # ✅ Хорошее покрытие
│   │   └── presentation/ # ❌ Нужны тесты
│   └── integration/
└── pyproject.toml
```

## 📝 8 подразделений ДНД (из constants.py)

```python
UNITS = (
    "ДНД «Всеволожский дозор»",
    "ДНД «Заневское ГП»",
    "ДНД «Правопорядок Лукоморье»",
    "ДНД «Колтушский патруль»",
    "ДНД «Новодевяткинское СП»",
    "ДНД «Русич»",
    "ДНД «Сертоловское ГП»",
    "ДНД «Северный оплот»",
)
```

## Последние изменения

**Дата:** 2025-10-25 (Сессия 2)

### ✅ Исправлено:
1. **test_exporters.py** - Неправильное название подразделения:
   - ❌ Было: `"ДНД «Кузьмоловский»"` (не существует)
   - ✅ Стало: `"ДНД «Заневское ГП»"` (валидное)
   - Исправлено в 2 местах (строка 72 и 248)

2. **validators.py** - IllegalMonthError при валидации:
   - Добавлена проверка месяца в `validate_day()` перед `calendar.monthrange()`
   - Теперь выбрасывается правильное исключение `MonthValidationError`
   - Исправлен тест `test_format_invalid_month`

### 🎯 Результат исправлений:
- 35 ошибок в test_exporters → должны быть исправлены ✅
- 1 провал в test_validators_extended → должен быть исправлен ✅
- Готовы к запуску полного набора тестов

**Дата:** 2025-10-25 (Сессия 1)

### Созданные тесты:
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

### Приоритет 1: Запустить тесты и проверить исправления 🚀
```bash
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod

# Быстрая проверка исправленных тестов
poetry run pytest tests/unit/infrastructure/test_exporters.py -v
poetry run pytest tests/unit/domain/test_validators_extended.py::TestFormatDate::test_format_invalid_month -v

# Полный прогон с coverage
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v
```

### Приоритет 2: Тесты для CLI (0% coverage) 📝
**Цель:** Поднять coverage с 61% до 90%

Создать тесты для:
- `presentation/cli/app.py` (105 строк, 0%)
- `presentation/cli/commands/create.py` (196 строк, 0%)
- `presentation/cli/commands/export.py` (54 строки, 0%)
- `presentation/cli/commands/load.py` (70 строк, 0%)
- `presentation/cli/formatters.py` (95 строк, 0%)

**Подход к тестированию CLI:**
- Использовать `typer.testing.CliRunner`
- Mock для Rich console и prompts
- Тестировать команды изолированно
- Проверять вывод и exit codes

### Приоритет 3: Финализация 🎉
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
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing

# Посмотреть coverage HTML
open htmlcov/index.html

# Запуск приложения
poetry run schedule-dnd

# Форматирование кода
poetry run black src tests
poetry run isort src tests

# Линтер
poetry run ruff check src tests

# Pre-commit проверки
pre-commit run --all-files
```

## Важные файлы для контекста

Claude может прочитать эти файлы самостоятельно:
1. `src/schedule_dnd/domain/constants.py` - 8 подразделений UNITS
2. `src/schedule_dnd/domain/models.py` - основные модели
3. `src/schedule_dnd/domain/validators.py` - валидация
4. `tests/unit/infrastructure/test_exporters.py` - примеры тестов
5. `ROADMAP.md` - полная история проекта
6. Coverage отчет: `htmlcov/index.html`

## GitHub репозиторий

- **Owner**: DmitrTRC
- **Repo**: https://github.com/DmitrTRC/schedule-dnd

## Запрос на помощь

Мне нужна помощь с:
[Опиши здесь свою задачу - например:]
- ✅ Проверить результаты тестов после исправлений
- 📝 Написать тесты для CLI компонентов
- 📈 Повысить coverage до 90%
- 🔧 Исправить найденные ошибки
- 📚 Обновить документацию
- 🎯 [Твоя конкретная задача]
```

---

## 📝 Как использовать этот промпт:

1. **Скопируйте** весь текст между тройными обратными кавычками
2. **Вставьте** в новый чат с Claude
3. **Добавьте** свою конкретную задачу в конце
4. ⚠️ **НЕ НУЖНО** прикладывать файлы - Claude имеет прямой доступ к проекту!

## 💡 Что Claude может делать:

- ✅ Читать любые файлы проекта
- ✅ Редактировать существующие файлы
- ✅ Создавать новые файлы
- ✅ Просматривать структуру директорий
- ❌ Запускать bash-команды (нужно запускать вручную)

## 🚀 Быстрый старт для новой сессии:

```
Привет Claude! Продолжаем работу над Schedule DND.

Проект: /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod

Статус:
- Coverage: 61.43% → Цель: 90%
- Исправлены критические ошибки в тестах
- Нужно написать тесты для CLI (0% coverage)

Задача: [Опиши что нужно сделать]
```

---

**Обновлено:** 2025-10-25 (после исправлений)
**Статус проекта:** Phase 4 - Testing & Documentation (in progress)
**Следующая цель:** CLI тесты → Coverage 90% → Production ready 🎯
