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
