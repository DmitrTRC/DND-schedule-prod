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

### 🔄 В процессе (Phase 4 - Сессия 3):
- Написание unit-тестов для CLI компонентов
- **Текущий статус:** Созданы тесты, но есть ошибки в моках и структуре

### 📊 Последние метрики (2025-10-26):

**Результаты тестов:**
- **Всего тестов:** 288 (+37 с прошлой сессии)
- **Прошло:** 264 ✅
- **Провалов:** 14 ❌
- **Ошибок:** 10 ⚠️
- **Coverage:** **72.36%** (+9.19%) → Цель: 90%

**Прогресс по coverage:**
- Сессия 1: 24% → 61% (+37%)
- Сессия 2: 61% → 63% (+2%) - исправление ошибок
- Сессия 3: 63% → **72%** (+9%) - тесты CLI

### 🔧 Coverage по компонентам:

**Отличный coverage (>90%):**
- schedule_service.py: 98% ✅
- export_service.py: 94% ✅
- excel_exporter.py: 97% ✅
- markdown_exporter.py: 97% ✅
- html_exporter.py: 96% ✅
- csv_exporter.py: 94% ✅
- json_exporter.py: 94% ✅
- models.py: 92% ✅

**Хороший coverage (80-90%):**
- dto.py: 88%
- config: 87%
- repositories: 83%
- logging.py: 80% (было 0%)

**Требует внимания (новые тесты не работают):**
- cli/app.py: 57% (было 0%, есть ошибки в тестах)
- cli/commands/create.py: 6% (было 0%, есть ошибки в тестах)
- cli/commands/base.py: 37% (было 0%)
- cli/formatters.py: 45% (было 0%)
- cli/commands/export.py: 9% (было 0%)
- cli/commands/load.py: 7% (было 0%)

## 📝 История изменений

### Сессия 1 (2025-10-25):
✅ Создано 78 тестов для экспортеров
✅ Создано 60+ тестов для валидаторов
✅ Coverage: 24% → 61%

### Сессия 2 (2025-10-25):
✅ Исправлено: "ДНД «Кузьмоловский»" → "ДНД «Заневское ГП»"
✅ Исправлен валидатор: добавлена проверка месяца в validate_day()
✅ Исправлены ожидания: "PDN" → "ПДН" (русский)
✅ Исправлен цвет Excel: "FF366092" → ("FF366092", "00366092")
✅ Все 251 тест прошли
✅ Coverage: 61% → 63%

### Сессия 3 (2025-10-26):
✅ Созданы тесты для CLI компонентов:
  - test_create_command.py (~10 тестов)
  - test_cli_app.py (~15 тестов)
  - test_other_components.py (~15 тестов)
✅ Coverage: 63% → 72% (+9%)
❌ Проблемы:
  - 10 ошибок в test_create_command.py
  - 3 провала в test_cli_app.py
  - 11 провалов в test_other_components.py

## 🔴 Текущие проблемы

### 1. **test_create_command.py - 10 ошибок**
```
TypeError: BaseCommand.__init__() got an unexpected keyword argument 'console'
```
**Причина:** BaseCommand.__init__() не принимает аргументы, создает их сам
**Решение:** Использовать patch для __init__ и настроить атрибуты после создания

### 2. **test_cli_app.py - 3 провала**
```
AttributeError: <module 'schedule_dnd.presentation.cli.app'> does not have the attribute 'CreateCommand'
```
**Причина:** CreateCommand импортируется внутри методов, не на уровне модуля
**Решение:** Патчить правильный путь импорта внутри метода

### 3. **test_other_components.py - 11 провалов**

**a) ScheduleFormatter методы не существуют:**
- `format_schedule_header()` - НЕТ в коде
- `format_unit_header()` - ЕСТЬ в коде ✅
- `format_schedule_summary()` - НЕТ в коде

