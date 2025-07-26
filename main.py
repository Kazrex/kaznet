import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from bot.utils.logger import setup_logger
from bot.utils.db import init_db
from bot.scheduler import setup_scheduler # ЖАҢА ИМПОРТ
from bot.handlers import start, city_selection, new_ad, my_ads, help, view_all_ads, admin_panel

async def main():
    await init_db()
    setup_logger()
    logging.info("Starting bot...")

    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Роутерлерді қосу
    dp.include_router(admin_panel.router)
    dp.include_router(start.router)
    dp.include_router(city_selection.router)
    dp.include_router(new_ad.router)
    dp.include_router(my_ads.router)
    dp.include_router(help.router)
    dp.include_router(view_all_ads.router)

    # ЖОСПАРЛАУШЫНЫ ІСКЕ ҚОСУ
    setup_scheduler(bot)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        await bot.session.close()
        logging.info("Bot stopped.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped manually.")