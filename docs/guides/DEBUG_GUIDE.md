# 🐛 Debug Mode & Logging Guide

## 🔍 Обзор

Приложение теперь имеет полноценную систему логирования с поддержкой debug mode.

---

## 📝 Логирование

### Где хранятся логи?

```
logs/schedule_dnd.log
```

Логи **всегда** пишутся в файл, независимо от режима.

### Уровни логирования

- **DEBUG** - Детальная информация (только в debug mode)
- **INFO** - Общая информация о работе
- **WARNING** - Предупреждения
- **ERROR** - Ошибки
- **CRITICAL** - Критические ошибки

---

## 🐛 Debug Mode

### Как включить?

#### Способ 1: Переменная окружения (рекомендуется)

```bash
# Linux/Mac
export SCHEDULE_DND_DEBUG=true
python -m schedule_dnd

# Windows
set SCHEDULE_DND_DEBUG=true
python -m schedule_dnd

# Или в одной строке
SCHEDULE_DND_DEBUG=true python -m schedule_dnd
```

#### Способ 2: Файл .env

Создайте/отредактируйте `.env` в корне проекта:

```env
SCHEDULE_DND_DEBUG=true
```

#### Способ 3: Аргумент командной строки

```bash
python -m schedule_dnd --debug
```

### Что делает debug mode?

1. ✅ **Подробные логи в консоль**
   - Все DEBUG сообщения выводятся в терминал
   - Видны номера строк и имена функций

2. ✅ **Детальная информация об ошибках**
   - Полный traceback при ошибках
   - Дополнительная диагностическая информация

3. ✅ **Логирование каждого шага**
   - Ввод пользователя записывается
   - Промежуточные состояния видны
   - Легко найти проблему

---

## 📋 Примеры логов

### Нормальный режим (logs/schedule_dnd.log)

```
2025-10-21 20:00:00 | INFO     | Application starting...
2025-10-21 20:00:01 | INFO     | Starting CreateCommand execution
2025-10-21 20:00:05 | INFO     | Period selected: Ноябрь 2025
2025-10-21 20:00:10 | INFO     | [Unit 1/8] Inputting shifts for: ДНД «Всеволожский дозор»
2025-10-21 20:00:15 | INFO     | [Shift #1] SUCCESS: 07.11.2025 - УУП
```

### Debug режим (консоль + файл)

```
2025-10-21 20:00:00 | DEBUG    | __main__:15 | Application starting...
2025-10-21 20:00:01 | DEBUG    | create.py:35 | Starting CreateCommand execution
2025-10-21 20:00:02 | DEBUG    | create.py:152 | Month input: 'ноябрь'
2025-10-21 20:00:02 | DEBUG    | create.py:156 | Month parsed successfully: <Month.NOVEMBER: 11>
2025-10-21 20:00:03 | DEBUG    | create.py:165 | Year input: 2025
2025-10-21 20:00:10 | DEBUG    | create.py:203 | [Shift #1] Raw input: '7'
2025-10-21 20:00:10 | DEBUG    | create.py:214 | [Shift #1] Parsed as day: 7
2025-10-21 20:00:10 | DEBUG    | create.py:221 | [Shift #1] Formatted date: 07.11.2025
2025-10-21 20:00:12 | DEBUG    | create.py:237 | [Shift #1] Duty type: 'УУП'
2025-10-21 20:00:12 | INFO     | create.py:249 | [Shift #1] SUCCESS: 07.11.2025 - УУП
```

---

## 🐞 Отладка проблем

### Проблема: "Неверный день: 1"

**Debug лог покажет:**

```
DEBUG | [Shift #1] Raw input: '1'
DEBUG | [Shift #1] Parsed as day: 1
DEBUG | [Shift #1] Formatted date: 01.11.2025
INFO  | [Shift #1] SUCCESS: 01.11.2025 - УУП
```

Если видите ошибку, но лог показывает успех - проблема в другом месте!

### Проблема: Экспорт не работает

**Debug лог покажет:**

