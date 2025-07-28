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

async def show_ads_page(message: Message, page: int = 1):
    user_id = message.from_user.id
    
    user = await db.get_user(user_id)
    if not user or not user[4]:
        await message.answer("Алдымен «🏙️ Қаланы өзгерту» батырмасын басып, қалаңызды таңдаңыз.")
        return

    city = user[4]
    ads, total_ads = await db.get_ads_by_city_paginated(city, page, PAGE_SIZE)

    if not ads:
        await message.answer(f"<b>{city}</b> қаласы бойынша әзірге хабарландырулар жоқ.")
        return

    total_pages = math.ceil(total_ads / PAGE_SIZE)
    
    response_text = f"<b>{city}</b> қаласы бойынша хабарландырулар (Бет {page}/{total_pages}):\n\n"
    response_text += "\n\n➖➖➖➖➖➖\n\n".join([await format_ad_message(ad) for ad in ads])

    keyboard = get_pagination_kb(page, total_pages, city)

    # Хабарландыруды жаңа хабарлама ретінде жіберу
    await message.answer(response_text, reply_markup=keyboard)


# --- ЖАҢА ХЕНДЛЕР ---
# /start кезіндегі "Хабарландыруларды көру" батырмасын басып алады
@router.callback_query(F.data == "view_ads_on_start")
async def view_ads_on_start_handler(callback: CallbackQuery):
    await callback.message.delete() # "Хабарландыруларды көру" батырмасы бар хабарламаны өшіреміз
    await show_ads_page(callback.message)
    await callback.answer()


@router.message(F.text == "🔍 Хабарландыруларды көру")
async def view_all_ads_handler(message: Message):
    await show_ads_page(message)

# Бетті ауыстыру логикасы (өзгереді)
@router.callback_query(F.data.startswith("page_"))
async def pagination_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[1])
    # Енді хабарламаны өңдейміз (edit), жаңадан жібермейміз
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    city = user[4]
    ads, total_ads = await db.get_ads_by_city_paginated(city, page, PAGE_SIZE)
    total_pages = math.ceil(total_ads / PAGE_SIZE)
    
    response_text = f"<b>{city}</b> қаласы бойынша хабарландырулар (Бет {page}/{total_pages}):\n\n"
    response_text += "\n\n➖➖➖➖➖➖\n\n".join([await format_ad_message(ad) for ad in ads])
    
    keyboard = get_pagination_kb(page, total_pages, city)
    
    try:
        await callback.message.edit_text(response_text, reply_markup=keyboard)
    except Exception:
        pass # Егер текст өзгермесе, қате шығармайды
    
    await callback.answer()

@router.callback_query(F.data == "ignore")
async def ignore_callback(callback: CallbackQuery):
    await callback.answer()
