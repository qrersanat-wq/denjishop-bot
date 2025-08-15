from aiogram.fsm.state import StatesGroup, State

class OrderFSM(StatesGroup):
    waiting_product = State()
    waiting_game_id = State()
    waiting_server  = State()