```
INFO  | Starting export workflow
INFO  | Export format choice: 6
DEBUG | Loading schedule from: /path/to/data/schedule_2025_11.json
DEBUG | Schedule loaded
INFO  | Exporting to ALL formats
DEBUG | Exporting to format: json
ERROR | Failed to export: Permission denied
```

Сразу видно где проблема!

---

## 🎯 Практические сценарии

### Сценарий 1: Тестирование новой функции

```bash
# Включить debug
export SCHEDULE_DND_DEBUG=true

# Запустить
python -m schedule_dnd

# Следить за логами в реальном времени в другом терминале
tail -f logs/schedule_dnd.log
```

### Сценарий 2: Баг репорт для разработчика

```bash
# Включить debug
SCHEDULE_DND_DEBUG=true python -m schedule_dnd

# Воспроизвести баг
# ...

# Отправить logs/schedule_dnd.log разработчику
```

### Сценарий 3: Production использование

```bash
# Просто запустить (логи только в файл)
python -m schedule_dnd

# Проверить логи при необходимости
less logs/schedule_dnd.log
```

---

## 📊 Структура логов

```
logs/
├── schedule_dnd.log          # Текущий лог
├── schedule_dnd.log.1        # Backup 1 (старый)
├── schedule_dnd.log.2        # Backup 2
└── schedule_dnd.log.3        # Backup 3
```

### Ротация логов

- Максимальный размер: **10 MB**
- Количество backup файлов: **5**
- Автоматическая ротация при достижении лимита

---

## ⚙️ Настройка через .env

```env
# Debug mode
SCHEDULE_DND_DEBUG=true

# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
SCHEDULE_DND_LOG_LEVEL=DEBUG

# Log to console
SCHEDULE_DND_LOG_TO_CONSOLE=true

# Log to file
SCHEDULE_DND_LOG_TO_FILE=true

# Log rotation
SCHEDULE_DND_LOG_ROTATION=true
SCHEDULE_DND_LOG_MAX_SIZE=10485760  # 10 MB
SCHEDULE_DND_LOG_BACKUP_COUNT=5
```

---

## 🔧 Программное использование

```python
from schedule_dnd.infrastructure.logging import setup_logging, get_logger

# Setup logging
setup_logging()

# Get logger
logger = get_logger(__name__)

# Use it
logger.debug("Детальная отладочная информация")
logger.info("Информационное сообщение")
logger.warning("Предупреждение")
logger.error("Ошибка")
logger.exception("Ошибка с traceback")
```

---

## 📝 Что логируется?

### CreateCommand

- Начало/конец выполнения
- Выбранный период (месяц/год)
- Каждое подразделение (начало/конец)
- Каждая смена (ввод/парсинг/добавление)
- Валидация (успех/ошибки)
- Сохранение
- Экспорт

### LoadCommand

- Список графиков
- Выбор графика
- Загрузка файла
- Отображение

### ExportCommand

- Выбор графика
- Выбор формата
- Экспорт (для каждого формата)
- Результаты

---

## 🎉 Исправлено

1. ✅ **Убран default="готово"** в Prompt.ask()
   - Теперь можно вводить цифры без конфликта

2. ✅ **Детальное логирование**
   - Каждый шаг записывается
   - Входные данные логируются
   - Ошибки детально описаны

3. ✅ **Debug mode**
   - Через переменную окружения
   - Через .env файл
   - Логи в консоль при debug=true

4. ✅ **Улучшенные сообщения об ошибках**
   - "Неверный день: '1'. Введите число от 1 до 31 или 'готово'"
   - Видно что именно было введено

---

## 🚀 Попробуйте сейчас!

```bash
# С debug
SCHEDULE_DND_DEBUG=true python -m schedule_dnd

# Создайте график
# Введите "1" когда спросит день
# Должно работать!

# Проверьте логи
cat logs/schedule_dnd.log | grep "Shift #1"
```

---

**Теперь создание графика работает + полное логирование! 🎉**
