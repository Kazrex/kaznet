from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_confirmation_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Иә, жариялау", callback_data="confirm_ad_yes")
    builder.button(text="❌ Жоқ, бас тарту", callback_data="confirm_ad_no")
    return builder.as_markup()