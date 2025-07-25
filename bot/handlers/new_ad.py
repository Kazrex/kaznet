from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.new_ad_states import NewAdStates
from bot.keyboards.category_kb import get_category_kb
from bot.keyboards.confirm_kb import get_confirmation_kb
from bot.utils import db

router = Router()

# 1. "Жаңа хабарландыру" батырмасын басу
@router.message(F.text == "📝 Жаңа хабарландыру")
async def new_ad_start(message: Message, state: FSMContext):
    await state.set_state(NewAdStates.waiting_for_category)
    await message.answer("Категорияны таңдаңыз:", reply_markup=get_category_kb())

# 2. Категорияны таңдау
@router.callback_query(NewAdStates.waiting_for_category, F.data.startswith("cat_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    await state.set_state(NewAdStates.waiting_for_title)
    await callback.message.edit_text(f"Таңдалған категория: <b>{category}</b>\n\nЕнді хабарландырудың тақырыбын жазыңыз (мысалы, 'iPhone 13 сатамын'):")
    await callback.answer()

# 3. Тақырыпты енгізу
@router.message(NewAdStates.waiting_for_title)
async def title_entered(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewAdStates.waiting_for_description)
    await message.answer("Тамаша! Енді сипаттамасын жазыңыз (жағдайы, ерекшеліктері, т.б.):")

# 4. Сипаттаманы енгізу
@router.message(NewAdStates.waiting_for_description)
async def description_entered(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(NewAdStates.waiting_for_price)
    await message.answer("Енді бағасын жазыңыз (мысалы, '150000 тг' немесе 'келісімді'):")

# 5. Бағаны енгізу
@router.message(NewAdStates.waiting_for_price)
async def price_entered(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(NewAdStates.waiting_for_contact)
    await message.answer("Байланыс үшін нөміріңізді немесе Telegram нигіңізді жазыңыз:")

# 6. Байланысты енгізу
@router.message(NewAdStates.waiting_for_contact)
async def contact_entered(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(NewAdStates.waiting_for_photo)
    await message.answer("Суретін жіберіңіз немесе 'суретсіз' деп жазыңыз.")

# 7. Суретті енгізу
@router.message(NewAdStates.waiting_for_photo)
async def photo_entered(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    else:
        await state.update_data(photo=None)

    data = await state.get_data()
    user_info = await db.get_user(message.from_user.id)
    city = user_info[4] # selected_city
    await state.update_data(city=city, user_id=message.from_user.id)

    # Хабарландыруды алдын ала көрсету
    ad_text = (
        f"<b>{data['title']}</b>\n\n"
        f"<b>Сипаттамасы:</b> {data['description']}\n"
        f"<b>Бағасы:</b> {data['price']}\n\n"
        f"<b>Категория:</b> {data['category']}\n"
        f"<b>Қала:</b> {city}\n"
        f"<b>Байланыс:</b> {data['contact']}"
    )

    await state.set_state(NewAdStates.waiting_for_confirmation)
    if data.get('photo'):
        await message.answer_photo(photo=data['photo'], caption=f"Тексеріп шығыңыз:\n\n{ad_text}", reply_markup=get_confirmation_kb())
    else:
        await message.answer(f"Тексеріп шығыңыз:\n\n{ad_text}", reply_markup=get_confirmation_kb())

# 8. Растау
@router.callback_query(NewAdStates.waiting_for_confirmation, F.data == "confirm_ad_yes")
async def ad_confirmed(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await db.add_ad_to_db(data)
    await callback.message.edit_text("✅ Сіздің хабарландыруыңыз сәтті жарияланды!")
    await state.clear()
    await callback.answer()

@router.callback_query(NewAdStates.waiting_for_confirmation, F.data == "confirm_ad_no")
async def ad_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Хабарландыру жарияланбады.")
    await callback.answer()