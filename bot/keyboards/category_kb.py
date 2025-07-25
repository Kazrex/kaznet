import json
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_category_kb():
    with open('data/categories.json', 'r', encoding='utf-8') as f:
        categories = json.load(f)
    
    builder = InlineKeyboardBuilder()
    for category in categories:
        builder.button(text=category, callback_data=f"cat_{category}")
    builder.adjust(2)
    return builder.as_markup()