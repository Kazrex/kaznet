import logging
from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from bot.utils import db
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def check_ads_for_expiry(bot: Bot):
    logging.info("Running scheduled job: checking for ad expiry...")
    try:
        ads_to_notify, ads_to_delete = await db.get_ads_for_expiry_check()

        # 1. Ескерту жіберу
        for ad_id, user_id, title in ads_to_notify:
            try:
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="✅ 7 күнге ұзарту", callback_data=f"extend_{ad_id}")]
                ])
                await bot.send_message(
                    user_id,
                    f"🔔 Ескерту!\n\nСіздің «<b>{title}</b>» атты хабарландыруыңыздың мерзімі шамамен 1 сағаттан соң бітеді.\n\n"
                    "Оны тағы 7 күнге ұзартқыңыз келе ме?",
                    reply_markup=keyboard
                )
                await db.update_ad_status(ad_id, 'pending_deletion') # Қайта ескерту жібермес үшін
            except TelegramAPIError as e:
                logging.error(f"Failed to send notification to {user_id} for ad {ad_id}: {e}")

        # 2. Өшіру
        for ad_id, user_id, title in ads_to_delete:
            try:
                await bot.send_message(
                    user_id,
                    f"🗑️ Сіздің «<b>{title}</b>» атты хабарландыруыңыздың мерзімі бітіп, жүйеден өшірілді."
                )
                await db.update_ad_status(ad_id, 'expired')
            except TelegramAPIError as e:
                logging.error(f"Failed to send expiry message to {user_id} for ad {ad_id}: {e}")
    
    except Exception as e:
        logging.error(f"Error in scheduler job: {e}")


def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
    # Жұмысты әр сағат сайын іске қосу
    scheduler.add_job(check_ads_for_expiry, 'interval', hours=1, args=(bot,))
    scheduler.start()
    logging.info("Scheduler started.")