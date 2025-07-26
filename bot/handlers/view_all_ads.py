import math
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.utils import db
from bot.keyboards.pagination_kb import get_pagination_kb

router = Router()
PAGE_SIZE = 5

async def format_ad_message(ad):
    # ad: (id, title, description, price, contact, photo_id, is_top)
    top_icon = "👑 " if ad[6] else ""
    return (
        f"{top_icon}<b>{ad[1]}</b>\n\n"
        f"<i>{ad[2]}</i>\n\n"
        f"<b>Бағасы:</b> {ad[3]}\n"
        f"<b>Байланыс:</b> {ad[4]}"
    )

async def show_ads_page(message_or_callback, page=1):
    is_message = isinstance(message_or_callback, Message)
    user_id = message_or_callback.from_user.id
    
    # Пайдаланушының қаласын алу
    user = await db.get_user(user_id)
    if not user or not user[4]:
        if is_message:
            await message_or_callback.answer("Алдымен «🏙️ Қаланы өзгерту» батырмасын басып, қалаңызды таңдаңыз.")
        else: # CallbackQuery
            await message_or_callback.answer("Алдымен қала таңдаңыз.", show_alert=True)
        return

    city = user[4]
    ads, total_ads = await db.get_ads_by_city_paginated(city, page, PAGE_SIZE)

    if not ads:
        if is_message:
            await message_or_callback.answer(f"<b>{city}</b> қаласы бойынша әзірге хабарландырулар жоқ.")
        else:
            await message_or_callback.answer("Бұл бетте хабарландырулар жоқ.", show_alert=True)
        return

    total_pages = math.ceil(total_ads / PAGE_SIZE)
    
    # Бір хабарламаға барлығын жинау
    response_text = f"<b>{city}</b> қаласы бойынша хабарландырулар (Бет {page}/{total_pages}):\n\n"
    response_text += "\n\n➖➖➖➖➖➖\n\n".join([await format_ad_message(ad) for ad in ads])

    keyboard = get_pagination_kb(page, total_pages, city)

    if is_message:
        await message_or_callback.answer(response_text, reply_markup=keyboard)
    else:
        try:
            await message_or_callback.message.edit_text(response_text, reply_markup=keyboard)
        except Exception: # Егер хабарлама өзгермесе, қате болмауы үшін
            await message_or_callback.answer()

@router.message(F.text == "🔍 Хабарландыруларды көру")
async def view_all_ads_handler(message: Message):
    await show_ads_page(message)

@router.callback_query(F.data.startswith("page_"))
async def pagination_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    await show_ads_page(callback, page)

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()