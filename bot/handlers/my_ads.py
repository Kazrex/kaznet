from aiogram import Router, F
from aiogram.types import Message
from bot.utils import db

router = Router()

@router.message(F.text == "📂 Менің хабарландыруларым")
async def show_my_ads(message: Message):
    user_ads = await db.get_user_ads_from_db(message.from_user.id)
    if not user_ads:
        await message.answer("Сіз әлі бірде-бір хабарландыру берген жоқсыз.")
        return

    response = "<b>📂 Сіздің хабарландыруларыңыз:</b>\n\n"
    for i, ad in enumerate(user_ads, 1):
        # ad: (title, description, price, created_at)
        response += (
            f"<b>{i}. {ad[0]}</b>\n"
            f"<i>Бағасы:</i> {ad[2]}\n"
            f"<i>Жарияланды:</i> {ad[3].split(' ')[0]}\n"
            f"-------------------\n"
        )
    await message.answer(response)