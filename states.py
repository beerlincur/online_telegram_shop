from aiogram.dispatcher.filters.state import StatesGroup, State

class OrderForm(StatesGroup):
    name = State()
    shipping = State()
    address = State()
    phone_number = State()
    mail = State()
    nickname = State()

class Mailing(StatesGroup):
    text = State()