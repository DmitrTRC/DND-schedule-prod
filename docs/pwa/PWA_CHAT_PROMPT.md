# Промпт для чата: Разработка PWA модуля для Schedule DND

## 📋 Контекст проекта

### О проекте Schedule DND
**Schedule DND** — Python CLI приложение для управления графиками патрульных дежурств 8 волонтёрских полицейских отрядов (Добровольные Народные Дружины) в России.

**Текущая версия:** v2.0 (No Cyrillic Input + Autosave)

**Технологии:**
- Python 3.11+
- Poetry (управление зависимостями)
- Pydantic v2 (валидация данных)
- Rich CLI (красивый терминальный интерфейс)
- Pytest (тестирование, coverage 72%)
- Clean Architecture (Domain, Application, Infrastructure, Presentation)

**Расположение проекта:**
```
/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod
```

**ВАЖНО:** У тебя есть **полный доступ к файлам проекта** через Filesystem tools. Ты можешь:
- Читать файлы: `Filesystem:read_text_file`
- Создавать файлы: `Filesystem:write_file`
- Редактировать файлы: `Filesystem:edit_file`
- Искать файлы: `Filesystem:search_files`
- Создавать директории: `Filesystem:create_directory`

### Структура проекта

```
DND-schedule-prod/
├── src/schedule_dnd/
│   ├── domain/              # Бизнес-логика, модели, валидаторы
│   │   ├── models.py        # Schedule, Unit, Shift
│   │   ├── enums.py         # DutyType, Month, ExportFormat
│   │   ├── validators.py    # Валидация дат, периодов
│   │   └── exceptions.py    # Кастомные исключения
│   ├── application/         # Use cases, сервисы
│   │   ├── dto.py           # Data Transfer Objects
│   │   └── services/
│   │       ├── schedule_service.py  # CRUD операции
│   │       └── export_service.py    # Экспорт в JSON/Excel/CSV/MD/HTML
│   ├── infrastructure/      # Внешние зависимости
│   │   ├── repositories/    # JSONRepository (сохранение/загрузка)
│   │   ├── exporters/       # Экспортёры для разных форматов
│   │   └── config/          # Settings (Pydantic Settings)
│   └── presentation/        # CLI интерфейс
│       └── cli/
│           ├── app.py       # CLIApp (главное меню)
│           └── commands/    # CreateCommand, ExportCommand, LoadCommand
├── tests/                   # 282 теста, 72% coverage
├── data/                    # Хранилище JSON графиков
├── docs/                    # Документация
└── pyproject.toml           # Poetry конфигурация
```

### Основной функционал

**CreateCommand (v2.0):**
1. Ввод периода (месяц 1-12, год) - **БЕЗ кириллицы**
2. Для каждого из 8 юнитов:
   - Ввод дня (1-31)
   - Выбор типа дежурства (1=ПДН, 2=ППСП, 3=УУП)
   - Автосохранение после каждого юнита
3. Валидация всего графика
4. Сохранение в JSON
5. Экспорт в 5 форматов: JSON, Excel, CSV, Markdown, HTML

**Ключевые особенности v2.0:**
- ✅ Нет ввода кириллицы (только цифры для месяца)
- ✅ Автосохранение после каждого юнита
- ✅ Восстановление прогресса при перезапуске
- ✅ Обработка Ctrl+C без потери данных
- ✅ Comprehensive логирование
- ✅ Все тесты проходят (282 passed)

### Текущее состояние

**Завершено:**
- ✅ Phase 4: Testing & Documentation (92%)
- ✅ Все unit-тесты работают
- ✅ Coverage: 72% (цель 90%)
- ✅ Clean Architecture реализована
- ✅ Полная документация в `docs/`

**GitHub:** DmitrTRC (пользователь)

---

## 🎯 Новая задача: PWA модуль

### Требования

**Цель:** Создать Progressive Web App для Schedule DND, которое будет работать на мобильных устройствах и в браузере.

**Почему PWA:**
- Конечные пользователи (волонтёры патрульных дружин) нуждаются в мобильном доступе
- Необходимо работать offline
- Простая установка через браузер (без App Store)
- Кросс-платформенность (iOS/Android/Desktop)

### Предложенное решение: Flet

**Flet** — Python фреймворк для создания кросс-платформенных приложений:
- Пишется на чистом Python (остаёмся в экосистеме)
- Поддержка PWA out-of-the-box
- Flutter под капотом (красивый UI)
- Работает на: Web, iOS, Android, Desktop
- Документация: https://flet.dev

**НО:** Открыт к альтернативам! Если есть лучшее решение — предложи!

### Альтернативы для рассмотрения

1. **Flet** (предложение пользователя)
   - ✅ Pure Python
   - ✅ PWA support
   - ✅ Красивый UI
   - ❓ Размер приложения?
   - ❓ Производительность на мобильных?

2. **FastAPI + React/Vue**
   - ✅ Стандартное решение
   - ✅ Полный контроль
   - ❌ Нужен JavaScript/TypeScript
   - ❌ Два языка в проекте

3. **Django + Django PWA**
   - ✅ Python only
   - ✅ Богатый функционал
   - ❌ Тяжеловесно для такой задачи

4. **Streamlit**
   - ✅ Pure Python
   - ✅ Очень быстрая разработка
   - ❌ Ограниченная PWA функциональность
   - ❌ Не очень мобильный UI

5. **PyScript + Service Workers**
   - ✅ Python в браузере
   - ❌ Экспериментальная технология
   - ❌ Ограничения производительности

### Архитектурные требования

**Принцип:** Сохранить Clean Architecture!