**b) ExportResultDTO требует поле `output_path`:**
```
ValidationError: Field required [type=missing, input_value={'success': True, 'format...}, input_type=dict]
```
**Фактическая структура:**
```python
class ExportResultDTO(BaseModel):
    success: bool
    format: str
    output_path: str  # ← ОБЯЗАТЕЛЬНОЕ поле!
    error: Optional[str] = None
    file_size: Optional[int] = None
```

**c) BaseCommand - абстрактный класс:**
```
TypeError: Can't instantiate abstract class BaseCommand with abstract method execute
```
**Решение:** Создать конкретную реализацию для тестов

**d) setup_logging() возвращает None:**
```python
def setup_logging(log_file: Optional[Path] = None) -> None:  # ← Возвращает None!
```
**Тест ожидал:** `assert logger is not None`
**Решение:** Использовать `get_logger()` вместо `setup_logging()`

## 🎯 План исправлений

### Приоритет 1: Исправить test_create_command.py (10 ошибок)
```python
# Правильный подход:
@patch('schedule_dnd.presentation.cli.commands.create.BaseCommand.__init__')
def test_something(mock_base_init):
    mock_base_init.return_value = None
    cmd = CreateCommand()
    cmd.console = Mock()
    cmd.settings = Mock()
    cmd.schedule_service = Mock()
    # ... и т.д.
```

### Приоритет 2: Исправить test_cli_app.py (3 провала)
```python
# Правильный путь для патча:
@patch('schedule_dnd.presentation.cli.commands.create.CreateCommand')  # ❌ Неправильно
@patch('builtins.input')
def test_something(...):
    # Внутри _handle_create_schedule() CreateCommand импортируется локально
    # Нужно патчить внутри метода, где происходит импорт
```

### Приоритет 3: Исправить test_other_components.py (11 провалов)
- Удалить тесты несуществующих методов
- Исправить ExportResultDTO - добавить output_path
- Создать ConcreteCommand(BaseCommand) для тестов
- Исправить test_setup_logging - использовать get_logger()

## Структура проекта

```
DND-schedule-prod/
├── src/schedule_dnd/
│   ├── domain/           # Бизнес-логика (100% coverage)
│   ├── application/      # Сервисы (94-98% coverage)
│   ├── infrastructure/   # Внешние системы (80-97% coverage)
│   └── presentation/     # CLI (6-57% coverage) ← ТРЕБУЕТ ВНИМАНИЯ
│       ├── cli/
│       │   ├── app.py (105 строк, 57%)
│       │   ├── commands/
│       │   │   ├── create.py (196 строк, 6%)
│       │   │   ├── export.py (54 строки, 9%)
│       │   │   ├── load.py (70 строк, 7%)
│       │   │   └── base.py (37 строк, 37%)
│       │   └── formatters.py (95 строк, 45%)
│       └── ...
├── tests/
│   ├── unit/
│   │   ├── domain/       # ✅ 100% coverage
│   │   ├── application/  # ✅ 94-98% coverage
│   │   ├── infrastructure/ # ✅ 80-97% coverage
│   │   └── presentation/ # ⚠️ Есть тесты, но не работают
│   │       ├── test_create_command.py (10 ошибок)
│   │       ├── test_cli_app.py (3 провала)
│   │       └── test_other_components.py (11 провалов)
│   └── integration/
└── pyproject.toml
```

## 📝 8 подразделений ДНД

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

## Ключевые команды

```bash
# Запуск только тестов презентационного слоя
poetry run pytest tests/unit/presentation/ -v

# Запуск конкретного файла с тестами
poetry run pytest tests/unit/presentation/test_create_command.py -v

# Полный прогон с coverage
poetry run pytest --cov=src/schedule_dnd --cov-report=html --cov-report=term-missing -v

# Посмотреть coverage HTML
open htmlcov/index.html
```

## Важные файлы для контекста

