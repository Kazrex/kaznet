from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from bot.utils import db
from bot.keyboards.city_kb import get_city_kb
from bot.handlers.view_all_ads import show_ads_page # Басқа хендлерден функция импорттау

router = Router()

@router.message(F.text == "🏙️ Қаланы өзгерту")
async def change_city_handler(message: Message):
    await message.answer("Жаңа қаланы таңдаңыз:", reply_markup=get_city_kb())

@router.callback_query(F.data.startswith("city_"))
async def select_city(callback: CallbackQuery):
    city = callback.data.split("_")[1]
    await db.update_user_city(callback.from_user.id, city)
    
    # Қала таңдалғаннан кейінгі хабарламаны өшіреміз
    await callback.message.delete()
    
    await callback.answer(f"Сіздің қалаңыз {city} болып өзгертілді!", show_alert=True)
    
    # --- МІНЕ, ЕКІНШІ МАҢЫЗДЫ ӨЗГЕРІС ---
    # Қаланы таңдағаннан кейін бірден хабарландыруларды көрсетеміз
    await show_ads_page(callback.message)