```
src/schedule_dnd/
├── domain/              # БЕЗ ИЗМЕНЕНИЙ
├── application/         # БЕЗ ИЗМЕНЕНИЙ
├── infrastructure/      # МИНИМАЛЬНЫЕ ИЗМЕНЕНИЯ
└── presentation/
    ├── cli/             # Существующий CLI (БЕЗ ИЗМЕНЕНИЙ)
    └── web/             # НОВЫЙ PWA модуль
        ├── app.py       # Web application
        ├── pages/       # UI страницы/компоненты
        ├── static/      # CSS, JS, icons
        └── manifest.json
```

**Важно:**
- ✅ PWA модуль должен использовать существующие services (schedule_service, export_service)
- ✅ Переиспользовать domain models и validators
- ✅ Не дублировать бизнес-логику
- ✅ CLI и PWA должны сосуществовать

### Функционал PWA (MVP)

**Обязательно:**
1. Создание графика (аналог CreateCommand)
   - Выбор месяца/года
   - Добавление смен для 8 юнитов
   - Автосохранение в LocalStorage
2. Просмотр созданных графиков
3. Экспорт в JSON/Excel/CSV
4. Работа offline (Service Workers)
5. Установка на домашний экран (PWA manifest)

**Опционально (Phase 2):**
- Редактирование существующих графиков
- Визуализация (календарь, графики)
- Уведомления о предстоящих дежурствах
- Синхронизация между устройствами

### Данные и хранение

**Текущее:** JSON файлы в `/data/`

**Для PWA:**
- LocalStorage для автосохранения
- IndexedDB для offline работы
- Синхронизация с JSON файлами (опционально)
- Возможность загрузки/выгрузки JSON

### Тестирование

- Unit-тесты для новых компонентов
- Интеграционные тесты PWA <-> services
- Поддержание coverage ≥70%

---

## 📝 Задание для чата

### Твоя роль

Ты — Senior Python разработчик с опытом в:
- Clean Architecture
- PWA разработке
- Python фреймворках (Flet/FastAPI/Django)
- Mobile-first дизайне
- Offline-first приложениях

### Что нужно сделать

**Шаг 1: Анализ и рекомендация**
1. Изучи существующий код проекта (у тебя есть доступ)
2. Проанализируй Flet vs альтернативы
3. Дай рекомендацию с обоснованием:
   - Какой фреймворк выбрать?
   - Почему именно он?
   - Какие компромиссы?
4. Оцени трудозатраты (в часах разработки)

**Шаг 2: Архитектура**
1. Распиши детальную структуру `presentation/web/`
2. Определи, как PWA будет взаимодействовать с существующими services
3. Определи data flow: LocalStorage ↔ Application Services ↔ Repository
4. Нарисуй диаграмму компонентов (текстом/ASCII)

**Шаг 3: План разработки**
1. Разбей на фазы (Phase 1: MVP, Phase 2: Enhanced features)
2. Определи tasks для каждой фазы
3. Укажи dependencies между tasks
4. Оцени время каждой фазы

**Шаг 4: Начало разработки**
1. Создай базовую структуру файлов
2. Подготовь `requirements.txt` / обнови `pyproject.toml`
3. Создай proof-of-concept:
   - Hello World PWA
   - Интеграция с schedule_service
   - Базовая форма создания графика
4. Инструкции по запуску для тестирования

### Вопросы для обсуждения

1. **Фреймворк:** Flet или альтернатива? Обоснуй выбор.
2. **Offline:** Как реализовать Service Workers в Python?
3. **State Management:** Как хранить состояние между sessions?
4. **Mobile UX:** Какие UI компоненты нужны для мобильного интерфейса?
5. **Deployment:** Как будем деплоить PWA?
6. **Data Sync:** Нужна ли синхронизация JSON с сервером?

### Ограничения

- ✅ Сохранить Clean Architecture
- ✅ Не ломать существующий CLI
- ✅ Переиспользовать domain/application layers
- ✅ Тесты должны проходить
- ✅ Python-first решение (если возможно)
- ⚠️ Бюджет: это волонтёрский проект (бесплатные решения приоритетны)

---

## 🚀 Начни с этого

```python
# Сначала изучи существующий код:
# 1. Прочитай domain models:
Filesystem:read_text_file("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd/domain/models.py")

# 2. Посмотри schedule_service:
Filesystem:read_text_file("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd/application/services/schedule_service.py")

# 3. Изучи CreateCommand (для понимания user flow):
Filesystem:read_text_file("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd/presentation/cli/commands/create.py")

# 4. Посмотри структуру проекта:
Filesystem:list_directory("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd")
```

После изучения — дай свои рекомендации и план!

---

## 📚 Дополнительные ресурсы

**Документация проекта:**
- `docs/phases/` - План разработки по фазам
- `docs/testing/START_TESTING_HERE.md` - Руководство по тестированию
- `docs/testing/TESTING_NO_CYRILLIC.md` - Особенности v2.0
- `CHANGELOG_v2.0.md` - История изменений

**Ссылки:**
- Flet: https://flet.dev
- Flet PWA Guide: https://flet.dev/docs/guides/python/deploying-web-app/progressive-web-apps
- Clean Architecture: https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html

---

## ✅ Критерии успеха

PWA модуль считается успешным, если:
1. ✅ Работает на мобильных (iOS/Android через браузер)
2. ✅ Можно установить на домашний экран
3. ✅ Работает offline
4. ✅ Использует существующие services (без дублирования логики)
5. ✅ Интуитивный mobile-first интерфейс
6. ✅ Тесты покрывают новый код (≥70%)
7. ✅ CLI продолжает работать без изменений
8. ✅ Документация обновлена

---

**Готов к обсуждению? Начинай с анализа кода и рекомендации по фреймворку!** 🚀
