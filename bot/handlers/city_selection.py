from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from bot.utils import db
from bot.keyboards.main_menu import get_main_menu_kb
from bot.keyboards.city_kb import get_city_kb

router = Router()

@router.message(F.text == "🏙️ Қаланы өзгерту")
async def change_city_prompt(message: Message):
    await message.answer("Жаңа қаланы таңдаңыз:", reply_markup=get_city_kb())

@router.callback_query(F.data.startswith("city_"))
async def select_city(callback: CallbackQuery):
    city = callback.data.split("_")[1]
    await db.update_user_city(callback.from_user.id, city)
    await callback.message.edit_text(f"Сіздің қалаңыз <b>{city}</b> болып таңдалды.")
    await callback.message.answer("Негізгі мәзір:", reply_markup=get_main_menu_kb())
    await callback.answer()