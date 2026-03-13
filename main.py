import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handler_order import router

async def main():
    # Проверка токена
    if not BOT_TOKEN:
        print("❌ Ошибка: Токен бота не найден! Проверьте файл .env")
        return
    
    # Создаем объект бота
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Подключаем роутер обработчиков
    dp.include_router(router)
    
    try:
        # Получаем информацию о боте
        bot_info = await bot.get_me()
        print(f"🤖 Бот запущен: {bot_info.first_name}")
        
        # Запускаем опрос (Polling)
        print("⚙️  Начинаю опрос обновлений...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        
    except KeyboardInterrupt:
        print("\n🛑 Бот остановлен вручную!")
    except (Exception, RuntimeError) as e:
        print(f"❌ Критическая ошибка: {type(e).__name__}: {e}")
    finally:
        await bot.session.close()
        print("💤 Сессия закрыта")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
