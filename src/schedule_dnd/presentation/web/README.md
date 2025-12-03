# 📱 Schedule DND PWA - Proof of Concept

Progressive Web Application для управления графиками патрульных дежурств ДНД.

## 🎯 Что реализовано в PoC

### ✅ Архитектура
- **Clean Architecture** сохранена полностью
- **Новый слой**: `presentation/web/` для PWA
- **Адаптер**: Интеграция Flet UI с существующими Services
- **Разделение**: Domain/Application layers БЕЗ ИЗМЕНЕНИЙ

### ✅ Функционал
- **Home Page**: Список всех графиков
- **Просмотр**: Отображение графиков с статистикой
- **Экспорт**: Экспорт в 5 форматов (JSON/Excel/CSV/MD/HTML)
- **Удаление**: Удаление графиков с подтверждением
- **Responsive UI**: Material Design, адаптивный под мобильные

### ✅ Интеграция
- Использует `ScheduleService` напрямую
- Использует `ExportService` напрямую
- Работает с `JSONScheduleRepository`
- Читает из `/data` директории

## 📦 Установка

### 1. Установить Flet

```bash
cd /Users/dmitrymorozov/PycharmProjects/DND-schedule-prod
poetry add flet
```

### 2. Обновить зависимости

```bash
poetry install
```

## 🚀 Запуск

### Вариант 1: Через Poetry

```bash
poetry run schedule-dnd-web
```

### Вариант 2: Напрямую

```bash
poetry shell
python -m schedule_dnd.presentation.web.app
```

### Вариант 3: Из entry point

```bash
poetry shell
python src/schedule_dnd/presentation/web/app.py
```

## 🌐 Доступ

После запуска приложение будет доступно по адресу:

```
http://localhost:8080
```

Откройте в браузере (Chrome/Safari/Firefox).

## 📱 Установка как PWA

### На Desktop (Chrome/Edge):
1. Откройте http://localhost:8080
2. Нажмите ⊕ в адресной строке
3. "Установить Schedule DND"

### На Mobile (Android/iOS):
1. Откройте в браузере
2. Safari: Share → "Add to Home Screen"
3. Chrome: Menu → "Install app"

## 🏗️ Структура PWA модуля

```
src/schedule_dnd/presentation/web/
├── __init__.py
├── app.py                  # Entry point (main)
├── pages/
│   ├── __init__.py
│   └── home.py            # Home page с списком графиков
├── components/
│   └── __init__.py        # (для будущих компонентов)
├── adapters/
│   ├── __init__.py
│   └── service_adapter.py # Интеграция с Services
├── state/
│   └── __init__.py        # (для state management)
└── assets/
    └── manifest.json      # PWA manifest
```

## 🔧 Технологии

- **Flet 0.24.1**: Python PWA framework
- **Flutter Web**: Rendering engine
- **Material Design**: UI components
- **Clean Architecture**: Слоистая архитектура

## 🎨 Демонстрация PoC

### Home Page функции:
- ✅ Список всех сохраненных графиков
- ✅ Карточки с информацией (месяц, год, количество смен/юнитов)
- ✅ Кнопки действий для каждого графика
- ✅ Empty state если графиков нет
- ✅ Обработка ошибок

### Доступные действия:
- **Просмотр** (placeholder)
- **Экспорт** - работает полностью!
  - JSON
  - Excel
  - CSV
  - Markdown
  - HTML
- **Удаление** - работает с подтверждением

## 📊 Интеграция с Services

```python
# Пример: как PWA использует существующие services

# 1. Инициализация (app.py)
repository = JSONScheduleRepository(data_dir=settings.data_dir)
schedule_service = ScheduleService(repository=repository)
export_service = ExportService(repository, exporter_factory)

# 2. Создание адаптера
adapter = FletServiceAdapter(
    schedule_service=schedule_service,
    export_service=export_service,
)

# 3. Использование в UI (home.py)
schedules = adapter.list_schedules()  # → schedule_service.list_schedules()
result = adapter.export_schedule(id, format)  # → export_service.export_schedule()
```

## 🧪 Тестирование

### Проверь следующее:

1. **Запуск**: `poetry run schedule-dnd-web`
2. **Открой**: http://localhost:8080
3. **Проверь**:
   - Отображаются ли существующие графики из `/data`?
   - Работает ли экспорт?
   - Работает ли удаление?
   - Responsive на мобильном? (DevTools → Toggle Device Toolbar)

## 🔮 Что дальше?

### Следующие шаги (за рамками PoC):

1. **Create Page** - Создание новых графиков через PWA
2. **View Page** - Детальный просмотр графика
3. **Edit Page** - Редактирование смен
4. **LocalStorage** - Offline кэширование
5. **Service Workers** - PWA offline mode
6. **Push Notifications** - Уведомления
7. **Tests** - Unit/E2E тесты для PWA

## ⚠️ Limitations в PoC

- **No Create**: Создание графиков пока только через CLI
- **No Edit**: Редактирование смен пока только через CLI
- **No Offline**: LocalStorage не реализован
- **No Tests**: Тесты для PWA не написаны
- **Icons**: Иконки PWA - placeholder

## 💡 Заметки

### PWA vs CLI
- **CLI**: Для детального ввода данных (NO CYRILLIC!)
- **PWA**: Для просмотра, экспорта, мобильного доступа

### Clean Architecture
- **Domain**: БЕЗ ИЗМЕНЕНИЙ ✅
- **Application**: БЕЗ ИЗМЕНЕНИЙ ✅
- **Infrastructure**: БЕЗ ИЗМЕНЕНИЙ ✅
- **Presentation**: +web/ модуль (новый слой)

## 🤝 Обратная связь

После тестирования PoC, дай фидбек:
- ✅ Что работает хорошо?
- ❌ Что нужно улучшить?
- 💡 Какие фичи добавить в первую очередь?

---

**Версия**: 0.1.0 (Proof of Concept)
**Автор**: DmitrTRC
**Дата**: 2024
