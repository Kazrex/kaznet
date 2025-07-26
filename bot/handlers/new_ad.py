from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.states.new_ad_states import NewAdStates
from bot.keyboards.category_kb import get_category_kb
from bot.utils import db

router = Router()

def get_top_options_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="👑 Premium (7 күн) - 1000 тг", callback_data="top_7")
    builder.button(text="⭐ VIP (3 күн) - 500 тг", callback_data="top_3")
    builder.button(text="🔥 Standart (1 күн) - 300 тг", callback_data="top_1")
    builder.button(text="➡️ Жай жариялау", callback_data="top_0")
    builder.adjust(1)
    return builder.as_markup()

# ... (new_ad_start, category_selected, title_entered, description_entered, price_entered, contact_entered функциялары өзгеріссіз) ...

@router.message(F.text == "📝 Жаңа хабарландыру")
async def new_ad_start(message: Message, state: FSMContext):
    user = await db.get_user(message.from_user.id)
    if not user or not user[4]:
        await message.answer("Алдымен қаланы таңдауыңыз керек. Ол үшін «🏙️ Қаланы өзгерту» батырмасын басыңыз.")
        return
    await state.set_state(NewAdStates.waiting_for_category)
    await message.answer("Категорияны таңдаңыз:", reply_markup=get_category_kb())

@router.callback_query(NewAdStates.waiting_for_category, F.data.startswith("cat_"))
async def category_selected(callback: CallbackQuery, state: FSMContext):
    category = callback.data.split("_", 1)[1]
    await state.update_data(category=category)
    await state.set_state(NewAdStates.waiting_for_title)
    await callback.message.edit_text(f"Таңдалған категория: <b>{category}</b>\n\nЕнді хабарландырудың тақырыбын жазыңыз:")
    await callback.answer()

@router.message(NewAdStates.waiting_for_title)
async def title_entered(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewAdStates.waiting_for_description)
    await message.answer("Сипаттамасын жазыңыз (жағдайы, ерекшеліктері, т.б.):")

@router.message(NewAdStates.waiting_for_description)
async def description_entered(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(NewAdStates.waiting_for_price)
    await message.answer("Бағасын жазыңыз (мысалы, '150000 тг' немесе 'келісімді'):")

@router.message(NewAdStates.waiting_for_price)
async def price_entered(message: Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(NewAdStates.waiting_for_contact)
    await message.answer("Байланыс үшін нөміріңізді немесе Telegram нигіңізді жазыңыз:")

@router.message(NewAdStates.waiting_for_contact)
async def contact_entered(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(NewAdStates.waiting_for_photo)
    await message.answer("Суретін жіберіңіз немесе 'суретсіз' деп жазыңыз.")


# --- ЖАҢАРТЫЛҒАН ЛОГИКА ---
@router.message(NewAdStates.waiting_for_photo)
async def photo_entered(message: Message, state: FSMContext):
    if message.photo:
        await state.update_data(photo=message.photo[-1].file_id)
    else:
        await state.update_data(photo=None)

    data = await state.get_data()
    user_info = await db.get_user(message.from_user.id)
    city = user_info[4]
    await state.update_data(city=city, user_id=message.from_user.id)

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
        await message.answer_photo(photo=data['photo'], caption=f"Тексеріп шығыңыз:\n\n{ad_text}\n\nБәрі дұрыс па?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Иә, дұрыс", callback_data="confirm_ad_yes")],[InlineKeyboardButton(text="❌ Жоқ, бас тарту", callback_data="confirm_ad_no")]]))
    else:
        await message.answer(f"Тексеріп шығыңыз:\n\n{ad_text}\n\nБәрі дұрыс па?", reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✅ Иә, дұрыс", callback_data="confirm_ad_yes")],[InlineKeyboardButton(text="❌ Жоқ, бас тарту", callback_data="confirm_ad_no")]]))

@router.callback_query(NewAdStates.waiting_for_confirmation, F.data == "confirm_ad_yes")
async def ad_confirmed(callback: CallbackQuery, state: FSMContext):
    await state.set_state(NewAdStates.waiting_for_top_choice)
    await callback.message.edit_text(
        "Хабарландыруыңызды жоғарыға шығарып, көбірек адамға көрсеткіңіз келе ме?",
        reply_markup=get_top_options_kb()
    )
    await callback.answer()

@router.callback_query(NewAdStates.waiting_for_confirmation, F.data == "confirm_ad_no")
async def ad_cancelled(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Хабарландыру жарияланбады.")
    await callback.answer()

@router.callback_query(NewAdStates.waiting_for_top_choice, F.data.startswith("top_"))
async def top_choice_handler(callback: CallbackQuery, state: FSMContext):
    choice = callback.data.split("_")[1]
    data = await state.get_data()
    
    # Хабарландыруды базаға қосу
    ad_id = await db.add_ad_to_db(data)
    
    if choice == "0":
        await callback.message.edit_text("✅ Сіздің хабарландыруыңыз сәтті жарияланды!")
    else:
        days = int(choice)
        # --- ТӨЛЕМ ЖҮЙЕСІН ҚОСАТЫН ЖЕР ---
        # Осы жерде сіз Payme, YooKassa, т.б. төлем жүйесіне сілтеме жасайсыз.
        # Төлем сәтті өткеннен кейін ғана ТОП статус беріледі.
        # Қазір біз төлемді сәтті өтті деп симуляция жасаймыз.
        await db.set_ad_top(ad_id, days)
        await callback.message.edit_text(f"✅ Хабарландыру жарияланды және {days} күнге ТОП статусын алды!")
        # --- ТӨЛЕМ ЛОГИКАСЫНЫҢ СОҢЫ ---

    await state.clear()
    await callback.answer()