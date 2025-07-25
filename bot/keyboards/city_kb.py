import json
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_city_kb():
    with open('data/cities.json', 'r', encoding='utf-8') as f:
        cities = json.load(f)
    
    builder = InlineKeyboardBuilder()
    for city in cities:
        builder.button(text=city, callback_data=f"city_{city}")
    builder.adjust(2) # Батырмаларды екі қатарға бөлу
    return builder.as_markup()