Для исправления тестов нужно изучить:
1. `src/schedule_dnd/presentation/cli/commands/base.py` - как устроен BaseCommand
2. `src/schedule_dnd/presentation/cli/commands/create.py` - CreateCommand
3. `src/schedule_dnd/presentation/cli/app.py` - CLIApp и импорты
4. `src/schedule_dnd/presentation/cli/formatters.py` - какие методы реально есть
5. `src/schedule_dnd/application/dto.py` - структура ExportResultDTO
6. `src/schedule_dnd/infrastructure/logging.py` - что возвращает setup_logging

## GitHub репозиторий

- **Owner**: DmitrTRC
- **Repo**: https://github.com/DmitrTRC/schedule-dnd

## 🎯 Запрос на помощь

Мне нужна помощь с:

**Главная задача:** Исправить 24 провальных теста в презентационном слое (10 ошибок + 14 провалов)

**Конкретно:**
1. ✅ test_create_command.py - исправить моки для BaseCommand
2. ✅ test_cli_app.py - исправить патчи импортов
3. ✅ test_other_components.py - исправить DTO и несуществующие методы

**После исправлений:**
- Ожидаемый coverage: **~85-90%** (сейчас 72%)
- Все 288 тестов должны пройти

**Альтернатива:** Если исправление тестов слишком сложно, можно:
- Упростить тесты до базовой проверки импортов
- Сфокусироваться на других компонентах с низким coverage
- Написать интеграционные тесты вместо unit
```

---

## 📝 Как использовать этот промпт:

1. **Скопируйте** весь текст между тройными обратными кавычками
2. **Вставьте** в новый чат с Claude
3. **Добавьте** конкретную задачу в конце
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
- Coverage: 72.36% → Цель: 90%
- Тестов: 288 (264 passed, 14 failed, 10 errors)
- Созданы тесты для CLI, но есть 24 провала

Задача: Исправить провальные тесты в презентационном слое

Приоритеты:
1. test_create_command.py - 10 ошибок с моками BaseCommand
2. test_cli_app.py - 3 провала с импортами
3. test_other_components.py - 11 провалов (DTO, методы, абстрактные классы)

Действие: Изучи реальную структуру классов и исправь тесты
```

---

**Обновлено:** 2025-10-26 (Сессия 3)
**Статус проекта:** Phase 4 - Testing & Documentation (in progress)
**Текущая цель:** Исправить 24 провальных теста → Coverage 90% 🎯

---

## 📊 Дорожная карта к 90% coverage:

```
Сессия 1: 24% → 61% (+37%)  ✅ Тесты для exporters и validators
Сессия 2: 61% → 63% (+2%)   ✅ Исправление ошибок в тестах
Сессия 3: 63% → 72% (+9%)   ⚠️ Тесты для CLI (с ошибками)
Сессия 4: 72% → 90% (+18%)  🎯 Исправление тестов + допокрытие
```

**До цели осталось:** +18% coverage = ~350 строк
**Основной резерв:** CLI компоненты (520 строк с низким coverage)

---

## ⚠️ Важные замечания:

1. **BaseCommand** не принимает аргументы в `__init__()` - создает все сам
2. **CreateCommand** импортируется локально в методах app.py
3. **ExportResultDTO** требует обязательное поле `output_path`
4. **ScheduleFormatter** не имеет методов `format_schedule_header` и `format_schedule_summary`
5. **setup_logging()** возвращает `None`, не logger - используйте `get_logger()`
6. **BaseCommand** абстрактный - нельзя создать напрямую, нужна конкретная имплементация

---

## 🔍 Для дебага:

```bash
# Запустить конкретный тест с подробным выводом
poetry run pytest tests/unit/presentation/test_create_command.py::TestCreateCommand::test_execute_success_minimal -vv

# Запустить с показом print statements
poetry run pytest tests/unit/presentation/ -v -s

# Запустить первый провальный тест
poetry run pytest tests/unit/presentation/ -x -v
```
