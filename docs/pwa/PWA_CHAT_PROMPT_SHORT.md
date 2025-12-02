# Разработка PWA модуля для Schedule DND

## Контекст
Schedule DND — Python CLI (v2.0) для управления графиками патрульных дежурств 8 ДНД в России. Clean Architecture, Python 3.11+, Poetry, Pydantic v2, Rich CLI, 282 теста (72% coverage).

**Проект:** `/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod`

**У тебя есть ПОЛНЫЙ доступ к файлам** через Filesystem tools.

## Структура
```
src/schedule_dnd/
├── domain/              # Models, validators, enums
├── application/         # Services (schedule_service, export_service)
├── infrastructure/      # Repositories, exporters
└── presentation/
    ├── cli/            # Существующий CLI
    └── web/            # НОВЫЙ PWA модуль (создать)
```

## Задача
Создать PWA для мобильного доступа волонтёров:
- Создание графиков (8 юнитов, типы дежурств)
- Просмотр/экспорт (JSON/Excel/CSV)
- Работа offline (Service Workers)
- Установка на домашний экран

## Предложение
**Flet** (Python PWA framework) — но открыт к альтернативам!

## Требования
✅ Сохранить Clean Architecture
✅ Переиспользовать domain/application layers
✅ Не ломать CLI
✅ Python-first решение
✅ Тесты ≥70% coverage

## Начни с:
1. Изучи код:
```python
Filesystem:read_text_file("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd/domain/models.py")
Filesystem:read_text_file("/Users/dmitrymorozov/PycharmProjects/DND-schedule-prod/src/schedule_dnd/application/services/schedule_service.py")
```

2. Дай рекомендацию: Flet vs альтернативы? Почему?

3. Предложи архитектуру `presentation/web/`

4. План разработки (phases, tasks, timing)

5. Создай proof-of-concept

Полный промпт: `docs/pwa/PWA_CHAT_PROMPT.md`
