from aiogram.fsm.state import State, StatesGroup

class NewAdStates(StatesGroup):
    """Жаңа хабарландыру құру процесінің күйлері."""
    waiting_for_category = State()
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_price = State()
    waiting_for_contact = State()
    waiting_for_photo = State()
    waiting_for_confirmation = State()