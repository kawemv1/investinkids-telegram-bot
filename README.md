Проверяю текущую конфигурацию логирования, чтобы добавить запись логов в файл.


[5 tools called]


Сейчас логи выводятся только в консоль. Добавьте запись в файл с ротацией и более детальное логирование событий.

## Решение: улучшенное логирование

Обновите `main.py`:

```python:investinkids-telegram-bot/main.py
import asyncio
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from db.queries import init_db
from handlers import user, admin
from scheduler import start_scheduler

# Создаем папку для логов, если её нет
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Настройка логирования
def setup_logging():
    # Формат логов
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Обработчик для файла с ротацией (макс 10 МБ, 5 файлов бэкапа)
    file_handler = RotatingFileHandler(
        filename=LOG_DIR / 'bot.log',
        maxBytes=10 * 1024 * 1024,  # 10 МБ
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Обработчик для ошибок в отдельный файл
    error_handler = RotatingFileHandler(
        filename=LOG_DIR / 'errors.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Обработчик для консоли (опционально, можно убрать на продакшене)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    
    # Настройка root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Логирование aiogram в отдельный файл (опционально)
    aiogram_logger = logging.getLogger('aiogram')
    aiogram_logger.setLevel(logging.WARNING)  # Только предупреждения и ошибки

setup_logging()

async def main():
    logger = logging.getLogger(__name__)
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Initialize bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Register routers
    dp.include_router(user.router)
    dp.include_router(admin.router)
    logger.info("Routers registered")
    
    # Start scheduler for reminders
    await start_scheduler(bot)
    logger.info("Reminder scheduler started")
    
    # Start polling
    logger.info("Bot started and ready to receive messages")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

## Дополнительно: логирование событий в обработчиках

Добавьте логирование в обработчики. Пример для `handlers/user.py`:

```python
import logging

logger = logging.getLogger(__name__)

# В начале обработчика cmd_start:
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Start command - show main menu"""
    logger.info(f"User {message.from_user.id} ({message.from_user.full_name}) started the bot")
    # ... остальной код

# В обработчике process_report_message:
@router.message(ReportStates.waiting_for_message)
async def process_report_message(message: Message, state: FSMContext, bot: Bot):
    """Process user's report message"""
    logger.info(f"New report from user {message.from_user.id}: {message.text[:50]}...")
    # ... остальной код
    logger.info(f"Report #{report_id} saved and sent to admin group")
```

## Что это дает:

1. Логи в файлах: `logs/bot.log` и `logs/errors.log`
2. Ротация: при достижении 10 МБ создается новый файл, хранится 5 бэкапов
3. Отдельный файл для ошибок
4. UTF-8 кодировка для корректного отображения русского текста
5. Консольный вывод (можно отключить на продакшене)

## Просмотр логов на сервере:

```bash
# Последние 50 строк
tail -n 50 logs/bot.log

# Следить за логами в реальном времени
tail -f logs/bot.log

# Поиск по логам
grep "ERROR" logs/bot.log

# Посмотреть ошибки
cat logs/errors.log
```

Нужно добавить логирование в конкретные обработчики?
