# handlers/admin.py
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# Твой Telegram ID
ADMIN_ID = 6784042593

# Главная админ-панель
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет доступа к админ-панели")
        return

    await message.answer(
        "Добро пожаловать в админ-панель!\n"
        "Команды:\n"
        "/orders - посмотреть все заказы\n"
        "/balance - проверить баланс"
    )

# Просмотр всех заказов (пока заглушка)
@router.message(Command("orders"))
async def view_orders(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет доступа к этой команде")
        return
    await message.answer("Здесь будет список всех заказов (пока заглушка)")

# Проверка баланса (заглушка)
@router.message(Command("balance"))
async def check_balance(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("У тебя нет доступа к этой команде")
        return
    await message.answer("Текущий баланс: 0")
