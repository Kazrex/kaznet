from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils import db
from datetime import datetime

router = Router()

@router.message(F.text == "📂 Менің хабарландыруларым")
async def show_my_ads(message: Message):
    user_ads = await db.get_user_ads_from_db(message.from_user.id)
    if not user_ads:
        await message.answer("Сіз әлі бірде-бір белсенді хабарландыру берген жоқсыз.")
        return

    response = "<b>📂 Сіздің белсенді хабарландыруларыңыз:</b>\n\n"
    for ad in user_ads:
        # ad: (title, price, created_at, expires_at)
        expires_at_dt = datetime.fromisoformat(ad[3])
        days_left = (expires_at_dt - datetime.now()).days
        response += (
            f"<b>{ad[0]}</b>\n"
            f"<i>Бағасы:</i> {ad[1]}\n"
            f"<i>Мерзімі бітеді:</i> <b>{days_left} күннен соң</b> ({expires_at_dt.strftime('%d.%m.%Y')})\n"
            f"-------------------\n"
        )
    await message.answer(response)

# Хабарландыру мерзімін ұзарту хендлері
@router.callback_query(F.data.startswith("extend_"))
async def extend_ad_handler(callback: CallbackQuery):
    ad_id = int(callback.data.split("_")[1])
    await db.extend_ad(ad_id)
    await callback.message.edit_text(
        "✅ Хабарландыруыңыздың мерзімі сәтті түрде тағы 7 күнге ұзартылды!"
    )
    await callback.answer("Сәтті ұзартылды!")