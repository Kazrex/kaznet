from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Жаңа хабарландыру")],
            [KeyboardButton(text="📂 Менің хабарландыруларым")],
            [KeyboardButton(text="🏙️ Қаланы өзгерту"), KeyboardButton(text="ℹ️ Көмек")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Мәзірден таңдаңыз..."
    )