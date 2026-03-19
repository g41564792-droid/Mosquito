import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handler_order import router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    # Проверка токена
    if not BOT_TOKEN:
        logger.error("Токен бота не найден! Проверьте файл .env")
        return
    
    # Создаем объект бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключаем роутер обработчиков
    dp.include_router(router)
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        logger.info(f"Бот запущен: {bot_info.first_name} (@{bot_info.username})")
        
        # Запускаем опрос (Polling)
        logger.info("Начинаю опрос обновлений...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную!")
    except Exception as e:
        logger.exception(f"Критическая ошибка: {type(e).__name__}: {e}")
    finally:
        await bot.session.close()
        logger.info("Сессия закрыта")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
