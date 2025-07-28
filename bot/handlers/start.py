from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from bot.utils import db
from bot.keyboards.city_kb import get_city_kb
from bot.keyboards.main_menu import get_main_menu_kb

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name

    await db.add_user(telegram_id, username, full_name)
    user = await db.get_user(telegram_id)

    # Негізгі менюді (reply keyboard) бірден жібереміз
    await message.answer(
        "Негізгі меню:",
        reply_markup=get_main_menu_kb(telegram_id)
    )

    # --- МІНЕ, ЕҢ БАСТЫ ӨЗГЕРІС ОСЫ ЖЕРДЕ ---
    if user and user[4]: # user[4] - selected_city (таңдалған қала)
        # Егер қала бұрын таңдалған болса, арнайы батырмамен хабарлама жібереміз
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Соңғы хабарландыруларды көру", callback_data="view_ads_on_start")]
        ])
        await message.answer(
            f"Сәлем, {full_name}! KAZNET-ке қайта қош келдіңіз!\n\n"
            f"Сіздің таңдаған қалаңыз: <b>{user[4]}</b>.\n\n"
            "Төмендегі батырманы басып, белсенді хабарландыруларды көре аласыз 👇",
            reply_markup=keyboard
        )
    else:
        # Егер қала таңдалмаса, таңдауды сұраймыз
        await message.answer(
            f"Сәлем, {full_name}!\nKAZNET ботына қош келдіңіз!\n\n"
            "Хабарландыруларды көру үшін алдымен қалаңызды таңдаңыз:",
            reply_markup=get_city_kb()
        )
